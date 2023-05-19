DROP TABLE IF EXISTS synthesization_test;

CREATE TABLE synthesization_test AS
          SELECT 1 AS a, 2 AS b, 3 AS c
UNION ALL SELECT 2 AS a, 4 AS b, 6 AS c
UNION ALL SELECT 3 AS a, 6 AS b, 9 AS c
UNION ALL SELECT 4 AS a, 8 AS b, 12 AS c
