from pydantic import BaseModel, Field

from dojocommons.domain.value_objects.id_generator import IdGenerator


class BaseEntity(BaseModel):
    """Modelo completo com ID"""

    id: str = Field(
        default_factory=lambda: IdGenerator.generate(),
        description="UUID único (gerado automaticamente)",
    )

    model_config = {
        "from_attributes": True,
    }
