import json
from http import HTTPMethod
from typing import Callable, Dict, Generic, TypeVar, Type

from pydantic import BaseModel

from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.model.base_event import BaseEvent
from dojocommons.model.base_resource import BaseResource
from dojocommons.model.response import Response
from dojocommons.service.base_service import BaseService

# Define um TypeVar para o tipo genérico da entidade
T = TypeVar("T", bound=BaseModel)


# noinspection PyArgumentList,Annotator
class BaseController(Generic[T]):
    def __init__(
        self,
        cfg: AppConfiguration,
        service_class: Type[BaseService[T]],
        resource: BaseResource,
        model_class: Type[T],
    ):
        self._service = service_class(cfg)  # type: ignore
        self._resource = resource
        self._model_class = model_class

        # Tipagem explícita para o _strategy
        self._strategy: Dict[HTTPMethod, Callable[[BaseEvent], Response]] = {
            HTTPMethod.GET: self._get,
            HTTPMethod.POST: self._post,
            HTTPMethod.PUT: self._put,
            HTTPMethod.DELETE: self._delete,
        }

    def dispatch(self, event: BaseEvent):
        method = self._strategy.get(event.http_method)
        if not method:
            return Response(status_code=405, body="Method Not Allowed")
        return method(event)

    def _get(self, event: BaseEvent):
        if event.resource == self._resource:
            return self._list(event)
        elif event.resource == f"{self._resource}_ID":
            return self._get_by_id(event)

    def _list(self, _event: BaseEvent):
        entities = self._service.list_all()
        entity_list = {"items": [entity.model_dump() for entity in entities]}
        return Response(
            status_code=200,
            body=json.dumps(entity_list, ensure_ascii=False, default=str),
        )

    def _get_by_id(self, event: BaseEvent):
        entity_id = event.path_parameters.get("id")
        entity = self._service.get_by_id(int(entity_id))
        if not entity:
            return Response(status_code=404, body="Entity not found")
        body = f'{{"item": {entity.model_dump_json(exclude_none=True)}}}'
        return Response(status_code=200, body=body)

    def _post(self, event: BaseEvent):
        entity = self._model_class.model_validate_json(event.body)
        entity = self._service.create(entity)
        body = f'{{"item": {entity.model_dump_json(exclude_none=True)}}}'
        return Response(status_code=201, body=body)

    def _put(self, event: BaseEvent):
        entity_id = event.path_parameters.get("id")
        existing_entity = self._service.get_by_id(int(entity_id))

        if not existing_entity:
            return Response(status_code=404, body="Entity not found")

        updates = self._model_class.model_validate_json(event.body)
        updated_entity = self._service.update(updates)
        body = (
            f'{{"item": {updated_entity.model_dump_json(exclude_none=True)}}}'
        )
        return Response(status_code=200, body=body)

    def _delete(self, event: BaseEvent):
        entity_id = event.path_parameters.get("id")
        self._service.delete(int(entity_id))
        return Response(status_code=204, body=None)
