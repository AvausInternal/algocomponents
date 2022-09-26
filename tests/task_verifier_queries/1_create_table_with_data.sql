DROP TABLE IF EXISTS table_with_data;

CREATE TABLE table_with_data (
        Email VARCHAR(255) NOT NULL,
        First_Name CHAR(25) NOT NULL,
        Last_Name CHAR(25),
        Score INT
);

INSERT INTO table_with_data VALUES("john.doe@email.com", "John", "Doe", "12");
INSERT INTO table_with_data VALUES("jane.doe@email.fi", "Jane", "Doe", "142");
INSERT INTO table_with_data VALUES("dummy.user@email.fi", "Dummy", "User", "33");