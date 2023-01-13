from typing import List

from algocomponents.adapters import SQLAdapter
from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import FeatureBase, GroupTask, SQLTask


class FeatureSet(GroupTask):
    """_summary_
    will propogate adapter and config to child tasks.
    #todo:
    - consider what can be lifted out of the class to utils
    - naming conventions
    - What ought to be a private function?
    - what should be a function? encapsulate logic(Seperation of concerns)

    Args:
        GroupTask (_type_): _description_
    """

    def __init__(
        self,
        output_table: str,
        features: list,
        input_table: str = None,
        feature_base: FeatureBase = None,
        import_columns: str = "selective",
        where_clause: str = None,  #
        drop_intermediate: bool = False,  # todo: implement
        target_label: bool = False,  # todo: implement
        **kwargs,
    ):

        super().__init__(**kwargs)
        self.feature_base = feature_base
        self.input_table = input_table
        self.features = features
        self.where_clause = where_clause
        self.drop_intermediate = drop_intermediate
        self.target_label = target_label

        if input_table is None and feature_base is None:
            raise ValueError("Provide either an input_table or feature_base")

        elif input_table is not None and feature_base is not None:
            raise ValueError("Provide either an input_table or feature_base, not both")

        elif input_table is None:  # input is a featurebase
            self.task_list.insert(0, feature_base)
            self.input_table = feature_base.output_table

        elif feature_base is None:  # input is a an ordinary table
            self.input_table = input_table

        if import_columns.lower() in ["selective", "full"]:
            self.import_columns = import_columns.lower()
        else:
            raise ValueError(
                f"import_columns must be 'selective' or 'full', not {import_columns}"
            )

        # todo: replace with a shallow add_to_config() call here?
        self.output_table = output_table.format(**self.config[self.section])
        self.config[self.section]["OUTPUT_TABLE"] = str(self.output_table)

        for feature_task in self.features:
            self.task_list.append(feature_task)

        # propagate to children
        self.propagate_config()
        self.propagate_sql_adapter(self.sql_adapter)

    def _format_query_cols(self, feature_list, prepend, pad) -> str:
        """Helper function for _get_sql_join_query()
        #* lift to util?"""
        output_columns = []

        for feature_col in feature_list:
            output_columns.append(f"{pad}{prepend}{feature_col},")

        return output_columns

    def _format_query_joins(self, feature, feat_no, pad) -> str:
        """Helper function for _get_sql_join_query()"""
        join_table = [f"LEFT JOIN {feature.output_table} AS f{feat_no}"]
        join_condition = []

        for cnt, pkey in enumerate(feature.output_primary_keys):
            if cnt == 0:
                on_condition = f"{pad}ON base.{pkey} = f{feat_no}.{pkey}"
            else:
                on_condition = f"{pad}AND base.{pkey} = f{feat_no}.{pkey}"
            join_condition.append(on_condition)

        return join_table + join_condition

    def output_primary_keys(self) -> List[str]:
        """The primary keys of the dataset output table.
        If the input is a featurebase, the primary keys are equal to
        the input's primary keys. Otherwise, the keys are the set-union
        of all feature's primary keys.
        """

        if self.feature_base:
            return self.feature_base.output_primary_keys
        else:
            # infer the primary keys we know of
            output_primary_keys = [feat.output_primary_keys for feat in self.features]
            return list(set().union(output_primary_keys))

    def _get_sql_join_query(self, pad_spaces=2) -> str:
        """Here we construct the full join script with helper functions"""
        # todo: what happens if no features? Raise error in init?
        # todo: raise error if nothing to join on, only base columns survive.
        # todo: catch multiple primary keys

        pad = pad_spaces * " "

        # build query components
        sql_joined_cols, sql_left_joins = [], []
        # ? do we drop existing output tables?
        sql_drop_line = ["DROP TABLE IF EXISTS {OUTPUT_TABLE};"]
        sql_create_line = ["CREATE TABLE {OUTPUT_TABLE} AS"]
        sql_select_line = ["SELECT"]
        base_cols = self._get_import_table_columns()
        sql_base_cols = self._format_query_cols(base_cols, "base.", pad)
        sql_base_table = [f"FROM {self.input_table} AS base"]

        for n, feature in enumerate(self.features):
            sql_joined_cols += self._format_query_cols(
                feature.output_columns_created, f"f{n}.", pad
            )
            sql_left_joins += self._format_query_joins(feature, n, pad)

        sql_joined_cols[-1] = sql_joined_cols[-1][:-1]  # remove the last comma

        sql_full_query = [
            sql_drop_line,  # ? create or replace this table?
            sql_create_line,
            sql_select_line,
            sql_base_cols,
            sql_joined_cols,
            sql_base_table,
            sql_left_joins,
        ]

        if self.where_clause:
            sql_full_query.append([f"WHERE\n{pad}{self.where_clause}"])

        final_query = "".join(["\n".join(i) + "\n" for i in sql_full_query])

        return final_query

    def _get_sql_drop_query(self, table_names: list) -> str:
        """given a list of table names, generate the sql to drop all the tables
        #* NOTE: this can be lifted to utils class. Useful outside this scope.

        Args:
            table_names (list): list of table names to drop

        Returns:
            str: SQL ready string
        """
        query = []
        for table in table_names:
            query.append(f"DROP TABLE IF EXISTS {table}")

        return "".join([i + ";\n" for i in query])

    def _get_import_table_columns(self) -> List[str]:
        """gets the input base table columns depending
        if self.import_columns is 'full' or 'selective'
        """
        if self.import_columns == "selective":
            # get only the primary keys
            return self.output_primary_keys()

        elif self.import_columns == "full":
            # get all the available columns
            if self.feature_base:
                cols = (
                    self.feature_base.output_primary_keys
                    + self.feature_base.output_columns_created
                )
                return list(set().union(cols))
            else:
                self.sql_adapter.connect()  # ? might be unnecessary
                return self.sql_adapter.get_table_columns(self.input_table)

    def _get_all_dataset_columns(self) -> List[str]:
        """Get all the columns of the final dataset this class creates

        Returns:
            List[str]: all the dataset columns created
        """
        output_columns = self._get_import_table_columns()
        for feature in self.features:
            output_columns += feature.output_columns_created
        return output_columns

    def _get_intermediate_table_names(self) -> List[str]:
        """Helper function for _get_sql_drop_query"""
        tables = []
        for feat in self.features:
            tables.append(feat.output_table)

        if self.feature_base:
            tables.append(self.feature_base.output_table)

        return tables

    def startup(self):
        # todo:
        # check legality of joins
        # make lists and loops?
        pass        

    def run(self):
        """
        todo: update docstring
        (..) and then verifies the output table.
        It is verified that the output table exists, and that it contains the
        intended columns

        """
        if self.features:
            join_tables_task = SQLTask(
                sql_adapter=self.sql_adapter,
                sql_string=self._get_sql_join_query(),
                config=self.config,
            )
            self.task_list.append(join_tables_task)

        # ? should this be here or in init?
        if self.drop_intermediate:
            drop_tables_task = SQLTask(
                sql_adapter=self.sql_adapter,
                sql_string=self._get_sql_drop_query(
                    self._get_intermediate_table_names()
                ),
            )
            self.task_list.append(drop_tables_task)

        super().run()

    def shutdown(self):
        """clean up after run
        #* some can be lifted to utils
        # todo:
        # check if rows are unchanged:
        # check that tables are dropped?

        Raises:
            TableMissingException: _description_
            DataMismatchException: _description_
        """
        # check for existance of output table
        if not self.sql_adapter.table_exists(self.output_table):
            raise TableMissingException(
                f"Output table has not been created: {self.output_table}"
            )

        generated_columns = self._get_all_dataset_columns()
        actual_columns = self.sql_adapter.get_table_columns(self.output_table)

        # check that output table has the right columns
        if not sorted(generated_columns) == sorted(actual_columns):
            raise DataMismatchException(
                f"Output table does not contain columns specified.\n"
                f"Output table: {self.output_table}\n"
                f"Has columns: {actual_columns}\n"
                f"but should contain columns: {generated_columns}\n"
            )
