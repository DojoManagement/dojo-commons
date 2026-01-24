from dojocommons.domain.entities.base_entity import BaseEntity
from dojocommons.domain.value_objects.id_generator import IdGenerator


def test_base_entity_creation_no_id(mocker, fixed_uuid):
    mocker.patch.object(IdGenerator, "generate", return_value=str(fixed_uuid))
    entity = BaseEntity()
    assert entity.id == str(fixed_uuid)


def test_base_entity_creation_with_id(fixed_uuid):
    entity = BaseEntity(id=str(fixed_uuid))
    assert entity.id == str(fixed_uuid)
