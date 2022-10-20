WITH sessions_events as(
  SELECT
    (SELECT value.string_value FROM UNNEST(event_params) where key = "page_location") AS locations,
    (SELECT value.int_value FROM UNNEST(event_params) where key = "ga_session_id") AS ga_session_id,
    MAX(user_pseudo_id) AS user_pseudo_id,
    MAX(Case event_name when 'session_start' then event_timestamp end) session_start,
    MAX(Case event_name when 'user_engagement' then event_timestamp  end) end_visit,
    MAX(event_date) AS event_date,
    MAX((SELECT value.string_value FROM UNNEST(event_params) where key = "page_title")) AS title,
    MAX((SELECT value.string_value FROM UNNEST(event_params) where key = "page_referrer")) AS referrer,
    MAX((SELECT value.string_value FROM UNNEST(event_params) where key = "Article tag")) AS article_tag,
  FROM `avaus-com-ga.analytics_243066661.events_*`
  GROUP BY ga_session_id, locations
),
  sessions_duration as(
  SELECT user_pseudo_id,
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  SAFE_SUBTRACT(end_visit, session_start) as duration,
  ga_session_id,
  article_tag,
  STRUCT(title, locations, referrer) AS page
  FROM sessions_events
  order by ga_session_id

)

  SELECT user_pseudo_id, event_date,
  duration,
  ga_session_id,
  article_tag,
  page
  FROM sessions_duration
  WHERE event_date BETWEEN '2021-08-01' AND CURRENT_DATE()
  order by event_date
;
