from typing import Any

from dojocommons.interface_adapters.dtos.response import Response
from dojocommons.interface_adapters.http.cors_helper import CORSHelper


class EntityPresenter:
    def present(
        self,
        body: dict[str, str] | list[dict[str, str]] | None,
        code: int = 200,
    ) -> Response:
        response_body = None if body is None else {"data": body}
        return self._build_response(code, response_body)

    def present_error(self, code: int, message: str) -> Response:
        return self._build_response(
            code, {"error": {"message": message, "code": code}}
        )

    def _build_response(self, status_code: int, body: Any) -> Response:
        return Response(
            status_code=status_code,
            headers=CORSHelper.get_cors_headers(),
            body=body,
        )
