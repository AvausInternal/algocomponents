MERGE
  weather_data.weather_forecast_Helsinki h
USING
  weather_data.weather_forecast_Stockholm s
ON
  s.time_epoch=h.time_epoch
  WHEN NOT MATCHED
  THEN
INSERT
  (temp_c)
VALUES
  (2);
MERGE
  `avaus-academy.weather_data.weather_forecast_Helsinki` h
USING
  `avaus-academy.weather_data.weather_forecast_Stockholm` s
ON
  s.time_epoch=h.time_epoch
  WHEN NOT MATCHED
  THEN
INSERT
  (temp_c)
VALUES
  (2)