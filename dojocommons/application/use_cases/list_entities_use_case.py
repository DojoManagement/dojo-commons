from typing import Any

from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.ports.repository import Repository


class ListEntitiesUseCase[T: BaseEntity]:
    def __init__(self, repository: Repository[T]):
        self._repository = repository

    def execute(self, filters: dict[str, Any] | None = None) -> list[T]:
        """Lista todas as entidades do tipo T"""
        if filters is None:
            filters = {}
        return self._repository.find_all(**filters)
