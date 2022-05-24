import random
from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter


class TestAdapterFindTableNames(TestCase):

    sql_adapter = LocalSqliteAdapter()

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

    def test_finding_single_table(self):
        table_names = self.sql_adapter.find_table_names(sql=self.simple_query)
        self.assertEqual(table_names, ["tmp"])

    def test_finding_single_table_bad_formatting(self):
        simple_query_poor_formatting = self.sql_query_format_scrambler(self.simple_query)
        table_names = self.sql_adapter.find_table_names(
            sql=simple_query_poor_formatting
        )
        map(str.lower, table_names)

        assert(table_names == ["tmp"])

    def test_finding_multiple_tables(self):
        table_names = self.sql_adapter.find_table_names(sql=self.advanced_query)
        map(str.lower, table_names)

        assert(sorted(table_names) == [
            "client_db.customer_product_table",
            "client_db.sales_table",
            "other_client_db.customer_product_sales_table",
        ])

    def test_finding_multiple_tables_bad_formatting(self):
        advanced_query_poor_formatting = self.sql_query_format_scrambler(self.advanced_query)
        table_names = self.sql_adapter.find_table_names(sql=advanced_query_poor_formatting)
        map(str.lower, table_names)

        assert(sorted(table_names) == [
            "client_db.customer_product_table",
            "client_db.sales_table",
            "other_client_db.customer_product_sales_table",
        ])

    def test_finding_multiple_tables_with_gcp_project(self):
        table_names = self.sql_adapter.find_table_names(sql=self.advanced_query_with_gcp_project)
        map(str.lower, table_names)

        assert(sorted(table_names) == [
            "gcp-project.client_db.customer_product_table",
            "gcp-project.client_db.sales_table",
            "gcp-project.other_client_db.customer_product_sales_table",
        ])

    def test_finding_multiple_tables_with_gcp_project_bad_formatting(self):
        advanced_query_with_gcp_project_poor_formatting = self.sql_query_format_scrambler(self.advanced_query_with_gcp_project)
        table_names = self.sql_adapter.find_table_names(sql=advanced_query_with_gcp_project_poor_formatting)
        map(str.lower, table_names)

        assert(sorted(table_names) == [
            "gcp-project.client_db.customer_product_table",
            "gcp-project.client_db.sales_table",
            "gcp-project.other_client_db.customer_product_sales_table",
        ])

    def test_finding_multiple_tables_with_cte(self):
        table_names = self.sql_adapter.find_table_names(sql=self.advanced_query_with_cte)
        map(str.lower, table_names)

        assert(sorted(table_names) == [
            "client_db.customer_product_table",
            "client_db.sales_table",
            "other_client_db.customer_product_sales_table",
        ])

    def test_finding_multiple_tables_with_cte_bad_formatting(self):
        advanced_query_with_cte_poor_formatting = self.sql_query_format_scrambler(self.advanced_query_with_cte)
        table_names = self.sql_adapter.find_table_names(sql=advanced_query_with_cte_poor_formatting)
        map(str.lower, table_names)

        assert(sorted(table_names) == [
            "client_db.customer_product_table",
            "client_db.sales_table",
            "other_client_db.customer_product_sales_table",
        ])

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
