SELECT
    SUM(
        ({target_column} - (SELECT AVG({target_column}) FROM {input_table} WHERE {group_column} = '{group_}'))
        *
        ({target_column} - (SELECT AVG({target_column}) FROM {input_table} WHERE {group_column} = '{group_}'))
    ) / (
        COUNT({target_column})-1
    ) AS variance
FROM {input_table}
WHERE {group_column} = '{group_}'
