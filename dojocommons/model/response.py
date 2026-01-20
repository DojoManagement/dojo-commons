from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Response(BaseModel):
    status_code: int
    headers: dict[str, str] | None = None
    body: Any | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
