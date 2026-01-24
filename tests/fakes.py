import datetime
from http import HTTPMethod

from pydantic import BaseModel

from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.interface_adapters.controllers.base_controller import (
    BaseController,
)
from dojocommons.interface_adapters.dtos.base_event import BaseEvent
from dojocommons.interface_adapters.dtos.response import Response


class FakeEntity(BaseEntity):
    name: str


class FakeModel(BaseModel):
    id: str
    nome: str
    idade: int | None = None
    ativo: bool
    criado_em: datetime.datetime


class FakeTestController(BaseController):
    def __init__(self):
        self._routes = {
            HTTPMethod.GET: self.handle_get,
        }

    def handle_get(self, _event: BaseEvent) -> Response:
        return Response(status_code=200, body="GET request handled")
