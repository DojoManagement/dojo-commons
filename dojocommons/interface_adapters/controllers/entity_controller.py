from http import HTTPMethod

from dojocommons.application.use_cases.create_entity_use_case import (
    CreateEntityUseCase,
)
from dojocommons.application.use_cases.delete_entity_use_case import (
    DeleteEntityUseCase,
)
from dojocommons.application.use_cases.get_entity_use_case import (
    GetEntityUseCase,
)
from dojocommons.application.use_cases.list_entities_use_case import (
    ListEntitiesUseCase,
)
from dojocommons.application.use_cases.update_entity_use_case import (
    UpdateEntityUseCase,
)
from dojocommons.interface_adapters.controllers.base_controller import (
    BaseController,
)
from dojocommons.interface_adapters.dtos.base_event import BaseEvent
from dojocommons.interface_adapters.dtos.response import Response


class EntityController(BaseController):
    def __init__(
        self,
        list_use_case: ListEntitiesUseCase,
        get_use_case: GetEntityUseCase,
        delete_use_case: DeleteEntityUseCase,
        update_use_case: UpdateEntityUseCase,
        create_use_case: CreateEntityUseCase,
    ):
        super().__init__()
        self._list_use_case = list_use_case
        self._get_use_case = get_use_case
        self._delete_use_case = delete_use_case
        self._update_use_case = update_use_case
        self._create_use_case = create_use_case

        self._routes = {
            HTTPMethod.GET: self._handle_get,
            HTTPMethod.POST: self._handle_post,
            HTTPMethod.PUT: self._handle_put,
            HTTPMethod.DELETE: self._handle_delete,
        }

    def _handle_get(self, event: BaseEvent) -> Response:
        if (
            self._resource_has_id(event)
            and event.path_parameters
            and "id" in event.path_parameters
        ):
            return self._handle_get_by_id(event)
        return self._handle_list(event)

    def _handle_get_by_id(self, event: BaseEvent) -> Response:
        if missing := self._require_id(event):
            return missing

        entity_id = event.path_parameters["id"]  # type: ignore[arg-type]
        entity = self._get_use_case.execute(entity_id)
        if entity is None:
            return Response(
                status_code=404,
                body=f"ID {entity_id} não encontrado.",
            )
        return Response(status_code=200, body=entity)

    def _handle_list(self, event: BaseEvent) -> Response:
        filters = event.query_parameters or {}
        entities = self._list_use_case.execute(filters)
        return Response(status_code=200, body=entities)

    def _handle_post(self, event: BaseEvent) -> Response:
        if missing := self._require_body(event):
            return missing

        result = self._create_use_case.execute(event)
        return Response(status_code=201, body=result)

    def _handle_put(self, event: BaseEvent) -> Response:
        if missing := self._require_id(event):
            return missing
        if missing := self._require_body(event):
            return missing

        entity_id = event.path_parameters["id"]  # type: ignore[arg-type]
        dto = event.model_dump()
        result = self._update_use_case.execute(entity_id, dto)
        if result is None:
            return Response(
                status_code=404,
                body=f"ID {entity_id} não encontrado.",
            )
        return Response(status_code=200, body=result)

    def _handle_delete(self, event: BaseEvent) -> Response:
        if missing := self._require_id(event):
            return missing

        entity_id = event.path_parameters["id"]  # type: ignore[arg-type]
        self._delete_use_case.execute(entity_id)
        return Response(status_code=204, body=None)

    def _require_id(self, event: BaseEvent) -> Response | None:
        if not event.path_parameters or "id" not in event.path_parameters:
            return Response(
                status_code=400,
                body=f"ID é obrigatório para {event.resource}.",
            )
        return None

    def _require_body(self, event: BaseEvent) -> Response | None:
        if event.body is None:
            msg = (
                "Corpo da requisição é obrigatório para {self._resource_name}."
            )
            return Response(status_code=400, body=msg)
        return None

    def _resource_has_id(self, event: BaseEvent) -> bool:
        return "{id}" in event.resource
