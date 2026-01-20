import os

import duckdb
from pydantic import BaseModel

from dojocommons.log.logging import logger
from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.util.model_util import ModelUtil


class DbService:
    def __init__(self, app_cfg: AppConfiguration):
        self._app_cfg = app_cfg
        self._conn = duckdb.connect()
        self._init_duckdb()
        logger.debug(
            "DuckDB connection initialized.",
            bucket=self._app_cfg.s3_bucket,
            path=self._app_cfg.s3_path,
            aws_endpoint=self._app_cfg.aws_endpoint,
        )

    def __del__(self):
        self.close_connection()

    def _init_duckdb(self):
        logger.debug("Initializing DuckDB with S3 configuration.")

        self._conn.execute("SET home_directory='/tmp'")
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")

        # Configuração para LocalStack (desenvolvimento)
        if self._app_cfg.aws_endpoint is not None:
            logger.debug("Configurando DuckDB para LocalStack.")
            self._conn.execute("SET s3_access_key_id='test';")
            self._conn.execute("SET s3_secret_access_key='test';")
            self._conn.execute("SET s3_region='us-east-1';")
            self._conn.execute("SET s3_url_style='path';")
            self._conn.execute("SET s3_use_ssl=false;")
            self._conn.execute(
                "SET s3_endpoint=?;", (self._app_cfg.aws_endpoint,)
            )
            logger.debug(
                "LocalStack endpoint configurado.",
                endpoint=self._app_cfg.aws_endpoint,
            )
        else:
            # Configuração para AWS real (produção) -
            # usa credenciais da IAM Role
            logger.debug("Configurando para AWS (usando IAM Role)")

            # Log informações do Lambda
            lambda_function = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "N/A")
            lambda_role_arn = os.environ.get("AWS_EXECUTION_ENV", "N/A")
            logger.debug(
                "Lambda Function",
                function=lambda_function,
                role_arn=lambda_role_arn,
            )

            region = self._app_cfg.aws_region or "sa-east-1"
            self._conn.execute("SET s3_region=?;", (region,))
            self._conn.execute("SET s3_url_style='path';")
            regional_endpoint = f"s3.{region}.amazonaws.com"
            self._conn.execute("SET s3_endpoint=?;", (regional_endpoint,))
            self._conn.execute("SET s3_use_ssl=true;")
            self._conn.execute("SET s3_url_compatibility_mode=true;")

            logger.debug(
                "AWS endpoint configurado.",
                region=region,
                endpoint=regional_endpoint,
            )

        # Testa a configuração
        try:
            result = self._conn.execute(
                "SELECT current_setting('s3_endpoint');"
            ).fetchone()
            logger.debug("Endpoint S3 atual verificado.", s3_endpoint=result)
        except duckdb.IOException as e:
            logger.exception("Erro ao verificar endpoint S3.", error=str(e))

    def create_table(
        self, class_type: type[BaseModel], table_name: str | None = None
    ):
        """
        Cria uma tabela DuckDB a partir de um modelo Pydantic.
        :param class_type: Modelo Pydantic que define a estrutura da tabela.
        :param table_name: Nome da tabela a ser criada.
        Se não fornecido, usa o nome da classe.
        :return: Resultado da execução da consulta.
        """
        if table_name is None:
            table_name = class_type.__name__.lower()

        try:
            self.create_table_from_parquet(table_name)
        except duckdb.IOException:
            self.create_table_from_model(class_type)

    def create_table_from_model(self, class_type: type[BaseModel]):
        """
        Cria uma tabela DuckDB a partir de um modelo Pydantic.
        :param class_type: Modelo Pydantic que define a estrutura da tabela.
        :return: Resultado da execução da consulta.
        """
        query = ModelUtil.generate_create_table_sql(class_type)
        self.execute_query(query)

    def create_table_from_parquet(self, table_name: str):
        """
        Cria uma tabela no DuckDB a partir de um arquivo Parquet armazenado
            no S3.
        :param table_name: Nome da tabela a ser criada.
        :return: Resultado da execução da consulta.
        """
        file_path = f"{self._app_cfg.s3_file_path}/{table_name}.parquet"
        query = (
            "CREATE TABLE IF NOT EXISTS "  # noqa: S608
            f"{table_name} AS SELECT * "
            f"FROM read_parquet('{file_path}');"
        )
        self.execute_query(query)

    def persist_data(self, table_name: str):
        """
        Persiste dados de uma tabela DuckDB para um arquivo Parquet no S3.
        :param table_name: Nome da tabela a ser persistida.
        :return: Resultado da execução da consulta.
        """
        file_path = f"{self._app_cfg.s3_file_path}/{table_name}.parquet"
        query = f"COPY {table_name} TO '{file_path}'"
        query += " (FORMAT PARQUET, COMPRESSION ZSTD)"

        logger.debug(
            "Persisting data to Parquet.",
            table=table_name,
            path=file_path,
            query=query,
        )
        return self.execute_query(query)

    def execute_query(self, query: str, params: tuple | None = None):
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
