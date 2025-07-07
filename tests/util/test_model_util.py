import datetime
import unittest

from pydantic import BaseModel

from dojocommons.util.model_util import ModelUtil


class DummyModel(BaseModel):
    id: int
    name: str
    value: float
    active: bool
    created_at: datetime.datetime
    birth_date: datetime.date
    data: dict
    tags: list
    optional_field: str = None


class TestModelUtil(unittest.TestCase):
    def test_pydantic_type_to_sql_basic_types(self):
        self.assertEqual(ModelUtil.pydantic_type_to_sql(int), "INTEGER")
        self.assertEqual(ModelUtil.pydantic_type_to_sql(float), "REAL")
        self.assertEqual(ModelUtil.pydantic_type_to_sql(str), "TEXT")
        self.assertEqual(ModelUtil.pydantic_type_to_sql(bool), "BOOLEAN")
        self.assertEqual(ModelUtil.pydantic_type_to_sql(list), "ARRAY")
        self.assertEqual(ModelUtil.pydantic_type_to_sql(dict), "JSONB")
        self.assertEqual(ModelUtil.pydantic_type_to_sql(datetime.date), "DATE")
        self.assertEqual(
            ModelUtil.pydantic_type_to_sql(datetime.datetime),
            "TIMESTAMP",
        )
        self.assertEqual(ModelUtil.pydantic_type_to_sql(bytes), "TEXT")

    def test_pydantic_type_to_sql_optional(self):
        from typing import Optional

        self.assertEqual(ModelUtil.pydantic_type_to_sql(Optional[str]), "TEXT")
        self.assertEqual(
            ModelUtil.pydantic_type_to_sql(Optional[int]),
            "INTEGER",
        )

    def test_generate_create_table_sql(self):
        sql = ModelUtil.generate_create_table_sql(DummyModel, "dummy_table")
        self.assertIn("CREATE TABLE dummy_table", sql)
        self.assertIn("id INTEGER NOT NULL PRIMARY KEY", sql)
        self.assertIn("name TEXT NOT NULL", sql)
        self.assertIn("value REAL NOT NULL", sql)
        self.assertIn("active BOOLEAN NOT NULL", sql)
        self.assertIn("created_at TIMESTAMP NOT NULL", sql)
        self.assertIn("birth_date DATE NOT NULL", sql)
        self.assertIn("data JSONB NOT NULL", sql)
        self.assertIn("tags ARRAY NOT NULL", sql)
        self.assertIn("optional_field TEXT NULL", sql)
        self.assertTrue(sql.strip().endswith(");"))

    def test_generate_create_table_sql_default_table_name(self):
        sql = ModelUtil.generate_create_table_sql(DummyModel)
        self.assertIn("CREATE TABLE dummymodel", sql)


if __name__ == "__main__":
    unittest.main()
