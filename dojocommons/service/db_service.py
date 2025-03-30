import duckdb
from sqlalchemy.orm import declarative_base

from dojocommons.model.app_configuration import AppConfiguration

Base = declarative_base()


class DbService:
    def __init__(self, app_cfg: AppConfiguration):
        self._app_cfg = app_cfg
        self._conn = duckdb.connect()
        self._init_duckdb()

    def __del__(self):
        self.close_connection()

    def _init_duckdb(self):
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")
        self._conn.execute(f"SET s3_region='{self._app_cfg.aws_region}';")

        if self._app_cfg.aws_endpoint is not None:
            self._conn.execute(
                f"SET s3_access_key_id='{self._app_cfg.aws_access_key_id}';"
            )
            self._conn.execute(
                f"SET s3_secret_access_key="
                f"'{self._app_cfg.aws_secret_access_key}';"
            )
            self._conn.execute("SET s3_url_style='path';")
            self._conn.execute("SET s3_use_ssl=false;")
            self._conn.execute(
                f"SET s3_endpoint='{self._app_cfg.aws_endpoint}';"
            )

    def create_table_from_csv(self, table_name: str):
        query = (
            f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * "
            f"FROM read_csv_auto('{self._app_cfg.s3_file_path}/{table_name}.csv');"
        )

        return self.execute_query(query)

    def persist_data(self, table_name: str):
        query = (
            f"COPY {table_name} TO '{self._app_cfg.s3_file_path}/{table_name}.csv' "
            f"(FORMAT CSV, HEADER TRUE)"
        )

        return self.execute_query(query)

    def execute_query(self, query: str, params: tuple = None):
        if params is None:
            return self._conn.execute(query)
        return self._conn.execute(query, params)

    def close_connection(self):
        self._conn.close()
