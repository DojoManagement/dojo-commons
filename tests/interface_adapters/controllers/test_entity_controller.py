from http import HTTPMethod, HTTPStatus


def test_get_list(controller, use_cases, event):
    event.http_method = HTTPMethod.GET
    event.resource = "/entities"
    event.query_parameters = {"nome": "Rodrigo"}

    use_cases["list"].execute.return_value = ["ent1", "ent2"]

    response = controller.dispatch(event)

    use_cases["list"].execute.assert_called_once_with({"nome": "Rodrigo"})
    assert response.status_code == HTTPStatus.OK
    assert response.body == ["ent1", "ent2"]


def test_get_by_id(controller, use_cases, event):
    event.http_method = HTTPMethod.GET
    event.path_parameters = {"id": "123"}

    use_cases["get"].execute.return_value = {"id": "123"}

    response = controller.dispatch(event)

    use_cases["get"].execute.assert_called_once_with("123")
    assert response.status_code == HTTPStatus.OK
    assert response.body == {"id": "123"}


def test_get_by_id_not_found(controller, use_cases, event):
    event.http_method = HTTPMethod.GET
    event.path_parameters = {"id": "999"}

    use_cases["get"].execute.return_value = None

    response = controller.dispatch(event)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "999" in response.body


def test_post_create(controller, use_cases, event):
    event.http_method = HTTPMethod.POST
    event.body = {"nome": "Rodrigo"}

    use_cases["create"].execute.return_value = {"id": "1", "nome": "Rodrigo"}

    response = controller.dispatch(event)

    use_cases["create"].execute.assert_called_once_with(event)
    assert response.status_code == HTTPStatus.CREATED
    assert response.body["nome"] == "Rodrigo"


def test_post_missing_body(controller, event):
    event.http_method = HTTPMethod.POST
    event.body = None

    response = controller.dispatch(event)

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_put_update(controller, use_cases, event):
    event.http_method = HTTPMethod.PUT
    event.path_parameters = {"id": "123"}
    event.body = {"nome": "Novo"}

    use_cases["update"].execute.return_value = {"id": "123", "nome": "Novo"}

    response = controller.dispatch(event)

    use_cases["update"].execute.assert_called_once()
    assert response.status_code == HTTPStatus.OK
    assert response.body["nome"] == "Novo"


def test_put_not_found(controller, use_cases, event):
    event.http_method = HTTPMethod.PUT
    event.path_parameters = {"id": "999"}
    event.body = '{"nome": "Novo"}'

    use_cases["update"].execute.return_value = None

    response = controller.dispatch(event)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_put_missing_id(controller, event):
    event.http_method = HTTPMethod.PUT
    event.path_parameters = None
    event.body = '{"nome": "Novo"}'

    response = controller.dispatch(event)

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete(controller, use_cases, event):
    event.http_method = HTTPMethod.DELETE
    event.path_parameters = {"id": "123"}

    response = controller.dispatch(event)

    use_cases["delete"].execute.assert_called_once_with("123")
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.body is None


def test_delete_missing_id(controller, event):
    event.http_method = HTTPMethod.DELETE
    event.path_parameters = None

    response = controller.dispatch(event)

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_unknown_http_method(controller, event):
    event.http_method = "PATCH"  # tipo inválido

    response = controller.dispatch(event)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
