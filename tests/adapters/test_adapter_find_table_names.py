import random
from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter, GCPAdapter


class TestAdapterFindTableNames(TestCase):

    sql_adapter = LocalSqliteAdapter()
    gcp_adapter = GCPAdapter()

    simple_query = """CREATE TABLE tmp"""

    advanced_query = """
        CREATE TABLE other_client_db.customer_product_sales_table AS
        SELECT
            a.customer_id,
            a.product_id,
            b.sales
        FROM client_db.customer_product_table a
        INNER JOIN client_db.sales_table b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
    """

    advanced_query_with_gcp_project = """
        CREATE TABLE gcp-project.other_client_db.customer_product_sales_table AS
        SELECT
            a.customer_id,
            a.product_id,
            b.sales
        FROM gcp-project.client_db.customer_product_table a
        INNER JOIN gcp-project.client_db.sales_table b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
    """

    advanced_query_with_cte = """
        CREATE TABLE other_client_db.customer_product_sales_table AS
        WITH avg AS (
            SELECT
                AVG(sales) AS sales
            FROM client_db.sales_table
        )
        SELECT
            a.customer_id,
            a.product_id,
            b.sales,
            b.sales / avg.sales AS avg_weighted_sales
        FROM client_db.customer_product_table a
        INNER JOIN client_db.sales_table b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
        CROSS JOIN avg
    """

    query_with_gcp_extract_method = """
        CREATE TABLE other_client_db.customer_product_sales_table AS
        SELECT
            a.customer_id,
            EXTRACT(ISOWEEK FROM start_at) as iso_week
        FROM client_db.sales_table a
    """

    drop_table_statement = """
        DROP TABLE client_db.customer_product_table
    """

    drop_table_statement_with_if = """
        DROP TABLE IF EXISTS client_db.customer_product_table
    """

    create_table_statement_with_if = """
        CREATE TABLE IF NOT EXISTS client_db.customer_product_table
    """

    query_with_table_in_comments = """
        -- DROP TABLE IF EXISTS client_db.customer_table
        DROP TABLE IF EXISTS client_db.customer_product_table
    """

    simple_tables = ["tmp"]
    drop_tables = ["client_db.customer_product_table"]
    advanced_tables = [
        "client_db.customer_product_table",
        "client_db.sales_table",
        "other_client_db.customer_product_sales_table",
    ]
    advanced_tables_with_gcp_project = [
        "gcp-project.client_db.customer_product_table",
        "gcp-project.client_db.sales_table",
        "gcp-project.other_client_db.customer_product_sales_table",
    ]
    query_with_gcp_extract_tables = [
        "client_db.sales_table",
        "other_client_db.customer_product_sales_table",
        # Notably, "start_at" should not be a table even though it trails FROM
    ]

    def test_finding_single_table(self):
        table_names = self.sql_adapter.find_table_names(sql=self.simple_query)
        assert table_names == self.simple_tables

    def test_finding_single_table_bad_formatting(self):
        simple_query_poor_formatting = self.sql_query_format_scrambler(
            self.simple_query
        )
        table_names = self.sql_adapter.find_table_names(
            sql=simple_query_poor_formatting
        )

        # Lowercase necessary as query formatting is scrambled
        table_names = [t.lower() for t in table_names]

        assert table_names == self.simple_tables

    def test_finding_tables_without_finding_parameters_in_gcp_method(self):
        table_names = self.gcp_adapter.find_table_names(
            sql=self.query_with_gcp_extract_method
        )

        assert sorted(table_names) == self.query_with_gcp_extract_tables

    def test_finding_tables_without_finding_parameters_in_gcp_method_bad_formatting(
        self,
    ):
        query_with_gcp_extract_method_bad_formatting = self.sql_query_format_scrambler(
            self.query_with_gcp_extract_method
        )

        table_names = self.gcp_adapter.find_table_names(
            sql=query_with_gcp_extract_method_bad_formatting
        )

        # Lowercase necessary as query formatting is scrambled
        table_names = [t.lower() for t in table_names]

        # Check that every table is found
        assert all([t in table_names for t in self.query_with_gcp_extract_tables])
        # Check that only expected tables are found
        assert all([t in self.query_with_gcp_extract_tables for t in table_names])

    def test_finding_multiple_tables(self):
        table_names = self.sql_adapter.find_table_names(sql=self.advanced_query)

        assert sorted(table_names) == self.advanced_tables

    def test_finding_multiple_tables_bad_formatting(self):
        advanced_query_poor_formatting = self.sql_query_format_scrambler(
            self.advanced_query
        )
        table_names = self.sql_adapter.find_table_names(
            sql=advanced_query_poor_formatting
        )

        # Lowercase necessary as query formatting is scrambled
        table_names = [t.lower() for t in table_names]

        # With scrambled formatting, a table may appear more than once but with
        # different casing. This is desired behaviour, as both versions of the
        # casing need to be found. However, this means the lists may not be
        # identical, so instead it is verified that every table that should be
        # found exists at least once in the returned table names.
        assert [t in table_names for t in self.advanced_tables]

    def test_finding_multiple_tables_with_gcp_project(self):
        table_names = self.sql_adapter.find_table_names(
            sql=self.advanced_query_with_gcp_project
        )

        assert sorted(table_names) == self.advanced_tables_with_gcp_project

    def test_finding_multiple_tables_with_gcp_project_bad_formatting(self):
        advanced_query_with_gcp_project_poor_formatting = (
            self.sql_query_format_scrambler(self.advanced_query_with_gcp_project)
        )
        table_names = self.sql_adapter.find_table_names(
            sql=advanced_query_with_gcp_project_poor_formatting
        )

        # Lowercase necessary as query formatting is scrambled
        table_names = [t.lower() for t in table_names]

        # With scrambled formatting, a table may appear more than once but with
        # different casing. This is desired behaviour, as both versions of the
        # casing need to be found. However, this means the lists may not be
        # identical, so instead it is verified that every table that should be
        # found exists at least once in the returned table names.
        assert [t.lower() in table_names for t in self.advanced_tables]

    def test_finding_multiple_tables_with_cte(self):
        table_names = self.sql_adapter.find_table_names(
            sql=self.advanced_query_with_cte
        )

        assert sorted(table_names) == self.advanced_tables

    def test_finding_multiple_tables_with_cte_bad_formatting(self):
        advanced_query_with_cte_poor_formatting = self.sql_query_format_scrambler(
            self.advanced_query_with_cte
        )
        table_names = self.sql_adapter.find_table_names(
            sql=advanced_query_with_cte_poor_formatting
        )

        # Lowercase necessary as query formatting is scrambled
        table_names = [t.lower() for t in table_names]

        # With scrambled formatting, a table may appear more than once but with
        # different casing. This is desired behaviour, as both versions of the
        # casing need to be found. However, this means the lists may not be
        # identical, so instead it is verified that every table that should be
        # found exists at least once in the returned table names.
        assert [t.lower() in table_names for t in self.advanced_tables]

    def test_finding_tables_in_drop_statement(self):
        table_names = self.sql_adapter.find_table_names(sql=self.drop_table_statement)
        assert table_names == ["client_db.customer_product_table"]

    def test_finding_tables_in_drop_statement_with_if(self):
        table_names = self.sql_adapter.find_table_names(
            sql=self.drop_table_statement_with_if
        )
        assert table_names == ["client_db.customer_product_table"]

    def test_finding_tables_in_create_statement_with_if(self):
        table_names = self.sql_adapter.find_table_names(
            sql=self.create_table_statement_with_if
        )
        assert table_names == ["client_db.customer_product_table"]

    def test_finding_tables_in_commented_query(self):
        table_names = self.sql_adapter.find_table_names(
            sql=self.query_with_table_in_comments
        )
        assert table_names == ["client_db.customer_product_table"]

    @staticmethod
    def sql_query_format_scrambler(string):
        # Add/remove newlines randomly
        string = string.replace("\n", "\n" * random.randint(0, 1))
        string = string.replace(" ", "\n" if random.randint(0, 10) > 1 else " ")

        # Make amount of whitespace random
        string = string.replace(" ", " " * random.randint(1, 3))

        # Randomize casing
        string = "".join(random.choice((str.upper, str.lower))(s) for s in string)

        return string
