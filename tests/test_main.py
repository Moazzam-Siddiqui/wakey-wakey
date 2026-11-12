import unittest
from unittest.mock import Mock, patch
import main

class ConfigTests(unittest.TestCase):
    def test_env_json_empty_defaults_to_empty_dict(self):
        with patch.dict("os.environ", {"TEST_MAP": ""}, clear=False):
            self.assertEqual(main.env_json("TEST_MAP"), {})

    def test_env_json_parses_project_password_map(self):
        value = '{"project-a":"secret","project-b":"secret2"}'
        with patch.dict("os.environ", {"TEST_MAP": value}, clear=False):
            self.assertEqual(main.env_json("TEST_MAP"), {"project-a": "secret", "project-b": "secret2"})

    def test_env_json_rejects_non_object(self):
        with patch.dict("os.environ", {"TEST_MAP": '["not","an","object"]'}, clear=False):
            with self.assertRaises(ValueError):
                main.env_json("TEST_MAP")

    def test_selected_project_refs_parses_comma_separated_values(self):
        with patch.dict("os.environ", {"SUPABASE_PROJECT_REFS": "abc, def ,ghi"}, clear=False):
            self.assertEqual(main.selected_project_refs(), {"abc", "def", "ghi"})

    def test_selected_project_refs_empty_means_all(self):
        with patch.dict("os.environ", {"SUPABASE_PROJECT_REFS": ""}, clear=False):
            self.assertEqual(main.selected_project_refs(), set())

class ProjectTests(unittest.TestCase):
    def test_get_status_uses_status_field(self):
        self.assertEqual(main.get_status({"status": "INACTIVE"}), "INACTIVE")

    def test_get_status_handles_missing_status(self):
        self.assertEqual(main.get_status({}), "UNKNOWN")

    def test_list_projects_returns_project_list(self):
        session = Mock()
        response = Mock(status_code=200)
        response.json.return_value = [{"ref": "abc", "name": "demo"}]
        session.request.return_value = response
        projects = main.list_projects(session)
        self.assertEqual(projects, [{"ref": "abc", "name": "demo"}])
        session.request.assert_called_once()

if __name__ == "__main__":
    unittest.main()
