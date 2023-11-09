DROP TABLE IF EXISTS {tmp_db}.{output_table};

CREATE TABLE {tmp_db}.{output_table} AS
SELECT
    threshold
    , TP
    , FP
    , TN
    , FN
    , ROUND(1.0 * (TP + TN) / NULLIF((TP + TN + FP + FN), 0), 2)
        AS accuracy_metric
    , ROUND(1.0 * TP / NULLIF(TP + FP, 0), 2) AS precision_metric
    , ROUND(1.0 * TP / NULLIF(TP + FN, 0), 2) AS recall_metric
    , ROUND(2.0 * TP / NULLIF(2 * TP + FP + FN, 0), 2) AS f1_score
FROM {tmp_db}.confusion_matrix
ORDER BY threshold ASC;
