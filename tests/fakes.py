import datetime

from pydantic import BaseModel

from dojocommons.domain.entities.base_entity import BaseEntity


class FakeEntity(BaseEntity):
    name: str


class FakeModel(BaseModel):
    id: str
    nome: str
    idade: int | None = None
    ativo: bool
    criado_em: datetime.datetime
