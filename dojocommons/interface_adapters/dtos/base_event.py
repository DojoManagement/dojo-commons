import http
from typing import Any

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    resource: str
    http_method: http.HTTPMethod = Field(alias="httpMethod")
    headers: dict[str, str] | None = None
    query_parameters: dict[str, Any] | None = Field(
        alias="queryStringParameters"
    )
    path_parameters: dict[str, Any] | None = Field(alias="pathParameters")
    body: str | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
