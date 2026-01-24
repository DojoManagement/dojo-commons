from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.ports.repository import Repository


class DeleteEntityUseCase[T: BaseEntity]:
    def __init__(self, repository: Repository[T]):
        self._repository = repository

    def execute(self, entity_id: str) -> None:
        """Deleta uma entidade do tipo T pelo seu ID"""
        self._repository.delete(entity_id)
