from dojocommons.application.use_cases.delete_entity_use_case import (
    DeleteEntityUseCase,
)


def test_delete_entity_use_case(mocker):
    repository_mock = mocker.Mock()
    entity_id = "123e4567-e89b-12d3-a456-426614174000"

    use_case = DeleteEntityUseCase(repository=repository_mock)

    use_case.execute(entity_id)

    repository_mock.delete.assert_called_once_with(entity_id)
