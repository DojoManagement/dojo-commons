from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.ports.repository import Repository


class CreateEntityUseCase[T: BaseEntity]:
    def __init__(self, repository: Repository[T]):
        self._repository = repository

    def execute(self, entity: T) -> T:
        """Cria uma nova entidade do tipo T"""
        return self._repository.create(entity)
