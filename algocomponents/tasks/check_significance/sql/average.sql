SELECT
    AVG({target_column}) AS average
FROM {input_table}
WHERE {group_column} = "{group_}"
