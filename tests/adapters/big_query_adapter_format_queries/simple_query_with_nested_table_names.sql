CREATE TABLE downsampled_customer_db.customers_formatted AS
SELECT *
FROM customer_db.customers
ORDER BY RAND()
LIMIT 300;
CREATE TABLE `avaus-academy.downsampled_customer_db.customers_formatted` AS
SELECT *
FROM `avaus-academy.customer_db.customers`
ORDER BY RAND()
LIMIT 300
