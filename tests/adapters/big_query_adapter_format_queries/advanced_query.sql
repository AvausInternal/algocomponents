CREATE TABLE other_client_db.customer_product_sales_table AS
SELECT
    a.customer_id
    , a.product_id
    , b.sales
FROM client_db.customer_product_table AS a
INNER JOIN client_db.sales_table AS b
    ON
        a.customer_id = b.customer_id
        AND a.product_id = b.product_id;
CREATE TABLE `avaus-academy.other_client_db.customer_product_sales_table` AS
SELECT
    a.customer_id
    , a.product_id
    , b.sales
FROM `avaus-academy.client_db.customer_product_table` AS a
INNER JOIN `avaus-academy.client_db.sales_table` AS b
    ON
        a.customer_id = b.customer_id
        AND a.product_id = b.product_id
