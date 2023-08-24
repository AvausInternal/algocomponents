DROP TABLE IF EXISTS {output_table};

CREATE TABLE {output_table} AS
SELECT 
    product_id,
    product_price,
    product_weight,
    product_price*1.0/product_weight as price_per_kg
FROM
    {input_table}
;
