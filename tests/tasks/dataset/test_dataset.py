import os

import pytest

from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import Dataset, Feature, FeatureBase, SQLPipeline, SQLTask
from algocomponents.adapters.custom_exceptions import DataMismatchException


# Define class here so finding sql folder is easier
class SimpleFeatureBase(FeatureBase):
    output_primary_keys = [
        "user_id",
        "product_id",
    ]
    output_columns_created = []


# Define class here so finding sql folder is easier
class SimpleFeatureOne(Feature):
    """An example feature that uses the featurebase as an input to
    generate two features on the user level.
    """

    input_columns = [
        "user_id",
        "product_id",
    ]
    output_primary_keys = [
        "user_id",
    ]
    output_columns_created = [
        "n_products_bought",
        "n_distinct_products_bought",
    ]


class SimpleFeatureTwo(Feature):
    """A example feature that uses a prexisting table as input to
    add features on the product level.
    """

    input_columns = [
        "product_id",
        "product_price",
        "product_weight",
    ]
    output_primary_keys = [
        "product_id",
    ]
    output_columns_created = [
        "price_per_kg",
        "product_price",
        "product_weight",
    ]


class IncorrectPrimaryKeyFeature(Feature):
    """A simple feature with the primary keys that intentionally
    do not exist elsewhere, for testing purposes."""

    input_columns = ["incorrectly_named_product_id"]
    output_primary_keys = [
        "incorrectly_named_product_id",
    ]
    output_columns_created = []


# changing scope to 'function' fixtures will run for each methodcall seperately.
@pytest.fixture(scope="class", name="prepared_table")
def prepare_existing_table():
    """
    todo:
        - remove assert?
        - yield the whole pipeline or just the name?
    """

    # setup:
    sql_adapter = LocalSqliteAdapter()
    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    dir_path = os.path.join("tests", "tasks", "dataset", "preparation_queries")

    pipeline = SQLPipeline(
        global_config_dir=global_config_path,
        sql_folder=dir_path,
        sql_folder_relative_path=False,
        sql_adapter=sql_adapter,
    )
    pipeline.start()

    # config variable sets the output table name
    table_name = pipeline.config[pipeline.section]["pre_existing_table"]
    formatted_table_name = table_name.format(**pipeline.config[pipeline.section])

    yield formatted_table_name

    # teardown:
    sql_adapter.connect()
    SQLTask(
        sql_string=f"DROP TABLE IF EXISTS {formatted_table_name};",
        sql_adapter=sql_adapter,
    ).start()
    assert sql_adapter.table_exists(formatted_table_name) is False


@pytest.mark.usefixtures("prepared_table")
class TestDatasetOutcomes:
    """A range of tests focusing on the output of the dataset

    #todo:
        - test if it runs with and without verify
        - full or selective
        - put featurebases in this class as input (safer)
        - [ ] Verify = True, drop_intermediate=True, featurebase:
        results in dropping the input table before the shutdown verify tasks can be run


    """

    # globals
    sql_adapter = LocalSqliteAdapter()
    global_config_path = os.path.join("tests", "tasks", "dataset", "dataset_config")
    work_dir_path = os.path.join("tests", "tasks", "dataset")
    pre_existing_table = (
        "{tmp_db}.pre_existing_table"  # For clarity, but exists also in config
    )
    base_output_table = (
        "{tmp_db}.feature_base_table"  # For clarity, but exists also in config
    )

    # instantiate a simple feature
    feature_one = SimpleFeatureOne(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_one_queries",
        input_table=base_output_table,
        output_table="{tmp_db}.feature_one_output",
    )

    # instantiate a simple feature
    feature_two = SimpleFeatureTwo(
        global_config_dir=global_config_path,
        sql_folder="simple_feature_two_queries",
        input_table=pre_existing_table,
        output_table="{tmp_db}.feature_two_output",
    )

    # instantiate feature with duplicate primary keys
    explosive_feature = SimpleFeatureOne(
        global_config_dir=global_config_path,
        sql_folder="explosive_feature_queries",
        input_table=base_output_table,
        output_table="{tmp_db}.feature_one_output",
    )

    feature_base = SimpleFeatureBase(
        global_config_dir=global_config_path,
        sql_folder=os.path.join("make_feature_base_queries"),
        sql_adapter=sql_adapter,  # needed if run seperately from Dataset
        output_table=base_output_table,
    )

    def test_prexisting_tables_exist(self, prepared_table):
        """test if the fixture has successfully prepared the tables assumed to be prexisting
        in the coming tests.

        by accepting the fixture name as argument we can interact with the yielded object, which is
        in this the formatted name of table it created for us.
        """
        self.sql_adapter.connect()
        assert self.sql_adapter.table_exists(prepared_table)
        assert self.sql_adapter.count_rows_in_table(prepared_table) > 0
        assert set(self.sql_adapter.get_table_columns(prepared_table)) == set(
            ["product_id", "product_price", "product_weight"]
        )

    def test_changed_rowcount(self):
        # total rows must remain unchanged between input and output
        # this will only throw DataMismatchException if verify is true.

        with pytest.raises(DataMismatchException):
            dataset = Dataset(
                output_table="{tmp_db}.test_output",
                features=[self.explosive_feature],
                # input_table=base_output_table,
                input_table="{tmp_db}.feature_base_table",
                feature_base=None,  # feature_base,
                import_columns="full",
                where_clause=None,
                drop_intermediate=False,
                target_label=False,
                global_config_dir=self.global_config_path,
                sql_adapter=self.sql_adapter,
                verify=True,
            )
            dataset.start()

    def test_unchanged_columns(self):
        """repeating feature_one will result in spurious columns
        which should throw an exception
        """

        with pytest.raises(DataMismatchException):
            self.feature_base.start()  # ensure output exists
            dataset = Dataset(
                output_table="{tmp_db}.test_output",
                features=[self.feature_one, self.feature_one],
                input_table="{tmp_db}.feature_base_table",
                feature_base=None,
                import_columns="full",
                global_config_dir=self.global_config_path,
                sql_adapter=self.sql_adapter,
                verify=True,
            )
            dataset.start()

    def test_drop_intermediate_tables(self):
        # delete intermidate tables that features create if drop_intermediate

        dataset = Dataset(
            output_table="{tmp_db}.test_output",
            features=[
                self.feature_one,
                self.feature_two,
            ],
            input_table="{tmp_db}.feature_base_table",
            drop_intermediate=False,  # vital to test
            global_config_dir=self.global_config_path,
            sql_adapter=self.sql_adapter,
        )
        dataset.start()
        dataset.sql_adapter.connect()

        # Tables exist after a normal run
        intermediate_tables = dataset._get_intermediate_table_names()
        for table in intermediate_tables:
            assert dataset.sql_adapter.table_exists(table)

        # Tables deleted
        dataset.drop_intermediate = True
        dataset.start()
        dataset.sql_adapter.connect()
        for table in intermediate_tables:
            assert not dataset.sql_adapter.table_exists(table)

    def test_selective_full(self):
        """r"""

        dataset = Dataset(
            output_table="{tmp_db}.test_output",
            features=[self.feature_one, self.feature_two],
            feature_base=self.feature_base,
            # input_table="{tmp_db}.feature_base_table",
            import_columns="selective",
            global_config_dir=self.global_config_path,
            sql_adapter=self.sql_adapter,
            drop_intermediate=False,
            verify=True,
        )
        dataset.start()
        dataset.sql_adapter.connect()
        formatted_name = "{tmp_db}.test_output".format(
            **dataset.config[dataset.section]
        )
        # todo: print to see change in output columns first
