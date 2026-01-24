import duckdb
import pytest

from dojocommons.infrastructure.repositories.duckdb_repository import (
    DuckDBRepository,
)
from tests.fakes import FakeEntity


def test_invalid_table_name_raises(db_mock, tmp_path):
    with pytest.raises(ValueError):
        DuckDBRepository(
            db=db_mock,
            model_class=FakeEntity,
            table_name="123-invalid",
            parquet_path=str(tmp_path),
        )


def test_create_table_from_parquet(repo, db_mock):
    repo._create_table_from_parquet()

    expected_query = (
        "CREATE TABLE IF NOT EXISTS fake_table AS SELECT * "
        f"FROM read_parquet('{repo._parquet_path}/fake_table.parquet');"
    )

    db_mock.execute.assert_called_with(expected_query)


def test_ensure_table_falls_back_to_model(mocker, db_mock, tmp_path):
    mocker.patch.object(
        db_mock, "execute", side_effect=[duckdb.IOException("fail"), None]
    )

    mocker.patch(
        "dojocommons.interface_adapters.mappers.model_util.ModelUtil.generate_create_table_sql",
        return_value="CREATE TABLE fake_table (id VARCHAR)",
    )

    _ = DuckDBRepository(
        db=db_mock,
        model_class=FakeEntity,
        table_name="fake_table",
        parquet_path=str(tmp_path),
    )

    # primeira chamada falha (parquet), segunda é create_table_from_model
    assert db_mock.execute.call_count == 2  # noqa: PLR2004


def test_save_to_parquet(repo, db_mock):
    repo.save_to_parquet()

    expected_query = (
        f"COPY fake_table TO '{repo._parquet_path}/fake_table.parquet'"
        " (FORMAT PARQUET, COMPRESSION ZSTD)"
    )

    db_mock.execute.assert_called_with(expected_query)


def test_create_inserts_entity(repo, db_mock):
    entity = FakeEntity(id="1", name="Rodrigo")

    # exists_by_id deve retornar False
    db_mock.execute.return_value.fetchone.return_value = (0,)

    result = repo.create(entity)

    assert result == entity

    db_mock.execute.assert_called_with(
        "INSERT INTO fake_table (id, name) VALUES (?, ?);", ("1", "Rodrigo")
    )


def test_create_raises_if_exists(repo, db_mock):
    entity = FakeEntity(id="1", name="Rodrigo")

    # exists_by_id retorna True
    db_mock.execute.return_value.fetchone.return_value = (1,)

    with pytest.raises(ValueError):
        repo.create(entity)


def test_find_by_id_returns_entity(repo, db_mock):
    db_mock.execute.return_value.fetchone.return_value = ("1", "Rodrigo")
    db_mock.execute.return_value.description = [("id",), ("name",)]

    result = repo.find_by_id("1")

    assert isinstance(result, FakeEntity)
    assert result.id == "1"
    assert result.name == "Rodrigo"


def test_find_by_id_returns_none(repo, db_mock):
    db_mock.execute.return_value.fetchone.return_value = None
    db_mock.execute.return_value.description = None

    assert repo.find_by_id("1") is None


def test_find_all_no_filters(repo, db_mock):
    db_mock.execute.return_value.fetchall.return_value = [
        ("1", "Rodrigo"),
        ("2", "Maria"),
    ]
    db_mock.execute.return_value.description = [("id",), ("name",)]

    result = repo.find_all()

    assert result == [
        FakeEntity(id="1", name="Rodrigo"),
        FakeEntity(id="2", name="Maria"),
    ]


def test_find_all_with_filters(repo, db_mock):
    # Arrange
    # Simula retorno do DuckDB
    db_mock.execute.return_value.fetchall.return_value = [
        ("1", "Rodrigo"),
        ("2", "Maria"),
    ]
    db_mock.execute.return_value.description = [("id",), ("name",)]

    # Act
    result = repo.find_all(name="Rodrigo")

    # Assert
    # Verifica se o SQL foi montado corretamente
    db_mock.execute.assert_called_with(
        "SELECT * FROM fake_table WHERE name = ?", ("Rodrigo",)
    )

    # Verifica se o retorno foi convertido em entidades
    assert len(result) == 2
    assert result[0].id == "1"
    assert result[0].name == "Rodrigo"


def test_find_all_invalid_column(repo):
    with pytest.raises(ValueError):
        repo.find_all(**{"invalid-column!": "x"})


def test_update(repo, db_mock):
    db_mock.execute.return_value.fetchone.return_value = ("1", "Novo Nome")
    db_mock.execute.return_value.description = [("id",), ("name",)]

    result = repo.update("1", {"name": "Novo Nome"})

    db_mock.execute.assert_any_call(
        "UPDATE fake_table SET name = ? WHERE id = ?;", ("Novo Nome", "1")
    )

    assert result.name == "Novo Nome"


def test_update_no_fields_calls_find_by_id(repo, mocker):
    mock_find = mocker.patch.object(repo, "find_by_id", return_value="ok")

    result = repo.update("1", {})

    mock_find.assert_called_once_with("1")
    assert result == "ok"


def test_delete(repo, db_mock):
    repo.delete("1")
    db_mock.execute.assert_called_with(
        "DELETE FROM fake_table WHERE id = ?;", ("1",)
    )


def test_exists_by_id(repo, db_mock):
    db_mock.execute.return_value.fetchone.return_value = (1,)
    assert repo.exists_by_id("1") is True

    db_mock.execute.return_value.fetchone.return_value = (0,)
    assert repo.exists_by_id("1") is False
