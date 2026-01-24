from dojocommons.application.use_cases.get_entity_use_case import (
    GetEntityUseCase,
)
from tests.conftest import FakeEntity


def test_get_entity_use_case(mocker):
    repository_mock = mocker.Mock()
    entity_id = "123e4567-e89b-12d3-a456-426614174000"
    entity = FakeEntity(id=entity_id, name="Test Entity")

    repository_mock.find_by_id.return_value = entity

    use_case = GetEntityUseCase(repository=repository_mock)

    result = use_case.execute(entity_id)

    repository_mock.find_by_id.assert_called_once_with(entity_id)
    assert result == entity
    assert result is entity


def test_get_entity_use_case_not_found(mocker):
    repository_mock = mocker.Mock()
    entity_id = "non-existent-id"

    repository_mock.find_by_id.return_value = None

    use_case = GetEntityUseCase(repository=repository_mock)

    result = use_case.execute(entity_id)

    repository_mock.find_by_id.assert_called_once_with(entity_id)
    assert result is None
