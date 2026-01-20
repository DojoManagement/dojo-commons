import http

from pydantic import BaseModel, Field, model_validator


class BaseEvent(BaseModel):
    resource: str
    http_method: http.HTTPMethod = Field(alias="httpMethod")
    headers: dict
    query_parameters: dict | None = Field(alias="queryStringParameters")
    path_parameters: dict | None = Field(alias="pathParameters")
    body: str | None

    class Config:
        populate_by_name = True

    @model_validator(mode="after")
    def validate_http_method(self):
        valid_methods = {
            http.HTTPMethod.GET,
            http.HTTPMethod.POST,
            http.HTTPMethod.PUT,
            http.HTTPMethod.DELETE,
        }
        if self.http_method not in valid_methods:
            msg = (
                f"Método HTTP '{self.http_method}' não é válido."
                "Apenas GET, POST, PUT ou DELETE são permitidos."
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_body(self):
        if (
            self.http_method
            in {
                http.HTTPMethod.POST,
                http.HTTPMethod.PUT,
            }
            and not self.body
        ):
            msg = (
                "Corpo da requisição é obrigatório para"
                " as operações POST e PUT."
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_path_parameters(self):
        if (
            self.http_method
            in {
                http.HTTPMethod.GET,
                http.HTTPMethod.PUT,
                http.HTTPMethod.DELETE,
            }
            and "id" in self.resource
            and (
                not self.path_parameters or not self.path_parameters.get("id")
            )
        ):
            msg = (
                "Parâmetro 'id' é obrigatório para as"
                " operações GET, PUT e DELETE."
            )
            raise ValueError(msg)
        return self
