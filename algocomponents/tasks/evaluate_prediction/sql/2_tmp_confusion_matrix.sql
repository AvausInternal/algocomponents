DROP TABLE IF EXISTS {tmp_db}.confusion_matrix;

CREATE TABLE {tmp_db}.confusion_matrix AS
SELECT
    B.threshold
    , COUNT(
        CASE
            WHEN
                A.{target_label_column} = 1
                AND A.{prediction_column} > B.threshold
                THEN 1
        END
    ) AS TP
    , COUNT(
        CASE
            WHEN
                A.{target_label_column} = 0
                AND A.{prediction_column} > B.threshold
                THEN 1
        END
    ) AS FP
    , COUNT(
        CASE
            WHEN
                A.{target_label_column} = 0
                AND A.{prediction_column} < B.threshold
                THEN 1
        END
    ) AS TN
    , COUNT(
        CASE
            WHEN
                A.{target_label_column} = 1
                AND A.{prediction_column} < B.threshold
                THEN 1
        END
    ) AS FN
FROM {tmp_db}.{input_table} AS A
CROSS JOIN {tmp_db}.threshold_table AS B
GROUP BY B.threshold;
