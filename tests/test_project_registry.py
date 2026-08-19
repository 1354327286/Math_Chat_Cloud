import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_project_registry import validate_registry
from scripts.project_registry import RegistryError, load_registry


class ProjectRegistryTests(unittest.TestCase):
    def test_accepts_valid_registry_without_directory_check(self):
        data = {
            "schema_version": 1,
            "projects": [
                {
                    "path": "sample_problem",
                    "title": "Sample",
                    "role": "active",
                    "description": "Description",
                }
            ],
        }
        self.assertEqual(validate_registry(data, Path("."), check_directories=False), [])

    def test_rejects_duplicate_or_unsafe_projects(self):
        data = {
            "schema_version": 1,
            "projects": [
                {"path": "../bad", "title": "Bad", "role": "unknown", "description": ""},
                {"path": "same", "title": "A", "role": "active", "description": ""},
                {"path": "same", "title": "B", "role": "active", "description": ""},
            ],
        }
        errors = validate_registry(data, Path("."), check_directories=False)
        self.assertTrue(any("safe ASCII" in error for error in errors))
        self.assertTrue(any("unsupported" in error for error in errors))
        self.assertTrue(any("duplicated" in error for error in errors))

    def test_merges_public_example_and_private_overlay(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "projects.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "projects": [
                            {
                                "path": "example_math_problem",
                                "title": "Example",
                                "role": "example",
                                "description": "Public",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (root / "projects.local.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "projects": [
                            {
                                "path": "sample_problem",
                                "title": "Sample",
                                "role": "active",
                                "description": "Private",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            registry = load_registry(root)
            self.assertEqual(
                [item["path"] for item in registry["projects"]],
                ["example_math_problem", "sample_problem"],
            )

    def test_duplicate_across_public_and_local_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record = {
                "path": "sample_problem",
                "title": "Sample",
                "role": "active",
                "description": "Description",
            }
            payload = json.dumps({"schema_version": 1, "projects": [record]})
            (root / "projects.json").write_text(payload, encoding="utf-8")
            (root / "projects.local.json").write_text(payload, encoding="utf-8")
            with self.assertRaises(RegistryError):
                load_registry(root)


if __name__ == "__main__":
    unittest.main()
