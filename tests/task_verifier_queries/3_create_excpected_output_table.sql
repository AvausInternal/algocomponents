DROP TABLE IF EXISTS exp_out_table;

CREATE TABLE exp_out_table (
        Email VARCHAR(255) NOT NULL,
        First_Name CHAR(25) NOT NULL,
        Last_Name CHAR(25),
        Score INT
);

INSERT INTO exp_out_table VALUES("john.doe@email.com", "John", "Doe", "12");
INSERT INTO exp_out_table VALUES("jane.doe@email.fi", "Jane", "Doe", "142");
INSERT INTO exp_out_table VALUES("dummy.user@email.fi", "Dummy", "User", "33");
