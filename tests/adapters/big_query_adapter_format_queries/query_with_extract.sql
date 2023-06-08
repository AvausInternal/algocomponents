SELECT book.CustomerID,book.BookingNo,
ctrl.CustomerNr,ctrl.ControlGroup,
ctrl.DatetimeAddedControlGroup AS ctrl_date_added,
FROM tmp.control_groups0001 AS ctrl
    INNER JOIN (
        SELECT (LEFT(
            CAST(EXTRACT(YEAR from TimeCreated) as string)
            , 4) || '-' || BookingNr) AS BookingNo,
            CustomerID AS CustomerId
        FROM raw.mimer_pb_acs_customerid_bookingnr) AS book
        ON ctrl.CustomerId=book.CustomerID
;
SELECT book.CustomerID,book.BookingNo,
ctrl.CustomerNr,ctrl.ControlGroup,
ctrl.DatetimeAddedControlGroup AS ctrl_date_added,
FROM `avaus-academy.tmp.control_groups0001` AS ctrl
    INNER JOIN (
        SELECT (LEFT(
            CAST(EXTRACT(YEAR from TimeCreated) as string)
            , 4) || '-' || BookingNr) AS BookingNo,
            CustomerID AS CustomerId
        FROM `avaus-academy.raw.mimer_pb_acs_customerid_bookingnr`) AS book
        ON ctrl.CustomerId=book.CustomerID
