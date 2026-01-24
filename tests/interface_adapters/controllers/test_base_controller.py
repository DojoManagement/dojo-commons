from http import HTTPMethod, HTTPStatus

from dojocommons.interface_adapters.controllers.base_controller import (
    BaseController,
)
from dojocommons.interface_adapters.dtos.base_event import BaseEvent
from dojocommons.interface_adapters.dtos.response import Response


class TestController(BaseController):
    def __init__(self):
        self._routes = {
            HTTPMethod.GET: self.handle_get,
        }

    def handle_get(self, _event: BaseEvent) -> Response:
        return Response(status_code=200, body="GET request handled")


def test_base_controller_with_no_routes():
    controller = BaseController()
    event = BaseEvent(
        resource="/test",
        http_method="GET",  # type: ignore[call-arg]
    )

    response = controller.dispatch(event)

    assert isinstance(response, Response)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert response.body == "Method Not Allowed"


def test_base_controller_with_registered_route():
    controller = TestController()
    event = BaseEvent(
        resource="/test",
        http_method="GET",  # type: ignore[call-arg]
    )

    response = controller.dispatch(event)

    assert isinstance(response, Response)
    assert response.status_code == HTTPStatus.OK
    assert response.body == "GET request handled"
