from http import HTTPStatus
from typing import TYPE_CHECKING

from dojocommons.interface_adapters.dtos.base_event import BaseEvent
from dojocommons.interface_adapters.dtos.response import Response
from dojocommons.interface_adapters.presenters.base import EntityPresenter

if TYPE_CHECKING:
    from collections.abc import Callable
    from http import HTTPMethod


class BaseController:
    def __init__(self, presenter: EntityPresenter):
        self._routes: dict[HTTPMethod, Callable[[BaseEvent], Response]] = {}
        self._presenter = presenter

    def dispatch(self, event: BaseEvent) -> Response:
        handler = self._routes.get(event.http_method)
        if handler is None:
            response: Response = self._presenter.present_error(
                code=HTTPStatus.METHOD_NOT_ALLOWED,
                message="Método não permitido",
            )
        else:
            response: Response = handler(event)

        return response
