import http
import unittest

from pydantic import ValidationError

from dojocommons.model.base_event import BaseEvent


class TestEventModel(unittest.TestCase):
    def test_valid_event_get(self):
        event_data = {
            "resource": "/example/{id}",
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": {"id": "123"},
            "body": None,
        }
        event = BaseEvent.model_validate(event_data)
        self.assertEqual("/example/{id}", event.resource)
        self.assertEqual(http.HTTPMethod.GET, event.http_method)
        self.assertEqual({"Content-Type": "application/json"}, event.headers)
        self.assertEqual({"key": "value"}, event.query_parameters)
        self.assertEqual({"id": "123"}, event.path_parameters)
        self.assertIsNone(event.body)

    def test_valid_event_get_no_id(self):
        event_data = {
            "resource": "/example",
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": None,
            "body": None,
        }
        event = BaseEvent.model_validate(event_data)
        self.assertEqual("/example", event.resource)
        self.assertEqual(http.HTTPMethod.GET, event.http_method)
        self.assertEqual({"Content-Type": "application/json"}, event.headers)
        self.assertEqual({"key": "value"}, event.query_parameters)
        self.assertIsNone(event.path_parameters)
        self.assertIsNone(event.body)

    def test_invalid_http_method(self):
        event_data = {
            "resource": "/example",
            "httpMethod": "OPTIONS",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": {"id": "123"},
            "body": None,
        }
        with self.assertRaises(ValidationError) as context:
            BaseEvent.model_validate(event_data)
        self.assertIn("Método HTTP 'OPTIONS' não é válido", str(context.exception))

    def test_missing_body_for_post(self):
        event_data = {
            "resource": "/example",
            "httpMethod": "POST",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": {"id": "123"},
            "body": None,
        }
        with self.assertRaises(ValidationError) as context:
            BaseEvent.model_validate(event_data)
        self.assertIn(
            "Corpo da requisição é obrigatório para as operações POST e PUT",
            str(context.exception),
        )

    def test_missing_path_parameters_for_get(self):
        event_data = {
            "resource": "/example/{id}",
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": None,
            "body": None,
        }
        with self.assertRaises(ValidationError) as context:
            BaseEvent.model_validate(event_data)
        self.assertIn(
            "Parâmetro 'id' é obrigatório para as operações GET, PUT e DELETE",
            str(context.exception),
        )

    def test_valid_event_post(self):
        event_data = {
            "resource": "/example",
            "httpMethod": "POST",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": {"id": "123"},
            "body": '{"key": "value"}',
        }
        event = BaseEvent.model_validate(event_data)
        self.assertEqual("/example", event.resource)
        self.assertEqual(http.HTTPMethod.POST, event.http_method)
        self.assertEqual({"Content-Type": "application/json"}, event.headers)
        self.assertEqual({"key": "value"}, event.query_parameters)
        self.assertEqual({"id": "123"}, event.path_parameters)
        self.assertEqual('{"key": "value"}', event.body)

    def test_missing_id_in_path_parameters(self):
        event_data = {
            "resource": "/example/{id}",
            "httpMethod": "DELETE",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"key": "value"},
            "pathParameters": {},
            "body": None,
        }
        with self.assertRaises(ValidationError) as context:
            BaseEvent.model_validate(event_data)
        self.assertIn(
            "Parâmetro 'id' é obrigatório para as operações GET, PUT e DELETE",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
