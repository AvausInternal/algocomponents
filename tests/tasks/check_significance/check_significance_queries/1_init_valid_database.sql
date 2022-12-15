DROP TABLE IF EXISTS dummy_test_results;

CREATE TABLE dummy_test_results (
    customer VARCHAR(255) NOT NULL,
    group_ CHAR(25) NOT NULL,
    sales INT
);

INSERT INTO dummy_test_results VALUES("1234", "test", "12");
INSERT INTO dummy_test_results VALUES("2345", "test", "142");
INSERT INTO dummy_test_results VALUES("3456", "control", "313");
INSERT INTO dummy_test_results VALUES("2344", "test", "132");
INSERT INTO dummy_test_results VALUES("5555", "control", "12");
INSERT INTO dummy_test_results VALUES("1111", "control", "3");
INSERT INTO dummy_test_results VALUES("8765", "control", "124");
INSERT INTO dummy_test_results VALUES("7777", "test", "1432");
INSERT INTO dummy_test_results VALUES("0101", "control", "3");
