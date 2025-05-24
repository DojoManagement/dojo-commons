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
            self._conn.execute("SET s3_access_key_id=?;",
                               (self._app_cfg.aws_access_key_id,))
            self._conn.execute("SET s3_secret_access_key=?;",
                               (self._app_cfg.aws_secret_access_key,))
            self._conn.execute("SET s3_url_style='path';")
            self._conn.execute("SET s3_use_ssl=false;")
            self._conn.execute("SET s3_endpoint=?;",
                               (self._app_cfg.aws_endpoint,))

    def create_table_from_parquet(self, table_name: str):
        """
        Cria uma tabela no DuckDB a partir de um arquivo Parquet armazenado
            no S3.
        :param table_name: Nome da tabela a ser criada.
        :return: Resultado da execução da consulta.
        """
        query = (
            "CREATE TABLE IF NOT EXISTS ? AS SELECT * "
            "FROM read_parquet(?);"
        )
        file_path = f"{self._app_cfg.s3_file_path}/{table_name}.parquet"
        return self.execute_query(query, (table_name, file_path))

    def persist_data(self, table_name: str):
        """
        Persiste dados de uma tabela DuckDB para um arquivo Parquet no S3.
        :param table_name: Nome da tabela a ser persistida.
        :return: Resultado da execução da consulta.
        """
        query = "COPY ? TO ? (FORMAT PARQUET, COMPRESSION ZSTD)"
        file_path = f"{self._app_cfg.s3_file_path}/{table_name}.parquet"
        return self.execute_query(query, (table_name, file_path))

    def execute_query(self, query: str, params: tuple = None):
        """
        Executa uma consulta na conexão DuckDB.
        :param query: Consulta SQL a ser executada.
        :param params: Parâmetros para uma instrução preparada.
        :return: Resultado da execução da consulta.
        """
        if params is None:
            return self._conn.execute(query)
        return self._conn.execute(query, params)

    def close_connection(self):
        """
        Fecha a conexão com o DuckDB.
        """
        self._conn.close()
