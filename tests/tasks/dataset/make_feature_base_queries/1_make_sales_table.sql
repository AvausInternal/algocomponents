DROP TABLE IF EXISTS {output_table};

CREATE TABLE {output_table} AS --this is a featurebase
SELECT
    1 AS user_id
    , 1 AS product_id
UNION ALL SELECT
    1 AS user_id
    , 2 AS product_id
UNION ALL SELECT
    1 AS user_id
    , 3 AS product_id
UNION ALL SELECT
    2 AS user_id
    , 3 AS product_id
UNION ALL SELECT
    2 AS user_id
    , 4 AS product_id
UNION ALL SELECT
    3 AS user_id
    , 5 AS product_id
UNION ALL SELECT
    3 AS user_id
    , 5 AS product_id;
