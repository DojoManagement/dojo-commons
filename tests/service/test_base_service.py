import unittest
from unittest.mock import Mock, call

from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.service.base_service import BaseService
from tests import UserRepository, User


class TestBaseService(unittest.TestCase):
    def setUp(self):
        self.cfg = AppConfiguration(
            app_name="test_app",
            app_version="1.0.0",
            s3_bucket="test-bucket",
            s3_path="db",
            aws_region="us-east-1",
            aws_endpoint="http://localhost:9000",
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
        )

        self.mock_repository = Mock(spec=UserRepository)
        self.service = BaseService(self.cfg, self.mock_repository)  # type: ignore

    def test_ctor(self):
        service = BaseService(self.cfg, self.mock_repository)  # type: ignore

        self.assertEqual(call(self.cfg), self.mock_repository.call_args)
        self.assertEqual(
            self.mock_repository.return_value, service._repository
        )
        self.mock_repository.reset_mock()

    def test_create(self):
        user = User(name="Rodrigo", email="rodrigo@example.com")
        self.service.create(user)

        self.assertEqual(call(user), self.mock_repository().create.call_args)
        self.mock_repository.reset_mock()

    def test_get_by_id(self):
        user_id = 1
        self.service.get_by_id(user_id)

        self.assertEqual(
            call(user_id), self.mock_repository().find_by_id.call_args
        )
        self.mock_repository.reset_mock()

    def test_list_all(self):
        return_values = [
            User(id=1, name="Fulano", email="fulano@example.com"),
            User(id=2, name="Beltrano", email="beltrano@example.com"),
        ]
        self.mock_repository().find_all.return_value = return_values
        actual = self.service.list_all()

        self.assertEqual(call(), self.mock_repository().find_all.call_args)
        self.assertEqual(return_values, actual)
        self.mock_repository.reset_mock()

    def test_update(self):
        user = User(id=1, name="Rodrigo", email="rodrigo@example.com")
        return_value = user
        self.mock_repository().update.return_value = return_value
        actual = self.service.update(user)

        self.assertEqual(
            call(
                1, {"id": 1, "name": "Rodrigo", "email": "rodrigo@example.com"}
            ),
            self.mock_repository().update.call_args,
        )
        self.assertEqual(return_value, actual)
        self.mock_repository.reset_mock()

    def test_delete(self):
        user_id = 1
        self.service.delete(user_id)

        self.assertEqual(
            call(user_id), self.mock_repository().delete.call_args
        )
        self.mock_repository.reset_mock()
