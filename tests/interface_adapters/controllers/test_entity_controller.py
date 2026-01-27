from http import HTTPMethod

from dojocommons.domain.entities.base_entity import BaseEntity


def test_get_list(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.GET
    event.resource = "/entities"
    event.query_parameters = {"nome": "Rodrigo"}

    use_cases["list"].execute.return_value = ["ent1", "ent2"]

    response = controller.dispatch(event)

    use_cases["list"].execute.assert_called_once_with({"nome": "Rodrigo"})
    presenter.present.assert_called_once_with(["ent1", "ent2"])
    assert response == presenter.present.return_value


def test_get_by_id(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.GET
    event.path_parameters = {"id": "123"}
    entity = BaseEntity(id="123")

    use_cases["get"].execute.return_value = entity

    response = controller.dispatch(event)

    use_cases["get"].execute.assert_called_once_with("123")

    presenter.present.assert_called_once_with(entity)
    assert response == presenter.present.return_value


def test_get_by_id_not_found(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.GET
    event.path_parameters = {"id": "999"}

    use_cases["get"].execute.return_value = None

    response = controller.dispatch(event)

    presenter.present_error.assert_called_once_with(
        code=404, message="ID 999 não encontrado."
    )
    assert response == presenter.present_error.return_value


def test_post_create(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.POST
    event.body = {"nome": "Rodrigo"}

    use_cases["create"].execute.return_value = {"id": "1", "nome": "Rodrigo"}

    response = controller.dispatch(event)

    use_cases["create"].execute.assert_called_once_with(event)
    presenter.present.assert_called_once_with(
        {"id": "1", "nome": "Rodrigo"}, code=201
    )
    assert response == presenter.present.return_value


def test_post_missing_body(controller, event, presenter):
    event.http_method = HTTPMethod.POST
    event.body = None

    response = controller.dispatch(event)

    presenter.present_error.assert_called_once_with(
        code=400,
        message=f"Corpo da requisição é obrigatório para {event.resource}.",
    )
    assert response == presenter.present_error.return_value


def test_put_update(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.PUT
    event.path_parameters = {"id": "123"}
    event.body = '{"nome": "Novo"}'

    use_cases["update"].execute.return_value = {"id": "123", "nome": "Novo"}

    response = controller.dispatch(event)

    use_cases["update"].execute.assert_called_once()
    presenter.present.assert_called_once_with({"id": "123", "nome": "Novo"})
    assert response == presenter.present.return_value


def test_put_not_found(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.PUT
    event.path_parameters = {"id": "999"}
    event.body = '{"nome": "Novo"}'

    use_cases["update"].execute.return_value = None

    response = controller.dispatch(event)
    presenter.present_error.assert_called_once_with(
        code=404, message="ID 999 não encontrado."
    )
    assert response == presenter.present_error.return_value


def test_put_missing_id(controller, event, presenter):
    event.http_method = HTTPMethod.PUT
    event.path_parameters = None
    event.body = '{"nome": "Novo"}'

    response = controller.dispatch(event)

    presenter.present_error.assert_called_once_with(
        code=400,
        message=f"ID é obrigatório para {event.resource}.",
    )
    assert response == presenter.present_error.return_value


def test_delete(controller, use_cases, event, presenter):
    event.http_method = HTTPMethod.DELETE
    event.path_parameters = {"id": "123"}

    response = controller.dispatch(event)

    use_cases["delete"].execute.assert_called_once_with("123")
    presenter.present.assert_called_once_with(None, code=204)
    assert response == presenter.present.return_value


def test_delete_missing_id(controller, event, presenter):
    event.http_method = HTTPMethod.DELETE
    event.path_parameters = None

    response = controller.dispatch(event)

    presenter.present_error.assert_called_once_with(
        code=400,
        message=f"ID é obrigatório para {event.resource}.",
    )
    assert response == presenter.present_error.return_value


def test_unknown_http_method(controller, event, presenter):
    event.http_method = "PATCH"  # tipo inválido

    response = controller.dispatch(event)

    presenter.present_error.assert_called_once_with(
        code=405, message="Método não permitido"
    )
    assert response == presenter.present_error.return_value
