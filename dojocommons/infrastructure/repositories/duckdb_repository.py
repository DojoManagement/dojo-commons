import re
from collections.abc import Iterable
from typing import Any

import duckdb

from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.ports.repository import Repository
from dojocommons.infrastructure.persistence.duckdb_service import DuckDbService
from dojocommons.interface_adapters.mappers.model_util import ModelUtil

_COLUMN_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_TABLE_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class DuckDBRepository[T: BaseEntity](Repository[T]):
    def __init__(
        self,
        db: DuckDbService,
        model_class: type[T],
        table_name: str,
        parquet_path: str,
    ):
        self._db = db
        self._model_class = model_class
        self._table_name = table_name
        self._parquet_path = parquet_path

        self._validate_table_name()
        self._ensure_table_exists()

    def _validate_table_name(self) -> None:
        if not _TABLE_PATTERN.match(self._table_name):
            msg = f"Nome de tabela inválido: {self._table_name}"
            raise ValueError(msg)

    def _ensure_table_exists(self) -> None:
        try:
            self._create_table_from_parquet()
        except (duckdb.IOException, duckdb.CatalogException):
            self._create_table_from_model()

    def _create_table_from_parquet(self) -> None:
        file_path = f"{self._parquet_path}/{self._table_name}.parquet"
        query = (
            "CREATE TABLE IF NOT EXISTS "  # noqa: S608
            f"{self._table_name} AS SELECT * "
            f"FROM read_parquet('{file_path}');"
        )
        self._db.execute(query)

    def _create_table_from_model(self) -> None:
        sql = ModelUtil.generate_create_table_sql(self._model_class)
        self._db.execute(sql)

    def save_to_parquet(self) -> None:
        file_path = f"{self._parquet_path}/{self._table_name}.parquet"
        query = f"COPY {self._table_name} TO '{file_path}'"
        query += " (FORMAT PARQUET, COMPRESSION ZSTD)"
        self._db.execute(query)

    def create(self, entity: T) -> T:
        if self.exists_by_id(entity.id):
            msg = f"Entidade com id {entity.id} já existe."
            raise ValueError(msg)

        data = entity.model_dump(exclude_none=True)
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())

        query = (
            f"INSERT INTO {self._table_name} ({fields}) "  # noqa: S608
            f"VALUES ({placeholders});"
        )
        self._db.execute(query, values)
        return entity

    def find_by_id(self, entity_id: str) -> T | None:
        query = (
            f"SELECT * FROM {self._table_name} "  # noqa: S608
            "WHERE id = ? LIMIT 1;"
        )
        cursor = self._db.execute(query, (entity_id,))
        row = cursor.fetchone()

        if not row or cursor.description is None:
            return None

        column_names = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(column_names, row, strict=False))

        return self._model_class.model_validate(row_dict)

    def find_all(self, order_by: str | None = None, **filters) -> list[T]:
        query = f"SELECT * FROM {self._table_name}"  # noqa: S608
        values = None

        if filters:
            self._validate_column_names(filters.keys())

            where = " AND ".join([f"{key} = ?" for key in filters])
            query += " WHERE " + where
            values = tuple(filters.values())

        if order_by:
            query += " ORDER BY " + order_by

        if values is not None:
            cursor = self._db.execute(query, values)
        else:
            cursor = self._db.execute(query)

        rows = cursor.fetchall()
        if cursor.description is None:
            return []

        column_names = [desc[0] for desc in cursor.description]
        return [
            self._model_class.model_validate(
                dict(zip(column_names, row, strict=False))
            )
            for row in rows
        ]

    def _validate_column_names(self, column_names: Iterable[str]) -> None:
        for column in column_names:
            if not _COLUMN_PATTERN.match(column):
                msg = f"Nome de coluna inválido: {column}"
                raise ValueError(msg)

    def update(self, entity_id: str, updates: dict[str, Any]) -> T | None:
        filtered = {k: v for k, v in updates.items() if v is not None}
        if not filtered:
            return self.find_by_id(entity_id)

        set_clauses = ", ".join([f"{key} = ?" for key in filtered])
        values = (*tuple(filtered.values()), entity_id)
        query = (
            f"UPDATE {self._table_name} SET {set_clauses} "  # noqa: S608
            "WHERE id = ?;"
        )
        self._db.execute(query, values)
        return self.find_by_id(entity_id)

    def delete(self, entity_id: str) -> None:
        query = f"DELETE FROM {self._table_name} WHERE id = ?;"  # noqa: S608
        self._db.execute(query, (entity_id,))

    def exists_by_id(self, entity_id: str) -> bool:
        query = (
            "SELECT EXISTS(SELECT 1 FROM "  # noqa: S608
            f"{self._table_name} WHERE id = ?)"
        )

        result = self._db.execute(query, (entity_id,)).fetchone()
        return bool(result[0])
