from dojocommons.interface_adapters.dtos.response import Response


class CORSHelper:
    """
    Helper para adicionar headers CORS às respostas
    """

    @staticmethod
    def get_cors_headers(
        additional_headers: dict[str, str] | None = None, origin: str = "*"
    ) -> dict[str, str]:
        """
        Retorna headers CORS padrão
        """
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": (
                "Content-Type, Authorization,X-Amz-Date, X-Api-Key"
            ),
            "Access-Control-Max-Age": "300",
        }

        if additional_headers:
            headers.update(additional_headers)

        return headers

    @staticmethod
    def add_cors_headers(response: Response) -> Response:
        """
        Adiciona headers CORS a um objeto Response
        """
        cors_headers = CORSHelper.get_cors_headers()

        if response.headers:
            response.headers.update(cors_headers)
        else:
            response.headers = cors_headers

        return response

    @staticmethod
    def create_error_response(
        status_code: int, error_message: str, error_type: str = "Error"
    ) -> Response:
        """
        Cria resposta de erro com CORS
        """
        return Response(
            status_code=status_code,
            headers=CORSHelper.get_cors_headers(),
            body={"error": error_type, "message": error_message},
        )
