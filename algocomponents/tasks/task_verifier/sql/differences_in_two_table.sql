-- Query which selects all rows that are not present in both of the tables


-- Select all the rows that are in TASK_OUTPUT_TABLE and are not in EXPECTED_OUTPUT_TABLE
SELECT * FROM (SELECT * FROM {TASK_OUTPUT_TABLE}
            {DISTINCT_STATEMENT}
            SELECT * FROM {EXPECTED_OUTPUT_TABLE}) 

-- Combine both tables
UNION ALL

-- Select all the rows that are in EXPECTED_OUTPUT_TABLE and are not in TASK_OUTPUT_TABLE
SELECT * FROM (SELECT * FROM {EXPECTED_OUTPUT_TABLE}
            {DISTINCT_STATEMENT}
            SELECT * FROM {TASK_OUTPUT_TABLE})