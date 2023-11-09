DROP TABLE IF EXISTS {output_table};

-- CREATE TABLE {output_table} AS
SELECT
    user_id
    , COUNT(*) AS n_products_bought
FROM {input_table}
GROUP BY user_id;
