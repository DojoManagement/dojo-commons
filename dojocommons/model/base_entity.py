from pydantic import BaseModel, Field

from dojocommons.util.id_generator import IdGenerator


class BaseEntity(BaseModel):
    """Modelo completo com ID"""

    id: str = Field(
        default_factory=IdGenerator.generate,
        description="UUID único (gerado automaticamente)",
    )

    class Config:
        from_attributes = True
