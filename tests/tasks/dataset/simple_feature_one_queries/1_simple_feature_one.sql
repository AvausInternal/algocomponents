DROP TABLE IF EXISTS {output_table};

CREATE TABLE {output_table} AS
SELECT
    user_id,
    COUNT(product_id) AS n_products_bought,
    COUNT(DISTINCT product_id) AS n_distinct_products_bought
FROM {input_table}
GROUP BY user_id
;