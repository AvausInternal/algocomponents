CREATE OR REPLACE TABLE tmp.ltv_features AS
SELECT
    customer_id
    , column_ending_in_update AS how_did_we_ever_miss_this
FROM tmp.stupid_simple_bugs;
CREATE OR REPLACE TABLE `avaus-academy.tmp.ltv_features` AS
SELECT
    customer_id
    , column_ending_in_update AS how_did_we_ever_miss_this
FROM `avaus-academy.tmp.stupid_simple_bugs`
