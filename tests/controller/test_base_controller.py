import unittest
from http import HTTPMethod
from unittest.mock import MagicMock, Mock, call, patch

from pydantic import BaseModel

from dojocommons.controller.base_controller import BaseController
from dojocommons.model.app_configuration import AppConfiguration
from dojocommons.model.base_event import BaseEvent
from tests import User, UserRepository, UserResource, UserService


class MockModel(BaseModel):
    id: int
    name: str


class TestBaseController(unittest.TestCase):
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
        self.mock_service = Mock(spec=UserService)
        self.mock_resource = Mock(spec=UserResource)
        self.mock_model = Mock(spec=User)

        self.controller = BaseController(
            self.cfg,
            self.mock_service,
            self.mock_resource,
            self.mock_model,  # type: ignore
        )

    def test_ctor(self):
        controller = BaseController(
            self.cfg,
            self.mock_service,
            self.mock_resource,
            self.mock_model,  # type: ignore
        )

        self.assertEqual(call(self.cfg), self.mock_service.call_args)
        self.assertEqual(self.mock_service.return_value, controller._service)
        self.assertEqual(self.mock_resource, controller._resource)
        self.assertEqual(self.mock_model, controller._model_class)

    def test_dispatch_method_not_allowed(self):
        # Evento com método HTTP não suportado
        event = MagicMock(spec=BaseEvent)
        event.http_method = "PATCH"

        response = self.controller.dispatch(event)

        self.assertEqual(405, response.status_code)
        self.assertEqual("Method Not Allowed", response.body)

    def test_get_list(self):
        # Mock do evento GET para listar
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.GET
        event.resource = self.mock_resource

        # Mock do retorno do serviço
        self.mock_service().list_all.return_value = [
            MagicMock(model_dump=lambda: {"id": 1, "name": "Test Entity"})
        ]

        response = self.controller.dispatch(event)

        self.assertEqual(200, response.status_code)
        self.assertIn("items", response.body)
        self.assertTrue(self.mock_service().list_all.called)

    def test_get_resource_not_found(self):
        # Mock do evento GET para um recurso inexistente
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.GET
        event.resource = "non_existent_resource"

        response = self.controller.dispatch(event)

        self.assertEqual(404, response.status_code)
        self.assertEqual("Resource not Found", response.body)

    def test_get_by_id(self):
        # Mock do evento GET para buscar por ID
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.GET
        event.resource = f"{self.mock_resource}_ID"
        event.path_parameters = {"id": "1"}

        def f(exclude_none):
            return {"id": 1, "name": "Test Entity"}

        # Mock do retorno do serviço
        self.mock_service().get_by_id.return_value = MagicMock(
            model_dump_json=f,
        )

        response = self.controller.dispatch(event)

        self.assertEqual(200, response.status_code)
        self.assertIn("item", response.body)
        self.assertEqual(call(1), self.mock_service().get_by_id.call_args)

    def test_get_by_id_not_found(self):
        # Mock do evento GET para buscar por ID
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.GET
        event.resource = f"{self.mock_resource}_ID"
        event.path_parameters = {"id": "1"}

        # Mock do retorno do serviço
        self.mock_service().get_by_id.return_value = None

        response = self.controller.dispatch(event)

        self.assertEqual(404, response.status_code)
        self.assertEqual("Entity not found", response.body)
        self.assertEqual(call(1), self.mock_service().get_by_id.call_args)

    def test_post(self):
        # Mock do evento POST
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.POST
        event.body = '{"name": "New Entity"}'

        # Mock do retorno do serviço
        created_entity = MockModel(id=1, name="New Entity")
        self.mock_service().create.return_value = created_entity

        with patch.object(
            MockModel,
            "model_validate_json",
            return_value=created_entity,
        ):
            response = self.controller.dispatch(event)

        self.assertEqual(201, response.status_code)
        self.assertIn("item", response.body)
        self.assertTrue(self.mock_service().create.called)
        self.assertEqual(
            '{"item": {"id":1,"name":"New Entity"}}',
            response.body,
        )

    def test_put(self):
        # Mock do evento PUT
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.PUT
        event.path_parameters = {"id": "1"}
        event.body = '{"name": "Updated Entity"}'

        # Mock do retorno do serviço
        existing_entity = MockModel(id=1, name="Old Entity")
        updated_entity = MockModel(id=1, name="Updated Entity")

        self.mock_service().get_by_id.return_value = existing_entity
        self.mock_service().update.return_value = updated_entity

        with patch.object(
            MockModel,
            "model_validate_json",
            return_value=updated_entity,
        ):
            response = self.controller.dispatch(event)

        self.assertEqual(200, response.status_code)
        self.assertIn("item", response.body)
        self.assertTrue(self.mock_service().update.called)
        self.assertEqual(call(1), self.mock_service().get_by_id.call_args)
        self.assertEqual(
            '{"item": {"id":1,"name":"Updated Entity"}}',
            response.body,
        )

    def test_put_not_found(self):
        # Mock do evento PUT com entidade inexistente
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.PUT
        event.path_parameters = {"id": "1"}
        event.body = '{"name": "Updated Entity"}'

        # Mock do retorno do serviço
        self.mock_service().get_by_id.return_value = None

        response = self.controller.dispatch(event)

        self.assertEqual(404, response.status_code)
        self.assertEqual("Entity not found", response.body)
        self.assertEqual(call(1), self.mock_service().get_by_id.call_args)
        self.assertFalse(self.mock_service().update.called)

    def test_delete(self):
        # Mock do evento DELETE
        event = MagicMock(spec=BaseEvent)
        event.http_method = HTTPMethod.DELETE
        event.path_parameters = {"id": "1"}

        response = self.controller.dispatch(event)

        self.assertEqual(204, response.status_code)
        self.assertIsNone(response.body)
        self.assertEqual(call(1), self.mock_service().delete.call_args)
