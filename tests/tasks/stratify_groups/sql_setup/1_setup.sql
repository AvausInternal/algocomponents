DROP TABLE IF EXISTS {mock_table};

CREATE TABLE {mock_table} AS
          SELECT 12645 AS customer_id, "SE" AS country, "Stockholm" AS city
UNION ALL SELECT 54762 AS customer_id, "SE" AS country, "Göteborg" AS city
UNION ALL SELECT 68456 AS customer_id, "SE" AS country, "Visby" AS city
UNION ALL SELECT 39485 AS customer_id, "SE" AS country, "Kalmar" AS city
UNION ALL SELECT 23576 AS customer_id, "SE" AS country, "Stockholm" AS city
UNION ALL SELECT 23465 AS customer_id, "SE" AS country, "Lund" AS city
UNION ALL SELECT 23462 AS customer_id, "NO" AS country, "Oslo" AS city
UNION ALL SELECT 75637 AS customer_id, "NO" AS country, "Oslo" AS city
UNION ALL SELECT 35726 AS customer_id, "NO" AS country, "Oslo" AS city
UNION ALL SELECT 94254 AS customer_id, "DK" AS country, "Köpenhamn" AS city
{truncate_statement}
