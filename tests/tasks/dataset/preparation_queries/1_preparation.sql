DROP TABLE IF EXISTS {pre_existing_table};

CREATE TABLE {pre_existing_table} AS
SELECT
    1 AS product_id
    , 10 AS product_price
    , 3 AS product_weight
UNION ALL SELECT
    2 AS product_id
    , 15 AS product_price
    , 5 AS product_weight
UNION ALL SELECT
    3 AS product_id
    , 20 AS product_price
    , 7 AS product_weight
UNION ALL SELECT
    4 AS product_id
    , 25 AS product_price
    , 9 AS product_weight
UNION ALL SELECT
    5 AS product_id
    , 30 AS product_price
    , 11 AS product_weight;
