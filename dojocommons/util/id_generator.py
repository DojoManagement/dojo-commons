import uuid


class IdGenerator:
    """
    Gerador de IDs únicos usando UUID v4.
    """

    @staticmethod
    def generate() -> str:
        """
        Gera um UUID v4 (aleatório).

        Exemplo: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            str: UUID v4 como string (36 caracteres)

        """
        return str(uuid.uuid4())

    @staticmethod
    def is_valid_uuid(uuid_str: str) -> bool:
        """
        Valida se uma string é um UUID válido.

        Args:
            uuid_str: String para validar

        Returns:
            bool: True se for UUID válido

        """
        try:
            uuid.UUID(uuid_str)
        except (ValueError, AttributeError, TypeError):
            return False
        else:
            return True
