import datetime
import os
import unittest
from unittest.mock import call, patch

import duckdb
from pydantic import BaseModel

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
                call("SET s3_region=?;", ("us-east-1",)),
                call("SET s3_access_key_id=?;", ("test_access_key",)),
                call("SET s3_secret_access_key=?;", ("test_secret_key",)),
                call("SET s3_url_style='path';"),
                call("SET s3_use_ssl=false;"),
                call("SET s3_endpoint=?;", ("http://localhost:9000",)),
            ],
            mock_conn.execute.call_args_list,
        )

    def test_create_table_from_parquet(self, mock_connect):
        mock_conn = mock_connect.return_value
        table_name = "test_table"
        path = f"s3://test-bucket/db/{table_name}.parquet"
        expected_query = (
            f"CREATE TABLE IF NOT EXISTS {table_name}"
            f" AS SELECT * FROM read_parquet('{path}');"
        )

        db_service = DbService(AppConfiguration())  # type: ignore

        db_service.create_table_from_parquet(table_name)
        self.assertEqual(
            call(expected_query),
            mock_conn.execute.call_args,
        )

    def test_persist_data(self, mock_connect):
        mock_conn = mock_connect.return_value
        table_name = "test_table"
        expected_query = "COPY ? TO ? (FORMAT PARQUET, COMPRESSION ZSTD)"
        path = f"s3://test-bucket/db/{table_name}.parquet"

        db_service = DbService(AppConfiguration())  # type: ignore
        db_service.persist_data(table_name)

        self.assertEqual(
            call(expected_query, (table_name, path)),
            mock_conn.execute.call_args,
        )

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

        # noinspection PyUnusedLocal
        db_service = DbService(AppConfiguration())  # type: ignore

        del db_service
        self.assertTrue(mock_conn.close.called)

    @patch.object(DbService, "create_table_from_model")
    @patch.object(DbService, "create_table_from_parquet")
    def test_create_table_fallbacks_to_model(
        self, mock_create_parquet, mock_create_model, _
    ):
        class DummyModel(BaseModel):
            id: int
            name: str

        db_service = DbService(AppConfiguration())  # type: ignore

        # Mock methods
        mock_create_parquet.side_effect = duckdb.IOException("fail")

        db_service.create_table(DummyModel, "dummy_table")

        self.assertEqual(
            call("dummy_table"),
            mock_create_parquet.call_args,
        )
        self.assertEqual(
            call(DummyModel),
            mock_create_model.call_args,
        )

    def test_create_table_from_model_executes_sql(self, mock_connect):
        mock_conn = mock_connect.return_value

        class DummyModel(BaseModel):
            id: int
            name: str
            created_at: datetime.datetime

        db_service = DbService(AppConfiguration())  # type: ignore

        # Mock execute_query
        db_service.create_table_from_model(DummyModel)

        self.assertEqual(
            call(
                "CREATE TABLE dummymodel (\n"
                "    id INTEGER NOT NULL PRIMARY KEY,\n"
                "    name TEXT NOT NULL,\n"
                "    created_at TIMESTAMP NOT NULL\n);"
            ),
            mock_conn.execute.call_args,
        )


if __name__ == "__main__":
    unittest.main()
