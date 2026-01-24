from unittest.mock import Mock

from dojocommons.infrastructure.config.app_configuration import (
    AppConfiguration,
)
from dojocommons.infrastructure.persistence.duckdb_service import DuckDbService


def test_duckdb_service_initializes_localstack(mocker):
    # Arrange
    mock_conn = Mock()
    mock_connect = mocker.patch("duckdb.connect", return_value=mock_conn)

    cfg = AppConfiguration(
        s3_bucket="test",
        s3_path="test",
        aws_endpoint="http://localhost:4566",
        aws_region="us-east-1",
    )

    # Act
    _ = DuckDbService(cfg)

    # Assert
    mock_connect.assert_called_once()

    # chamadas básicas
    mock_conn.execute.assert_any_call("SET home_directory='/tmp'")
    mock_conn.execute.assert_any_call("INSTALL httpfs; LOAD httpfs;")

    # chamadas específicas do LocalStack
    mock_conn.execute.assert_any_call("SET s3_access_key_id='test'")
    mock_conn.execute.assert_any_call("SET s3_secret_access_key='test'")
    mock_conn.execute.assert_any_call("SET s3_region='us-east-1'")
    mock_conn.execute.assert_any_call("SET s3_url_style='path'")
    mock_conn.execute.assert_any_call("SET s3_use_ssl=false")
    mock_conn.execute.assert_any_call("SET s3_endpoint=?", (cfg.aws_endpoint,))


def test_duckdb_service_initializes_aws(mocker):
    mock_conn = Mock()
    mocker.patch("duckdb.connect", return_value=mock_conn)

    cfg = AppConfiguration(
        s3_bucket="test",
        s3_path="test",
        aws_endpoint=None,
        aws_region="sa-east-1",
    )

    _ = DuckDbService(cfg)

    mock_conn.execute.assert_any_call("SET s3_region=?", ("sa-east-1",))
    mock_conn.execute.assert_any_call("SET s3_url_style='path'")
    mock_conn.execute.assert_any_call(
        "SET s3_endpoint=?", ("s3.sa-east-1.amazonaws.com",)
    )
    mock_conn.execute.assert_any_call("SET s3_use_ssl=true")
    mock_conn.execute.assert_any_call("SET s3_url_compatibility_mode=true")


def test_execute_calls_duckdb(mocker):
    mock_conn = Mock()
    mocker.patch("duckdb.connect", return_value=mock_conn)

    cfg = AppConfiguration(s3_bucket="x", s3_path="y")
    service = DuckDbService(cfg)

    service.execute("SELECT 1")

    mock_conn.execute.assert_called_with("SELECT 1")


def test_close_calls_duckdb_close(mocker):
    mock_conn = Mock()
    mocker.patch("duckdb.connect", return_value=mock_conn)

    cfg = AppConfiguration(s3_bucket="x", s3_path="y")
    service = DuckDbService(cfg)

    service.close()

    mock_conn.close.assert_called_once()
