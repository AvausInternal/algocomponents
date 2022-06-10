from unittest import TestCase

from algocomponents.adapters import LocalSqliteAdapter


class TestAdapterFindTableNames(TestCase):

    local_sqlite_adapter = LocalSqliteAdapter()

    simple_query = """CREATE TABLE tmp"""
    simple_query_with_backticks = """CREATE TABLE `tmp`"""
    simple_query_formatted = """CREATE TABLE tmp"""

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
    advanced_query_with_backticks = """
        CREATE TABLE `other_client_db.customer_product_sales_table` AS
        SELECT
            a.customer_id,
            a.product_id,
            b.sales
        FROM `client_db.customer_product_table` a
        INNER JOIN `client_db.sales_table` b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
    """
    advanced_query_formatted = """
        CREATE TABLE other_client_db_customer_product_sales_table AS
        SELECT
            a.customer_id,
            a.product_id,
            b.sales
        FROM client_db_customer_product_table a
        INNER JOIN client_db_sales_table b
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
    advanced_query_with_cte_and_backticks = """
        CREATE TABLE `other_client_db.customer_product_sales_table` AS
        WITH avg AS (
            SELECT
                AVG(sales) AS sales
            FROM `client_db.sales_table`
        )
        SELECT
            a.customer_id,
            a.product_id,
            b.sales,
            b.sales / avg.sales AS avg_weighted_sales
        FROM `client_db.customer_product_table` a
        INNER JOIN `client_db.sales_table` b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
        CROSS JOIN avg
    """
    advanced_query_with_cte_formatted = """
        CREATE TABLE other_client_db_customer_product_sales_table AS
        WITH avg AS (
            SELECT
                AVG(sales) AS sales
            FROM client_db_sales_table
        )
        SELECT
            a.customer_id,
            a.product_id,
            b.sales,
            b.sales / avg.sales AS avg_weighted_sales
        FROM client_db_customer_product_table a
        INNER JOIN client_db_sales_table b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
        CROSS JOIN avg
    """

    def test_formatting_simple_query(self):
        query = self.local_sqlite_adapter.format_table_names(query=self.simple_query)
        assert(query == self.simple_query_formatted)

    def test_formatting_simple_query_with_backticks(self):
        query = self.local_sqlite_adapter.format_table_names(query=self.simple_query_with_backticks)
        assert (query == self.simple_query_formatted)

    def test_formatting_advanced_query(self):
        query = self.local_sqlite_adapter.format_table_names(query=self.advanced_query)
        assert (query == self.advanced_query_formatted)

    def test_formatting_advanced_query_with_backticks(self):
        query = self.local_sqlite_adapter.format_table_names(query=self.advanced_query_with_backticks)
        assert (query == self.advanced_query_formatted)

    def test_formatting_advanced_query_with_cte(self):
        query = self.local_sqlite_adapter.format_table_names(query=self.advanced_query_with_cte)
        assert (query == self.advanced_query_with_cte_formatted)

    def test_formatting_advanced_query_with_cte_and_backticks(self):
        query = self.local_sqlite_adapter.format_table_names(query=self.advanced_query_with_cte_and_backticks)
        assert (query == self.advanced_query_with_cte_formatted)
