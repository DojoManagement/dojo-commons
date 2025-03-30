from typing import Optional

from pydantic import BaseModel, Field


class Response(BaseModel):
    status_code: int = Field(alias="statusCode")
    body: Optional[str]

    class Config:
        populate_by_name = True
