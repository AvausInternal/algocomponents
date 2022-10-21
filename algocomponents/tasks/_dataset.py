"""Support for gradual typing as defined by PEP 484"""
from typing import List

from algocomponents.adapters.custom_exceptions import (
    TableMissingException,
    DataMismatchException,
)
from algocomponents.tasks import FeatureBase, GroupTask, SQLTask, Feature


class Dataset(GroupTask):
    """
    A Dataset constructs a dataset table out of an input base table and a set
    of featuresets. It does this by running all the features and followed by
    an SQL join query to create the desired output table.

    Args:
        output_table: Where the resulting table is saved
        features: list of the features that make up the dataset
        input_table: the basis on which to join feature columns
        feature_base: a featurebase can take the place of an input_table
        import_columns: either 'selective' or 'full':
            'full': output_table  will include all the columns in the input
            'selective': output_table will include the primary keys of the input
        where_clause: Injects a where-clause inside the main join query
        drop_intermediate: drop the intermediate tables created
        verify: run lightweight checks on the integrity of the operations
        target_label: assume the last column in the dataset is a target_label

    """

    def __init__(
        self,
        output_table: str,
        features: List[Feature],
        input_table: str = None,
        feature_base: FeatureBase = None,
        import_columns: str = "selective",
        where_clause: str = None,
        drop_intermediate: bool = False,
        verify: bool = True,
        target_label: bool = False,
        **kwargs,
    ):

        super().__init__(**kwargs)
        self.feature_base = feature_base
        self.input_table = input_table
        self.features = features
        self.where_clause = where_clause
        self.drop_intermediate = drop_intermediate
        self.target_label = target_label
        self.verify = verify

        if input_table is None and feature_base is None:
            raise ValueError("Provide either an input_table or feature_base")

        elif input_table is not None and feature_base is not None:
            raise ValueError("Provide either an input_table or feature_base")

        elif input_table is None:  # implies input is a featurebase
            self.task_list.insert(0, feature_base)
            self.input_table = feature_base.output_table

        elif feature_base is None:  # implies input is a an ordinary table
            self.input_table = input_table.format(**self.config[self.section])

        if import_columns.lower() in ["selective", "full"]:
            self.import_columns = import_columns.lower()
        else:
            raise ValueError(
                f"import_columns must be 'selective' or 'full', not {import_columns}"
            )
        if features is None:
            raise ValueError("Provide at least one feature in features")
        if target_label:
            raise NotImplementedError(
                "Target labels will be supported in future releases"
            )

        for feature_task in self.features:
            if isinstance(feature_task, Feature):  # refactor after renaming Feature
                self.task_list.append(feature_task)
            else:
                raise ValueError(
                    f"features must be of type Feature, not {type(feature_task)}"
                )

        # propagate config to tasks in task list
        self.propagate_config()
        self.propagate_sql_adapter(self.sql_adapter)

        # add to config without propogation to tasks in tasklist
        self.output_table = str(output_table.format(**self.config[self.section]))
        self.add_to_config("output_table", self.output_table, recursive=False)

    def primary_keys(self) -> List[str]:
        """The primary keys of the dataset output table.
        If the input is a featurebase, the primary keys are equal to
        the input's primary keys. Otherwise, the keys are the set-union
        of all the supplied feature primary keys.
        """

        if self.feature_base:
            return self.feature_base.output_primary_keys
        else:
            # infer the primary keys we know of
            primary_keys = [feat.output_primary_keys for feat in self.features]
            return list(set().union(primary_keys))

    def _format_query_cols(
        self, features: List[Feature], prepend: str, pad: str
    ) -> str:
        """Helper function for _get_sql_join_query()"""

        output_columns = []
        for feature_col in features:
            output_columns.append(f"{pad}{prepend}{feature_col},")

        return output_columns

    def _format_query_joins(self, feature: Feature, feat_no: int, pad: str) -> str:
        """Helper function for _get_sql_join_query()

        Limitations:
            - feature primary keys are always joined on a column of the same
            name in the input table.
        """
        join_table = [f"LEFT JOIN {feature.output_table} AS f{feat_no}"]
        join_condition = []

        for cnt, pkey in enumerate(feature.output_primary_keys):
            if cnt == 0:
                on_condition = f"{pad}ON base.{pkey} = f{feat_no}.{pkey}"
            else:
                on_condition = f"{pad}AND base.{pkey} = f{feat_no}.{pkey}"
            join_condition.append(on_condition)

        return join_table + join_condition

    def _get_sql_join_query(
        self, where_clause: str = None, pad_spaces: int = 2, drop_existing: bool = True
    ) -> str:
        """_summary_

        Args:
            where_clause (str, optional): The lines following a WHERE. Defaults to None
            pad_spaces (int, optional): SQL query indent spaces. Defaults to 2
            drop_existing (bool, optional): Drops existing tables. Defaults to True

        Returns:
            str: SQL-ready query
        """

        pad = pad_spaces * " "

        # build and format query components
        sql_joined_cols, sql_left_joins = [], []
        sql_create_line = ["CREATE TABLE {output_table} AS"]
        sql_select_line = ["SELECT"]
        base_cols = self._get_import_table_columns()
        sql_base_cols = self._format_query_cols(base_cols, "base.", pad)
        sql_base_table = [f"FROM {self.input_table} AS base"]

        for n, feature in enumerate(self.features):
            sql_joined_cols += self._format_query_cols(
                feature.output_columns_created, f"f{n}.", pad
            )
            sql_left_joins += self._format_query_joins(feature, n, pad)

        # remove the last comma in query columns
        if len(sql_joined_cols) > 0:
            sql_joined_cols[-1] = sql_joined_cols[-1][:-1]

        sql_full_query = [
            sql_create_line,
            sql_select_line,
            sql_base_cols,
            sql_joined_cols,
            sql_base_table,
            sql_left_joins,
        ]

        if drop_existing:
            sql_full_query.insert(0, ["DROP TABLE IF EXISTS {output_table};"])

        if where_clause:
            sql_full_query.append([f"WHERE\n{pad}{self.where_clause}"])

        final_query = "".join(["\n".join(i) + "\n" for i in sql_full_query])

        return final_query

    def _get_sql_drop_query(self, table_names: List[str]) -> str:
        """given a list of table_names, generate the sql to drop all the tables

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
        """Returns a list of the input table column names. Depending on self.import_columns,
        will return either: the entire list of columns, or the primary keys of the table.

        Returns:
            List[str]: Input column names
        """

        if self.import_columns == "selective":
            return self.primary_keys()

        # get all the available columns
        elif self.import_columns == "full":
            if self.feature_base:
                cols = (
                    self.feature_base.output_primary_keys
                    + self.feature_base.output_columns_created
                )
                return list(set().union(cols))
            else:
                self.sql_adapter.connect()  # might not be necessary
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
        """
        If verify is true, run startup tasks that verify the integrity of the opterations.
        """
        super().startup()

        # verify required columns are a subset of the input table columns
        if self.verify:
            if self.sql_adapter is None:
                raise ValueError("sql_adapter must be provided if verify is true")

            self.sql_adapter.connect()
            input_table_columns = set(
                self.sql_adapter.get_table_columns(self.input_table)
            )
            required_columns = set(self._get_import_table_columns())

            if not set(required_columns).issubset(input_table_columns):
                raise DataMismatchException(
                    f"Input table does not contain the necessary columns\n"
                    f"Input table {self.input_table}\n is missing:"
                    f"{required_columns.difference(input_table_columns)}\n"
                )

    def run(self):
        """
        Appends necessary SQL tasks to the task list before running
        """
        if self.features:
            join_tables_task = SQLTask(
                sql_adapter=self.sql_adapter,
                sql_string=self._get_sql_join_query(where_clause=self.where_clause),
                config=self.config,
            )
            self.task_list.append(join_tables_task)

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
        """
        run shutdown tasks, such as verifying the integrity of the opterations done
        """
        if self.verify:
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

            # check dataset leaves no. of rows unchanged:
            input_table_rows = self.sql_adapter.count_rows_in_table(self.input_table)
            output_table_row = self.sql_adapter.count_rows_in_table(self.output_table)
            if input_table_rows != output_table_row:
                raise DataMismatchException(
                    f"Dataset run operation resulted in a change in rows\n"
                    f"Input table has {input_table_rows} rows\n"
                    f"Output table has {output_table_row} rows\n"
                )

            # check intermediary tables are dropped
            if self.drop_intermediate:
                for table in self._get_intermediate_table_names():
                    if self.sql_adapter.table_exists(table):
                        raise DataMismatchException(
                            f"Drop intermidate tables failed, table {table} exists \n"
                        )
