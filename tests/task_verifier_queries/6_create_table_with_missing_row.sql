DROP TABLE IF EXISTS table_with_missing_row;

CREATE TABLE table_with_missing_row (
        Email VARCHAR(255) NOT NULL,
        First_Name CHAR(25) NOT NULL,
        Last_Name CHAR(25),
        Score INT
);

INSERT INTO table_with_missing_row VALUES("john.doe@email.com", "John", "Doe", "12");
INSERT INTO table_with_missing_row VALUES("jane.doe@email.fi", "Jane", "Doe", "142");