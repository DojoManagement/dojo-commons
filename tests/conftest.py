import uuid

import pytest

from dojocommons.domain.entities.base_entity import BaseEntity


class FakeEntity(BaseEntity):
    name: str


@pytest.fixture
def fixed_uuid():
    return uuid.UUID("12345678-1234-5678-1234-567812345678")
