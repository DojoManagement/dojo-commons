from typing import TYPE_CHECKING

from dojocommons.domain.entities.base_event import BaseEvent
from dojocommons.domain.entities.response import Response

if TYPE_CHECKING:
    from collections.abc import Callable
    from http import HTTPMethod


class BaseController:
    def __init__(self):
        self._routes: dict[HTTPMethod, Callable[[BaseEvent], Response]] = {}

    def dispatch(self, event: BaseEvent) -> Response:
        handler = self._routes.get(event.http_method)
        if handler is None:
            return Response(status_code=405, body="Method Not Allowed")
        return handler(event)
