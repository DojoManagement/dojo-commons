from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.exceptions.business_exception import BusinessError
from dojocommons.domain.ports.repository import Repository


class UpdateEntityUseCase[T: BaseEntity]:
    def __init__(self, repository: Repository[T]):
        self.repository = repository

    def execute(self, entity_id: str, updates: dict) -> T:
        entity = self.repository.find_by_id(entity_id)
        if not entity:
            msg = f"Entidade com ID {entity_id} não encontrada."
            raise BusinessError(msg, status_code=404)

        updated_entity = self.repository.update(entity_id, updates)
        if not updated_entity:
            msg = f"Não foi possível atualizar a entidade com ID {entity_id}."
            raise BusinessError(msg, status_code=500)

        return updated_entity
