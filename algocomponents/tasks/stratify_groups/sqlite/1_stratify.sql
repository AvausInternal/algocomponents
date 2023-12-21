DROP TABLE IF EXISTS {output_table};

CREATE TABLE {output_table} AS
SELECT
    *
    , ROW_NUMBER() OVER (
        ORDER BY
            {stratify_on}
    ) % {n_groups} + 1 AS test_group
FROM {input_table};
