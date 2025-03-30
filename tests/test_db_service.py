import os
import unittest
from unittest.mock import patch, call

from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.service.db_service import DbService


@patch.dict(
    os.environ,
    {
        "APP_NAME": "test_app",
        "APP_VERSION": "1.0.0",
        "S3_BUCKET": "test-bucket",
        "S3_PATH": "db",
        "AWS_REGION": "us-east-1",
        "AWS_ENDPOINT": "http://localhost:9000",
        "AWS_ACCESS_KEY_ID": "test_access_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret_key",
    },
)
@patch("dojocommons.service.db_service.duckdb.connect")
class TestDbService(unittest.TestCase):
    def test_init_duckdb_with_endpoint(self, mock_connect):
        mock_conn = mock_connect.return_value
        _ = DbService(AppConfiguration())  # type: ignore

        self.assertEqual(
            [
                call("INSTALL httpfs; LOAD httpfs;"),
                call("SET s3_region='us-east-1';"),
                call("SET s3_access_key_id='test_access_key';"),
                call("SET s3_secret_access_key='test_secret_key';"),
                call("SET s3_url_style='path';"),
                call("SET s3_use_ssl=false;"),
                call("SET s3_endpoint='http://localhost:9000';"),
            ],
            mock_conn.execute.call_args_list,
        )

    def test_create_table_from_csv(self, mock_connect):
        mock_conn = mock_connect.return_value
        table_name = "test_table"
        expected_query = (
            f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * "
            f"FROM read_csv_auto('s3://test-bucket/db/{table_name}.csv');"
        )

        db_service = DbService(AppConfiguration())  # type: ignore

        db_service.create_table_from_csv(table_name)
        self.assertEqual(call(expected_query), mock_conn.execute.call_args)

    def test_persist_data(self, mock_connect):
        mock_conn = mock_connect.return_value
        table_name = "test_table"
        expected_query = (
            f"COPY {table_name} TO 's3://test-bucket/db/{table_name}.csv' "
            f"(FORMAT CSV, HEADER TRUE)"
        )

        db_service = DbService(AppConfiguration())  # type: ignore
        db_service.persist_data(table_name)

        self.assertEqual(call(expected_query), mock_conn.execute.call_args)

    def test_execute_query(self, mock_connect):
        mock_conn = mock_connect.return_value

        query = "SELECT * FROM test_table"
        params = ("param1", "param2")

        db_service = DbService(AppConfiguration())  # type: ignore
        db_service.execute_query(query, params)

        self.assertEqual(call(query, params), mock_conn.execute.call_args)

    def test_execute_query_no_params(self, mock_connect):
        mock_conn = mock_connect.return_value

        query = "SELECT * FROM test_table"

        db_service = DbService(AppConfiguration())  # type: ignore
        db_service.execute_query(query)

        self.assertEqual(call(query), mock_conn.execute.call_args)

    def test_close_connection(self, mock_connect):
        mock_conn = mock_connect.return_value

        db_service = DbService(AppConfiguration())  # type: ignore
        db_service.close_connection()

        self.assertTrue(mock_conn.close.called)

    def test_delete_class(self, mock_connect):
        mock_conn = mock_connect.return_value

        db_service = DbService(AppConfiguration())  # type: ignore

        del db_service
        self.assertTrue(mock_conn.close.called)


if __name__ == "__main__":
    unittest.main()
