import duckdb

from dojocommons.model.app_configuration import AppConfiguration


class DbService:
    def __init__(self, app_cfg: AppConfiguration):
        self._app_cfg = app_cfg
        self._conn = duckdb.connect()
        self._init_duckdb()

    def __del__(self):
        self.close_connection()

    def _init_duckdb(self):
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")
        self._conn.execute("SET s3_region=?;", (self._app_cfg.aws_region,))
        if self._app_cfg.aws_endpoint is not None:
            self._conn.execute(
                "SET s3_access_key_id=?;", (self._app_cfg.aws_access_key_id,)
            )
            self._conn.execute(
                "SET s3_secret_access_key=?;",
                (self._app_cfg.aws_secret_access_key,),
            )
            self._conn.execute("SET s3_url_style='path';")
            self._conn.execute("SET s3_use_ssl=false;")
            self._conn.execute(
                "SET s3_endpoint=?;", (self._app_cfg.aws_endpoint,)
            )

    def create_table_from_csv(self, table_name: str):
        """
        Create a table in DuckDB from a CSV file stored in S3.
        :param table_name: the name of the table to create
        :return: the object with the result of the query execution
        """
        query = (
            "CREATE TABLE IF NOT EXISTS ? AS SELECT * "
            "FROM read_csv_auto(?);"
        )
        file_path = f"{self._app_cfg.s3_file_path}/{table_name}.csv"
        return self.execute_query(query, (table_name, file_path))

    def persist_data(self, table_name: str):
        """
        Persist data from a DuckDB table to a CSV file in S3.
        :param table_name: the name of the table to persist
        :return: the object with the result of the query execution
        """
        query = "COPY ? TO ? (FORMAT CSV, HEADER TRUE)"
        file_path = f"{self._app_cfg.s3_file_path}/{table_name}.csv"
        return self.execute_query(query, (table_name, file_path))

    def execute_query(self, query: str, params: tuple = None):
        """
        Execute a query on the DuckDB connection.
        :param query: the SQL query to execute.
        :param params: the params of a prepared statement.
        :return: the object with the result of the query execution.
        """
        if params is None:
            return self._conn.execute(query)
        return self._conn.execute(query, params)

    def close_connection(self):
        """
        Close the duckdb connection.
        """
        """
        :return: 
        """
        self._conn.close()
