from typing import Any

import duckdb
from dojocommons.infrastructure.logging.logger import logger

from dojocommons.infrastructure.config.app_configuration import (
    AppConfiguration,
)


class DuckDbService:
    def __init__(self, cfg: AppConfiguration):
        self._cfg = cfg
        self._conn = duckdb.connect()
        self._configure_s3()
        logger.debug("DuckDB initialized", endpoint=self._cfg.aws_endpoint)

    def _configure_s3(self):
        self._conn.execute("SET home_directory='/tmp'")
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")

        if self._cfg.aws_endpoint:
            self._configure_localstack()
        else:
            self._configure_aws()

    def _configure_localstack(self):
        logger.debug("Configuring DuckDB for LocalStack")
        self._conn.execute("SET s3_access_key_id='test'")
        self._conn.execute("SET s3_secret_access_key='test'")
        self._conn.execute("SET s3_region='us-east-1'")
        self._conn.execute("SET s3_url_style='path'")
        self._conn.execute("SET s3_use_ssl=false")
        self._conn.execute("SET s3_endpoint=?", (self._cfg.aws_endpoint,))

    def _configure_aws(self):
        logger.debug("Configuring DuckDB for AWS IAM Role")

        region = self._cfg.aws_region or "sa-east-1"
        endpoint = f"s3.{region}.amazonaws.com"

        self._conn.execute("SET s3_region=?", (region,))
        self._conn.execute("SET s3_url_style='path'")
        self._conn.execute("SET s3_endpoint=?", (endpoint,))
        self._conn.execute("SET s3_use_ssl=true")
        self._conn.execute("SET s3_url_compatibility_mode=true")

    def execute(self, query: str, params: tuple | None = None) -> Any:
        if params:
            return self._conn.execute(query, params)
        return self._conn.execute(query)

    def close(self) -> None:
        self._conn.close()
