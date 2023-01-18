resource "google_bigquery_routine" "test_routine_terraform" {
  dataset_id      = "transform"
  routine_id      = "prep_email_to_ads"
  routine_type    = "SCALAR_FUNCTION"
  language        = "SQL"
  definition_body = "TO_HEX(SHA256(LOWER(TRIM(x))))"
  arguments {
    name      = "x"
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  return_type = "{\"typeKind\" :  \"STRING\"}" # not necessary
  project     = var.gcp_project_name
}

# various options described here: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_routine

resource "google_bigquery_routine" "get_known_users" {
  dataset_id      = var.transform_dataset_id
  routine_id      = "get_known_users"
  routine_type    = "PROCEDURE"
  language        = "SQL"
  description = <<-EOS
  ID KEY - a string with the name of the column which is a unique identifier in your table (e.g. "user_id")
  START_SUFFIX - the beginning of the period you want to get (in the format "YYYYMMDD", e.g. "20221201")
  END_SUFFIX - the end of the period you want to get (in the format "YYYYMMDD", e.g. "20221231")
  EOS
  definition_body = <<-EOS
  SELECT
    *
  FROM
    `${var.ga_project_id}.${var.ga_dataset_id}.events_*`
  LEFT JOIN
    UNNEST(user_properties) AS up
  WHERE
    (_TABLE_SUFFIX BETWEEN START_SUFFIX
      AND END_SUFFIX)
    AND ((LOWER(ID_KEY)='user_id' AND user_id IS NOT NULL) OR (up.key=ID_KEY AND up.value.string_value IS NOT NULL))
  EOS
  arguments {
    name      = "ID_KEY"
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "START_SUFFIX" # in the format: YYYYMMDD
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "END_SUFFIX" # in the format: YYYYMMDD
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  project = var.gcp_project_name
}

resource "google_bigquery_routine" "get_unknown_users" {
  dataset_id      = var.transform_dataset_id
  routine_id      = "get_unknown_users"
  routine_type    = "PROCEDURE"
  language        = "SQL"
    description = <<-EOS
  ID KEY - a string with the name of the column which is a unique identifier in your table (e.g. "user_id")
  START_SUFFIX - the beginning of the period you want to get (in the format "YYYYMMDD", e.g. "20221201")
  END_SUFFIX - the end of the period you want to get (in the format "YYYYMMDD", e.g. "20221231")
  EOS
  definition_body = <<-EOS
  SELECT
  *
  FROM
    `${var.ga_project_id}.${var.ga_dataset_id}.events_*`
  LEFT JOIN
    UNNEST(user_properties) AS up
  WHERE
    (_TABLE_SUFFIX BETWEEN START_SUFFIX
      AND END_SUFFIX)
  AND ((LOWER(ID_KEY)='user_id' AND user_id IS NULL) OR (up.key=ID_KEY AND up.value.string_value IS NULL))
  EOS
  arguments {
    name      = "ID_KEY"
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "START_SUFFIX" # in the format: YYYYMMDD
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "END_SUFFIX" # in the format: YYYYMMDD
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  project = var.gcp_project_name
}

resource "google_bigquery_routine" "get_flattened_categorical_data" {
  dataset_id      = var.transform_dataset_id
  routine_id      = "get_flattened_categorical_data"
  routine_type    = "PROCEDURE"
  language        = "SQL"
    description = <<-EOS
  ID KEY - a string with the name of the column which is a unique identifier in your table (e.g. "user_id")
  START_SUFFIX - the beginning of the period you want to get (in the format "YYYYMMDD", e.g. "20221201")
  END_SUFFIX - the end of the period you want to get (in the format "YYYYMMDD", e.g. "20221231")
  EOS
  definition_body = <<-EOS
SELECT
  * EXCEPT(last_record)
FROM (
  SELECT
    ROW_NUMBER() OVER(PARTITION BY IF (LOWER(ID_KEY)='user_id',user_id, IF (up.key=ID_KEY,up.value.string_value,user_pseudo_id))
    ORDER BY
      event_timestamp DESC) AS last_record,
  IF
    ((LOWER(ID_KEY)='user_id'
        AND user_id IS NOT NULL)
      OR (up.key=ID_KEY
        AND up.value.string_value IS NOT NULL),'known','unknown') AS id_type,
    user_pseudo_id,
    user_id,
    up.key,
    up.value.string_value,
    event_timestamp,
    stream_id,
    platform,
    geo.*,
    traffic_source.*,
    privacy_info.*,
    device.*
  FROM
    `${var.ga_project_id}.${var.ga_dataset_id}.events_*`
  LEFT JOIN
    UNNEST(user_properties) AS up
  WHERE
    (_TABLE_SUFFIX BETWEEN START_SUFFIX
    AND END_SUFFIX) ) cte
WHERE
  last_record=1
EOS
  arguments {
    name      = "ID_KEY"
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "START_SUFFIX" # in the format: YYYYMMDD
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "END_SUFFIX" # in the format: YYYYMMDD
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  project = var.gcp_project_name
}

resource "google_bigquery_routine" "get_time_grouped_page_views_per_user" {
  dataset_id      = var.transform_dataset_id
  routine_id      = "get_time_grouped_page_views_per_user"
  routine_type    = "PROCEDURE"
  language        = "SQL"
    description = <<-EOS
    MODE - used to indicate whether you want daily, weekly or monthly data. Accepted values: 'day', 'week' or 'month'.
    DAYS - how many days since the current timestamp you want the data to come from
    EOS
  definition_body = <<-EOS
SELECT user_id,time_grouping AS time_grouping,COUNT(*) AS page_views FROM
(
SELECT user_id, event_timestamp,
CASE
WHEN LOWER(MODE)='day' THEN FORMAT_TIMESTAMP('%d%m%Y',TIMESTAMP_MICROS(event_timestamp))
WHEN LOWER(MODE)='week' THEN FORMAT_TIMESTAMP('%V%Y',TIMESTAMP_MICROS(event_timestamp))
WHEN LOWER(MODE)='month' THEN FORMAT_TIMESTAMP('%m%Y',TIMESTAMP_MICROS(event_timestamp))
ELSE 'INCORRECT MODE SELECTED - CHOOSE FROM: (day, week, month)'
END AS time_grouping
FROM
  `${var.ga_project_id}.${var.ga_dataset_id}.events_*`
  WHERE event_name = 'page_view'
    AND
  (TIMESTAMP_MICROS(event_timestamp) BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL DAYS DAY) AND CURRENT_TIMESTAMP() )
  AND (_TABLE_SUFFIX BETWEEN FORMAT_TIMESTAMP('%Y%m%d',TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL DAYS DAY)) AND FORMAT_TIMESTAMP('%Y%m%d',CURRENT_TIMESTAMP()))
AND user_id IS NOT NULL
)
GROUP BY user_id,time_grouping
ORDER BY user_id,MAX(event_timestamp)

EOS
  arguments {
    name      = "MODE" # either 'day', 'week' or 'month'
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  arguments {
    name      = "DAYS" # how many days in the past we want to look from current timestamp
    data_type = "{\"typeKind\" :  \"INT64\"}"
  }
  project = var.gcp_project_name
}