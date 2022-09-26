DROP TABLE IF EXISTS table_with_diff_value;

CREATE TABLE table_with_diff_value (
        Email VARCHAR(255) NOT NULL,
        First_Name CHAR(25) NOT NULL,
        Last_Name CHAR(25),
        Score INT
);

INSERT INTO table_with_diff_value VALUES("john.doe@email.com", "John", "Doe", "12");
INSERT INTO table_with_diff_value VALUES("jane.doe@email.fi", "Jane", "Doe", "142");
INSERT INTO table_with_diff_value VALUES("dummy.user@email.fi", "Dummy", "User", "55");