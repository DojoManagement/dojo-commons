from http import HTTPStatus

from dojocommons.application.use_cases.update_entity_use_case import (
    UpdateEntityUseCase,
)
from dojocommons.domain.exceptions.business_exception import BusinessError
from tests.fakes import FakeEntity


def test_update_entity_use_case(mocker):
    repository_mock = mocker.Mock()
    entity_id = "123e4567-e89b-12d3-a456-426614174000"
    updated_entity = FakeEntity(id=entity_id, name="Updated Entity")

    repository_mock.update.return_value = updated_entity

    use_case = UpdateEntityUseCase(repository=repository_mock)

    result = use_case.execute(entity_id, updated_entity.model_dump())

    repository_mock.update.assert_called_once_with(
        entity_id, updated_entity.model_dump()
    )
    assert result == updated_entity
    assert result is updated_entity


def test_update_entity_use_case_entity_not_found(mocker):
    repository_mock = mocker.Mock()
    entity_id = "non-existent-id"

    repository_mock.find_by_id.return_value = None

    use_case = UpdateEntityUseCase(repository=repository_mock)

    try:
        use_case.execute(entity_id, {"name": "New Name"})
    except BusinessError as e:
        assert isinstance(e, BusinessError)
        assert str(e) == f"Entidade com ID {entity_id} não encontrada."
        assert e.status_code == HTTPStatus.NOT_FOUND


def test_update_entity_use_case_update_failure(mocker):
    repository_mock = mocker.Mock()
    entity_id = "123e4567-e89b-12d3-a456-426614174000"
    existing_entity = FakeEntity(id=entity_id, name="Existing Entity")

    repository_mock.find_by_id.return_value = existing_entity
    repository_mock.update.return_value = None

    use_case = UpdateEntityUseCase(repository=repository_mock)

    try:
        use_case.execute(entity_id, {"name": "New Name"})
    except BusinessError as e:
        assert isinstance(e, BusinessError)
        assert (
            str(e)
            == f"Não foi possível atualizar a entidade com ID {entity_id}."
        )
        assert e.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
