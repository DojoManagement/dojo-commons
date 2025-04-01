import unittest
from unittest.mock import MagicMock, call
from typing import Optional
from pydantic import BaseModel
from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.repository.base_repository import BaseRepository


# Modelo de exemplo para os testes
class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str


class TestBaseRepository(unittest.TestCase):
    def setUp(self):
        # Configuração do mock para o DbService
        self.mock_db_service = MagicMock()
        self.app_cfg = AppConfiguration(
            app_name="TestApp",
            app_version="1.0.0",
            s3_bucket="test-bucket",
            s3_path="db",
            aws_region="us-east-1",
            aws_endpoint="http://localhost:9000",
            aws_access_key_id="test-access-key",
            aws_secret_access_key="test-secret-key",
        )
        self.repository = BaseRepository(
            cfg=self.app_cfg, model=User, table_name="users"
        )
        self.repository._db = self.mock_db_service

    def test_create(self):
        # Configuração
        user = User(name="John Doe", email="john.doe@example.com")
        self.mock_db_service.execute_query.return_value = None

        # Execução
        result = self.repository.create(user)

        # Verificação
        self.assertEqual(
            call(
                f"INSERT INTO {self.repository._table_name} (name, email) VALUES (?, ?)",
                ("John Doe", "john.doe@example.com"),
            ),
            self.mock_db_service.execute_query.call_args,
        )
        self.assertEqual(user, result)

    def test_find_by_id_found(self):
        # Configuração
        user_data = (1, "John Doe", "john.doe@example.com")
        mock_execute_query = self.mock_db_service.execute_query.return_value
        mock_execute_query.fetchone.return_value = user_data

        # Execução
        result = self.repository.find_by_id(1)

        # Verificação
        self.assertEqual(
            call("SELECT * FROM users WHERE id = ?", (1,)),
            self.mock_db_service.execute_query.call_args,
        )
        self.assertIsNotNone(result)
        self.assertEqual(1, result.id)
        self.assertEqual("John Doe", result.name)
        self.assertEqual("john.doe@example.com", result.email)

    def test_find_by_id_not_found(self):
        # Configuração
        mock_execute_query = self.mock_db_service.execute_query.return_value
        mock_execute_query.fetchone.return_value = None

        # Execução
        result = self.repository.find_by_id(1)

        # Verificação
        self.assertEqual(
            call("SELECT * FROM users WHERE id = ?", (1,)),
            self.mock_db_service.execute_query.call_args,
        )
        self.assertIsNone(result)

    def test_find_all(self):
        # Configuração
        users_data = [
            (1, "John Doe", "john.doe@example.com"),
            (2, "Jane Doe", "jane.doe@example.com"),
        ]
        mock_execute_query = self.mock_db_service.execute_query.return_value
        mock_execute_query.fetchall.return_value = users_data

        # Execução
        result = self.repository.find_all()

        # Verificação
        self.assertEqual(
            call("SELECT * FROM users"),
            self.mock_db_service.execute_query.call_args,
        )
        self.assertEqual(2, len(result))
        self.assertEqual(1, result[0].id)
        self.assertEqual("John Doe", result[0].name)
        self.assertEqual("john.doe@example.com", result[0].email)
        self.assertEqual(2, result[1].id)
        self.assertEqual("Jane Doe", result[1].name)
        self.assertEqual("jane.doe@example.com", result[1].email)

    def test_update(self):
        # Configuração
        updated_user_data = (1, "John Smith", "john.smith@example.com")
        mock_execute_query = self.mock_db_service.execute_query.return_value
        mock_execute_query.fetchone.return_value = updated_user_data

        # Execução
        result = self.repository.update(1, {"name": "John Smith"})

        # Verificação
        self.assertEqual(
            [
                call(
                    "UPDATE users SET name = ? WHERE id = ?",
                    ("John Smith", 1),
                ),
                call("SELECT * FROM users WHERE id = ?", (1,)),
            ],
            self.mock_db_service.execute_query.call_args_list,
        )
        self.assertIsNotNone(result)
        self.assertEqual(1, result.id)
        self.assertEqual("John Smith", result.name)
        self.assertEqual("john.smith@example.com", result.email)

    def test_delete(self):
        # Configuração
        self.mock_db_service.execute_query.return_value = None

        # Execução
        self.repository.delete(1)

        # Verificação
        self.assertEqual(
            call("DELETE FROM users WHERE id = ?", (1,)),
            self.mock_db_service.execute_query.call_args,
        )
        self.assertTrue(self.mock_db_service.execute_query.called)


if __name__ == "__main__":
    unittest.main()
