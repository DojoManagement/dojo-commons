# tests/test_model_util.py
import datetime
from typing import Optional

from dojocommons.interface_adapters.mappers.model_util import ModelUtil
from tests.fakes import FakeModel


def test_pydantic_type_to_sql_basic_types():
    assert ModelUtil.pydantic_type_to_sql(int) == "INTEGER"
    assert ModelUtil.pydantic_type_to_sql(float) == "REAL"
    assert ModelUtil.pydantic_type_to_sql(str) == "TEXT"
    assert ModelUtil.pydantic_type_to_sql(bool) == "BOOLEAN"
    assert ModelUtil.pydantic_type_to_sql(list) == "ARRAY"
    assert ModelUtil.pydantic_type_to_sql(dict) == "JSONB"
    assert ModelUtil.pydantic_type_to_sql(datetime.date) == "DATE"
    assert ModelUtil.pydantic_type_to_sql(datetime.datetime) == "TIMESTAMP"


def test_pydantic_type_to_sql_optional():
    assert (
        ModelUtil.pydantic_type_to_sql(
            Optional[int]  # type: ignore[arg-type]  # noqa: UP045
        )
        == "INTEGER"
    )
    assert (
        ModelUtil.pydantic_type_to_sql(
            Optional[str]  # type: ignore[arg-type]  # noqa: UP045
        )
        == "TEXT"
    )


def test_pydantic_type_to_sql_unknown_type():
    class Custom: ...

    assert ModelUtil.pydantic_type_to_sql(Custom) == "TEXT"


def test_generate_create_table_sql_default_name():
    sql = ModelUtil.generate_create_table_sql(FakeModel)

    assert "CREATE TABLE fakemodel" in sql
    assert "id TEXT NOT NULL PRIMARY KEY" in sql
    assert "nome TEXT NOT NULL" in sql
    assert "idade INTEGER NULL" in sql
    assert "ativo BOOLEAN NOT NULL" in sql
    assert "criado_em TIMESTAMP NOT NULL" in sql


def test_generate_create_table_sql_custom_name():
    sql = ModelUtil.generate_create_table_sql(FakeModel, table_name="usuarios")

    assert "CREATE TABLE usuarios" in sql


def test_generate_create_table_sql_field_order():
    sql = ModelUtil.generate_create_table_sql(FakeModel)

    # A ordem deve seguir a ordem declarada no modelo
    expected_order = [
        "id TEXT NOT NULL PRIMARY KEY",
        "nome TEXT NOT NULL",
        "idade INTEGER NULL",
        "ativo BOOLEAN NOT NULL",
        "criado_em TIMESTAMP NOT NULL",
    ]

    for index, expected in enumerate(expected_order):
        assert (
            expected in sql.splitlines()[index + 1]
        )  # +1 por causa da linha CREATE TABLE


def test_nullable_fields():
    sql = ModelUtil.generate_create_table_sql(FakeModel)

    assert "idade INTEGER NULL" in sql  # idade é Optional[int]
