SELECT
  event_params.list,
  lst.element.value.string_value
FROM
  Mateusz.ga_test,
  UNNEST(event_params.list) lst
WHERE
  lst.element.value.string_value LIKE "%shop.googlemerchandisestore%";
SELECT
  event_params.list,
  lst.element.value.string_value
FROM
  `avaus-academy.Mateusz.ga_test`,
  UNNEST(event_params.list) lst
WHERE
  lst.element.value.string_value LIKE "%shop.googlemerchandisestore%"