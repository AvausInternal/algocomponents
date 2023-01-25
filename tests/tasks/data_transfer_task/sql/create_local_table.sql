DROP TABLE IF EXISTS data_transfer_table;

CREATE TABLE data_transfer_table AS 
SELECT 
    "LocalSQLite" AS adapter,
    2500 AS power_level
UNION ALL 
SELECT
    "LocalSQLite" AS adapter,
    3500 AS power_level

