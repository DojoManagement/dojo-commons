from http import HTTPStatus

from dojocommons.interface_adapters.controllers.base_controller import (
    BaseController,
)
from dojocommons.interface_adapters.dtos.base_event import BaseEvent
from dojocommons.interface_adapters.dtos.response import Response
from tests.fakes import FakeTestController


def test_base_controller_with_no_routes(presenter):
    controller = BaseController(presenter)
    event = BaseEvent(
        resource="/test",
        http_method="GET",  # type: ignore[call-arg]
    )

    response = controller.dispatch(event)

    assert response == presenter.present_error.return_value
    presenter.present_error.assert_called_once_with(
        code=HTTPStatus.METHOD_NOT_ALLOWED,
        message="Método não permitido",
    )


def test_base_controller_with_registered_route():
    controller = FakeTestController()
    event = BaseEvent(
        resource="/test",
        http_method="GET",  # type: ignore[call-arg]
    )

    response = controller.dispatch(event)

    assert isinstance(response, Response)
    assert response.status_code == HTTPStatus.OK
    assert response.body == "GET request handled"
