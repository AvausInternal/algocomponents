from configparser import ConfigParser
from unittest import TestCase
import os
import sys

# This is required for github actions to find the algocomponents imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from algocomponents.adapters import GCPAdapter


class TestAdapterFindTableNames(TestCase):

    gcp_project = "avaus-academy"
    config = ConfigParser()
    config.set(section="DEFAULT", option="gcp_project", value=gcp_project)
    gcp_adapter = GCPAdapter(config=config)

    simple_query = """CREATE TABLE tmp"""
    simple_query_with_backticks = """CREATE TABLE `tmp`"""
    simple_query_formatted = """CREATE TABLE `avaus-academy.tmp`"""

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
    advanced_query_with_project = f"""
        CREATE TABLE {gcp_project}.other_client_db.customer_product_sales_table AS
        SELECT
            a.customer_id,
            a.product_id,
            b.sales
        FROM avaus-academy.client_db.customer_product_table a
        INNER JOIN avaus-academy.client_db.sales_table b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
    """
    advanced_query_formatted = f"""
        CREATE TABLE `{gcp_project}.other_client_db.customer_product_sales_table` AS
        SELECT
            a.customer_id,
            a.product_id,
            b.sales
        FROM `avaus-academy.client_db.customer_product_table` a
        INNER JOIN `avaus-academy.client_db.sales_table` b
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
    advanced_query_with_cte_and_project = f"""
        CREATE TABLE {gcp_project}.other_client_db.customer_product_sales_table AS
        WITH avg AS (
            SELECT
                AVG(sales) AS sales
            FROM avaus-academy.client_db.sales_table
        )
        SELECT
            a.customer_id,
            a.product_id,
            b.sales,
            b.sales / avg.sales AS avg_weighted_sales
        FROM avaus-academy.client_db.customer_product_table a
        INNER JOIN avaus-academy.client_db.sales_table b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
        CROSS JOIN avg
    """
    advanced_query_with_cte_formatted = f"""
        CREATE TABLE `{gcp_project}.other_client_db.customer_product_sales_table` AS
        WITH avg AS (
            SELECT
                AVG(sales) AS sales
            FROM `avaus-academy.client_db.sales_table`
        )
        SELECT
            a.customer_id,
            a.product_id,
            b.sales,
            b.sales / avg.sales AS avg_weighted_sales
        FROM `avaus-academy.client_db.customer_product_table` a
        INNER JOIN `avaus-academy.client_db.sales_table` b
            ON a.customer_id = b.customer_id
            AND a.product_id = b.product_id
        CROSS JOIN avg
    """

    def test_formatting_simple_query(self):
        query = self.gcp_adapter.format_table_names(query=self.simple_query)
        assert query == self.simple_query_formatted

    def test_formatting_simple_query_with_backticks(self):
        query = self.gcp_adapter.format_table_names(
            query=self.simple_query_with_backticks
        )
        assert query == self.simple_query_formatted

    def test_re_formatting_simple_query(self):
        query = self.gcp_adapter.format_table_names(query=self.simple_query_formatted)
        assert query == self.simple_query_formatted

    def test_formatting_advanced_query(self):
        query = self.gcp_adapter.format_table_names(query=self.advanced_query)
        assert query == self.advanced_query_formatted

    def test_formatting_advanced_query_with_backticks(self):
        query = self.gcp_adapter.format_table_names(
            query=self.advanced_query_with_backticks
        )
        assert query == self.advanced_query_formatted

    def test_formatting_advanced_query_with_project(self):
        query = self.gcp_adapter.format_table_names(
            query=self.advanced_query_with_project
        )
        assert query == self.advanced_query_formatted

    def test_re_formatting_advanced_query(self):
        query = self.gcp_adapter.format_table_names(query=self.advanced_query_formatted)
        assert query == self.advanced_query_formatted

    def test_formatting_advanced_query_with_cte(self):
        query = self.gcp_adapter.format_table_names(query=self.advanced_query_with_cte)
        assert query == self.advanced_query_with_cte_formatted

    def test_formatting_advanced_query_with_cte_and_backticks(self):
        query = self.gcp_adapter.format_table_names(
            query=self.advanced_query_with_cte_and_backticks
        )
        assert query == self.advanced_query_with_cte_formatted

    def test_formatting_advanced_query_with_cte_and_project(self):
        query = self.gcp_adapter.format_table_names(
            query=self.advanced_query_with_cte_and_project
        )
        assert query == self.advanced_query_with_cte_formatted

    def test_re_formatting_advanced_query_with_cte(self):
        query = self.gcp_adapter.format_table_names(
            query=self.advanced_query_with_cte_formatted
        )
        assert query == self.advanced_query_with_cte_formatted
