DROP TABLE IF EXISTS {OUTPUT_TABLE};

CREATE TABLE {OUTPUT_TABLE} AS
SELECT 
  product_id,
  product_price,
  product_weight,
  product_price*1.0/product_weight as price_per_kg
FROM
  {INPUT_TABLE}
;
