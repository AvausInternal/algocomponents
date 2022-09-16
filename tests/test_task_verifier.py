from unittest import TestCase
import sqlite3

from algocomponents.tasks.task_verifier.task_verifier import (
    VerifyOutput,
    SaveExpectedOutput,
)
from algocomponents.adapters import LocalSqliteAdapter
from algocomponents.tasks import SQLPipeline


class EmptySQLPipeline(SQLPipeline):
    pass


class TestTaskVerifier(TestCase):
    def setUp(self):
        self.sql_pipeline = EmptySQLPipeline(sql_adapter=LocalSqliteAdapter())
        connection_obj = sqlite3.connect("local_sqlite.db")
        cursor_obj = connection_obj.cursor()
        tables = [
            "table_with_data",
            "table_without_data",
            "exp_out_table",
            "table_with_diff_cols",
        ]
        for table in tables:
            delete = f"""DROP TABLE IF EXISTS {table};"""
            cursor_obj.execute(delete)
            connection_obj.commit()

        table_without_data = """ CREATE TABLE table_without_data (
                    Email VARCHAR(255) NOT NULL,
                    First_Name CHAR(25) NOT NULL,
                    Last_Name CHAR(25),
                    Score INT
                ); """
        cursor_obj.execute(table_without_data)
        connection_obj.commit()
        table_with_data = """ CREATE TABLE table_with_data (
                    Email VARCHAR(255) NOT NULL,
                    First_Name CHAR(25) NOT NULL,
                    Last_Name CHAR(25),
                    Score INT
                ); """
        cursor_obj.execute(table_with_data)
        connection_obj.commit()

        data = (
            """ INSERT INTO table_with_data VALUES("joni", "joni", "rajala", "12"); """
        )
        cursor_obj.execute(data)
        connection_obj.commit()

        exp_out_table = """ CREATE TABLE exp_out_table (
                    Email VARCHAR(255) NOT NULL,
                    First_Name CHAR(25) NOT NULL,
                    Last_Name CHAR(25),
                    Score INT
                ); """
        cursor_obj.execute(exp_out_table)
        connection_obj.commit()

        data = """ INSERT INTO exp_out_table VALUES("joni", "joni", "rajala", "12"); """
        cursor_obj.execute(data)
        connection_obj.commit()

        table_with_diff_cols = """ CREATE TABLE table_with_diff_cols (
                    Email VARCHAR(255) NOT NULL,
                    First_Name CHAR(25) NOT NULL,
                    Score INT
                ); """
        cursor_obj.execute(table_with_diff_cols)
        connection_obj.commit()

        connection_obj.close()

    # Tests for Setupping the TaskVerifier
    def test_successful_setup(self):
        verifier = SaveExpectedOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_data",
            expected_output_table="exp_out_table",
        )
        try:
            verifier.start()
        except Exception as e:
            self.fail("Throws exception on setup")

    def test_setup_missing_output_table(self):
        verifier = SaveExpectedOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_which_doesnt_exist",
            expected_output_table="exp_out_table",
        )
        with self.assertRaises(Exception):
            verifier.start()

    # Tests for verifying task
    def test_missing_expected_output_table(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_data",
            expected_output_table="table_which_doesnt_exist",
        )
        with self.assertRaises(Exception):
            verifier.start()

    def test_missing_task_output_table(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_which_doesnt_exist",
            expected_output_table="table_with_data",
        )
        with self.assertRaises(Exception):
            verifier.start()

    def test_matching_data(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_data",
            expected_output_table="exp_out_table",
        )
        try:
            verifier.start()
        except:
            self.fail(f"Throws exception even though data matches")

    def test_missing_data(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_without_data",
            expected_output_table="exp_out_table",
        )
        with self.assertRaises(Exception):
            verifier.start()

    def test_different_columns(self):
        verifier = VerifyOutput(
            for_task=self.sql_pipeline,
            task_output_table="table_with_diff_cols",
            expected_output_table="exp_out_table",
        )
        with self.assertRaises(Exception):
            verifier.start()
