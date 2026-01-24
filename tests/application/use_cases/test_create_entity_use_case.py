from dojocommons.application.use_cases.create_entity_use_case import (
    CreateEntityUseCase,
)
from tests.fakes import FakeEntity


def test_create_entity_use_case(mocker):
    repository_mock = mocker.Mock()
    entity = FakeEntity(name="Test Entity")

    repository_mock.create.return_value = entity

    use_case = CreateEntityUseCase(repository=repository_mock)

    result = use_case.execute(entity)

    repository_mock.create.assert_called_once_with(entity)
    assert result == entity
    assert result is entity
