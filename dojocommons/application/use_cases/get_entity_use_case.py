from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.ports.repository import Repository


class GetEntityUseCase[T: BaseEntity]:
    def __init__(self, repository: Repository[T]):
        self.repository = repository

    def execute(self, entity_id: str) -> T | None:
        return self.repository.find_by_id(entity_id)
