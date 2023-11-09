WITH sessions_events AS (
    SELECT
        (
            SELECT value.string_value
            FROM UNNEST(event_params)
            WHERE key = "page_location"
        ) AS locations
        , (
            SELECT value.int_value
            FROM UNNEST(event_params)
            WHERE key = "ga_session_id"
        ) AS ga_session_id
        , MAX(user_pseudo_id) AS user_pseudo_id
        , MAX(CASE event_name WHEN "session_start" THEN event_timestamp END)
            AS session_start
        , MAX(CASE event_name WHEN "user_engagement" THEN event_timestamp END)
            AS end_visit
        , MAX(event_date) AS event_date
        , MAX(
            (
                SELECT value.string_value
                FROM UNNEST(event_params)
                WHERE key = "page_title"
            )
        ) AS title
        , MAX(
            (
                SELECT value.string_value
                FROM UNNEST(event_params)
                WHERE key = "page_referrer"
            )
        ) AS referrer
        , MAX(
            (
                SELECT value.string_value
                FROM UNNEST(event_params)
                WHERE key = "Article tag"
            )
        ) AS article_tag
    FROM `avaus-com-ga.analytics_243066661.events_*`
    GROUP BY ga_session_id, locations
)

, sessions_duration AS (
    SELECT
        user_pseudo_id
        , ga_session_id
        , article_tag
        , PARSE_DATE("%Y%m%d", event_date) AS event_date
        , SAFE_SUBTRACT(end_visit, session_start) AS duration
        , STRUCT(title, locations, referrer) AS page
    FROM sessions_events
    ORDER BY ga_session_id

)

SELECT
    user_pseudo_id
    , event_date
    , duration
    , ga_session_id
    , article_tag
    , page
FROM sessions_duration
WHERE event_date BETWEEN "2021-08-01" AND CURRENT_DATE()
ORDER BY event_date;
