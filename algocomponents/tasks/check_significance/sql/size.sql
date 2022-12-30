SELECT 
    COUNT({target_column}) AS size
FROM {input_table}
WHERE {group_column} = '{group_}'
