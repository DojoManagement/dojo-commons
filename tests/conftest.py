import uuid

import pytest

from dojocommons.infrastructure.repositories.duckdb_repository import (
    DuckDBRepository,
)
from tests.fakes import FakeEntity


@pytest.fixture
def fixed_uuid():
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def db_mock(mocker):
    return mocker.Mock()


@pytest.fixture
def repo(db_mock, tmp_path):
    return DuckDBRepository(
        db=db_mock,
        model_class=FakeEntity,
        table_name="fake_table",
        parquet_path=str(tmp_path),
    )
