from dojocommons.application.use_cases.list_entities_use_case import (
    ListEntitiesUseCase,
)
from tests.fakes import FakeEntity


def test_list_entities_use_case(mocker):
    repository_mock = mocker.Mock()
    entity1 = FakeEntity(
        id="123e4567-e89b-12d3-a456-426614174000", name="Entity One"
    )
    entity2 = FakeEntity(
        id="123e4567-e89b-12d3-a456-426614174001", name="Entity Two"
    )
    entities = [entity1, entity2]

    repository_mock.find_all.return_value = entities

    use_case = ListEntitiesUseCase(repository=repository_mock)

    result = use_case.execute()

    repository_mock.find_all.assert_called_once()
    assert result == entities
    assert result is entities


def test_list_entities_use_case_with_filters(mocker):
    repository_mock = mocker.Mock()
    entity1 = FakeEntity(
        id="123e4567-e89b-12d3-a456-426614174002", name="Filtered Entity"
    )
    entities = [entity1]

    repository_mock.find_all.return_value = entities

    use_case = ListEntitiesUseCase(repository=repository_mock)

    filters = {"name": "Filtered Entity"}
    result = use_case.execute(filters=filters)

    repository_mock.find_all.assert_called_once_with(**filters)
    assert result == entities
    assert result is entities
