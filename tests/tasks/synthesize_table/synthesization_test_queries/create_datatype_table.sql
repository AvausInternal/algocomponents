DROP TABLE IF EXISTS synthesization_datatype_test;

CREATE TABLE synthesization_datatype_test AS
SELECT
    "Take on me" AS string_column
    , 7 AS int_column
    , True AS bool_column
    , 3.84 AS float_column
    , DATE("2018-08-01") AS date_column
    , DATETIME("2020-08-01 01:21:00") AS datetime_column
    , X'ABCD' AS blob_column
UNION ALL SELECT
    "Take me on" AS string_column
    , 5 AS int_column
    , False AS bool_column
    , 1.39 AS float_column
    , DATE("2022-01-01") AS date_column
    , DATETIME("2024-11-05 10:31:00") AS datetime_column
    , X'1234' AS blob_column;
