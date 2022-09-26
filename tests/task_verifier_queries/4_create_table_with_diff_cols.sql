DROP TABLE IF EXISTS table_with_diff_cols;

CREATE TABLE table_with_diff_cols (
        Email VARCHAR(255) NOT NULL,
        First_Name CHAR(25) NOT NULL,
        Last_Name CHAR(25)
);

INSERT INTO table_with_diff_cols VALUES("john.doe@email.com", "John", "Doe");
INSERT INTO table_with_diff_cols VALUES("jane.doe@email.fi", "Jane", "Doe");
INSERT INTO table_with_diff_cols VALUES("dummy.user@email.fi", "Dummy", "User");