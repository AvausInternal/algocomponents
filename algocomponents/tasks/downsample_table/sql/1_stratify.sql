DROP TABLE IF EXISTS {output_table};

CREATE TABLE {output_table} AS
SELECT
    *
FROM {stratify_in_between_table}
WHERE test_group = 1
;
