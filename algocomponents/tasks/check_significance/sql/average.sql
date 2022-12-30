SELECT 
    AVG({target_column}) as average
FROM {input_table}
WHERE {group_column} = '{group_}'
