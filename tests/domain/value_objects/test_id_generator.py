from dojocommons.domain.value_objects.id_generator import IdGenerator


def test_generate_id(mocker, fixed_uuid):
    mocker.patch(
        "dojocommons.domain.value_objects.id_generator.uuid.uuid4",
        return_value=fixed_uuid,
    )

    generated_id = IdGenerator.generate()
    assert generated_id == str(fixed_uuid)


def test_is_valid_uuid():
    valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
    invalid_uuid = "invalid-uuid-string"

    assert IdGenerator.is_valid_uuid(valid_uuid) is True
    assert IdGenerator.is_valid_uuid(invalid_uuid) is False
