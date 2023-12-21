WITH book AS (
    SELECT
        CustomerID AS CustomerId
        , (LEFT(
            CAST(EXTRACT(YEAR FROM TimeCreated) AS string)
            , 4
        ) || "-" || BookingNr) AS BookingNo
    FROM raw.mimer_pb_acs_customerid_bookingnr
)

SELECT
    book.CustomerID
    , book.BookingNo
    , ctrl.CustomerNr
    , ctrl.ControlGroup
    , ctrl.DatetimeAddedControlGroup AS ctrl_date_added
FROM tmp.control_groups0001 AS ctrl
INNER JOIN book
    ON ctrl.CustomerId = book.CustomerID;
WITH book AS (
    SELECT
        CustomerID AS CustomerId
        , (LEFT(
            CAST(EXTRACT(YEAR FROM TimeCreated) AS string)
            , 4
        ) || "-" || BookingNr) AS BookingNo
    FROM `avaus-academy.raw.mimer_pb_acs_customerid_bookingnr`
)

SELECT
    book.CustomerID
    , book.BookingNo
    , ctrl.CustomerNr
    , ctrl.ControlGroup
    , ctrl.DatetimeAddedControlGroup AS ctrl_date_added
FROM `avaus-academy.tmp.control_groups0001` AS ctrl
INNER JOIN book
    ON ctrl.CustomerId = book.CustomerID
