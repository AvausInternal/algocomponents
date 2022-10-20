CREATE OR REPLACE TABLE `avaus-academy.db.output_prediction` AS

SELECT
    *
FROM ML.PREDICT (
    MODEL `avaus-academy.db.output_model`,
    (
        SELECT
            * EXCEPT(dataframe, snacker_id)
        FROM `avaus-academy.db.data_split_table`
        WHERE dataframe = 'test'
    )
)
;
