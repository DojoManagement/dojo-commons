import uuid
from http import HTTPMethod

import pytest

from dojocommons.infrastructure.repositories.duckdb_repository import (
    DuckDBRepository,
)
from dojocommons.interface_adapters.controllers.entity_controller import (
    EntityController,
)
from dojocommons.interface_adapters.dtos.base_event import BaseEvent
from tests.fakes import FakeEntity


@pytest.fixture
def event():
    return BaseEvent(
        http_method=HTTPMethod.GET,  # type: ignore[call-arg]
        resource="/entities/{id}",
        path_parameters=None,  # type: ignore[call-arg]
        query_parameters=None,  # type: ignore[call-arg]G
        body=None,
    )  # type: ignore[arg-type]


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


@pytest.fixture
def use_cases(mocker):
    return {
        "list": mocker.Mock(),
        "get": mocker.Mock(),
        "delete": mocker.Mock(),
        "update": mocker.Mock(),
        "create": mocker.Mock(),
    }


@pytest.fixture
def controller(use_cases):
    return EntityController(
        list_use_case=use_cases["list"],
        get_use_case=use_cases["get"],
        delete_use_case=use_cases["delete"],
        update_use_case=use_cases["update"],
        create_use_case=use_cases["create"],
    )
