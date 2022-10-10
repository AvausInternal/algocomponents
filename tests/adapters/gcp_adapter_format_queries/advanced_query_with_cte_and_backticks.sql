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
;
CREATE TABLE `avaus-academy.other_client_db.customer_product_sales_table` AS
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
