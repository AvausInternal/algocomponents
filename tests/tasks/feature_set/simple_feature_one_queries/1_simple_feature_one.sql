DROP TABLE IF EXISTS {OUTPUT_TABLE};

CREATE TABLE {OUTPUT_TABLE} AS
SELECT
    user_id,
    COUNT(product_id) AS n_products_bought,
    COUNT(DISTINCT product_id) AS n_distinct_products_bought
FROM {INPUT_TABLE}
GROUP BY user_id
;