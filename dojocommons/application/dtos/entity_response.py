from abc import abstractmethod
from dataclasses import dataclass
from typing import Self

from dojocommons.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class EntityResponse[T: BaseEntity]:
    id: str

    @abstractmethod
    @classmethod
    def from_entity(cls, entity: T) -> Self: ...
