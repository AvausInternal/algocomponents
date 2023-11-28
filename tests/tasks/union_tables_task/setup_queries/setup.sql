DROP TABLE IF EXISTS triforce_of_power;
CREATE TABLE triforce_of_power AS
SELECT
    "Ganondorf" AS holder
    , "Din" AS goddess;

DROP TABLE IF EXISTS triforce_of_wisdom;
CREATE TABLE triforce_of_wisdom AS
SELECT
    "Zelda" AS holder
    , "Nayru" AS goddess;

DROP TABLE IF EXISTS triforce_of_courage;
CREATE TABLE triforce_of_courage AS
SELECT
    "Link" AS holder
    , "Farore" AS goddess;

DROP TABLE IF EXISTS light_arrows;
CREATE TABLE light_arrows AS
SELECT "Link" AS holder;
