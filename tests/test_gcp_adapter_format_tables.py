from configparser import ConfigParser
from unittest import TestCase

from algocomponents.adapters import GCPAdapter


class TestGCPAdapterFormatTables(TestCase):

    gcp_project = "avaus-academy"
    config = ConfigParser()
    config.set(section="DEFAULT", option="gcp_project", value=gcp_project)
    gcp_adapter = GCPAdapter(config=config)
    gcp_adapter_without_config = GCPAdapter()

    simple_query = """CREATE TABLE tmp"""
    simple_query_with_backticks = """CREATE TABLE `tmp`"""
    simple_query_formatted = """CREATE TABLE `avaus-academy.tmp`"""
    simple_query_with_gcp_project = """CREATE TABLE `another_gcp_project.db.tmp`"""

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
    query_with_ml_methods = """
        SELECT
            *
        FROM
            ML.FEATURE_IMPORTANCE(MODEL `mydataset.mymodel`)
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
    advanced_query_with_wildcard_table = """
        WITH sessions_events as(
          SELECT
            (SELECT value.string_value FROM UNNEST(event_params) where key = "page_location") AS locations,
            (SELECT value.int_value FROM UNNEST(event_params) where key = "ga_session_id") AS ga_session_id,
            MAX(user_pseudo_id) AS user_pseudo_id,
            MAX(Case event_name when 'session_start' then event_timestamp end) session_start,
            MAX(Case event_name when 'user_engagement' then event_timestamp  end) end_visit,
            MAX(event_date) AS event_date,
            MAX((SELECT value.string_value FROM UNNEST(event_params) where key = "page_title")) AS title,
            MAX((SELECT value.string_value FROM UNNEST(event_params) where key = "page_referrer")) AS referrer, 
            MAX((SELECT value.string_value FROM UNNEST(event_params) where key = "Article tag")) AS article_tag,
          FROM `avaus-com-ga.analytics_243066661.events_*` 
          GROUP BY ga_session_id, locations
        ),
          sessions_duration as( 
          SELECT user_pseudo_id, 
          PARSE_DATE('%Y%m%d', event_date) AS event_date,
          SAFE_SUBTRACT(end_visit, session_start) as duration,
          ga_session_id,
          article_tag,
          STRUCT(title, locations, referrer) AS page
          FROM sessions_events
          order by ga_session_id
          
        )
        
          SELECT user_pseudo_id, event_date,
          duration,
          ga_session_id,
          article_tag,
          page
          FROM sessions_duration
          WHERE event_date BETWEEN '2021-08-01' AND CURRENT_DATE()
          order by event_date
    """

    def test_formatting_simple_query(self):
        query = self.gcp_adapter._format_table_names(query=self.simple_query)
        assert query == self.simple_query_formatted

    def test_formatting_simple_query_with_backticks(self):
        query = self.gcp_adapter._format_table_names(
            query=self.simple_query_with_backticks
        )
        assert query == self.simple_query_formatted

    def test_re_formatting_simple_query(self):
        query = self.gcp_adapter._format_table_names(query=self.simple_query_formatted)
        assert query == self.simple_query_formatted

    def test_formatting_query_with_ml_methods(self):
        query = self.gcp_adapter._format_table_names(query=self.query_with_ml_methods)
        assert query == self.query_with_ml_methods

    def test_formatting_simple_query_with_gcp_project(self):
        query = self.gcp_adapter._format_table_names(
            query=self.simple_query_with_gcp_project
        )
        assert query == self.simple_query_with_gcp_project

    def test_formatting_simple_query_with_missing_config(self):
        query = self.gcp_adapter_without_config._format_table_names(
            query=self.simple_query
        )
        assert query == self.simple_query_with_backticks

    def test_formatting_advanced_query(self):
        query = self.gcp_adapter._format_table_names(query=self.advanced_query)
        assert query == self.advanced_query_formatted

    def test_formatting_advanced_query_with_backticks(self):
        query = self.gcp_adapter._format_table_names(
            query=self.advanced_query_with_backticks
        )
        assert query == self.advanced_query_formatted

    def test_formatting_advanced_query_with_project(self):
        query = self.gcp_adapter._format_table_names(
            query=self.advanced_query_with_project
        )
        assert query == self.advanced_query_formatted

    def test_re_formatting_advanced_query(self):
        query = self.gcp_adapter._format_table_names(
            query=self.advanced_query_formatted
        )
        assert query == self.advanced_query_formatted

    def test_formatting_advanced_query_with_cte(self):
        query = self.gcp_adapter._format_table_names(query=self.advanced_query_with_cte)
        assert query == self.advanced_query_with_cte_formatted

    def test_formatting_advanced_query_with_cte_and_backticks(self):
        query = self.gcp_adapter._format_table_names(
            query=self.advanced_query_with_cte_and_backticks
        )
        assert query == self.advanced_query_with_cte_formatted

    def test_formatting_advanced_query_with_cte_and_project(self):
        query = self.gcp_adapter._format_table_names(
            query=self.advanced_query_with_cte_and_project
        )
        assert query == self.advanced_query_with_cte_formatted

    def test_re_formatting_advanced_query_with_cte(self):
        query = self.gcp_adapter._format_table_names(
            query=self.advanced_query_with_cte_formatted
        )
        assert query == self.advanced_query_with_cte_formatted

    def test_formatting_advanced_query_with_wildcard_table(self):
        query = self.gcp_adapter_without_config._format_table_names(
            query=self.advanced_query_with_wildcard_table
        )
        assert query == self.advanced_query_with_wildcard_table
