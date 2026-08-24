import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import translate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = json.loads(
            (PROJECT_ROOT / ".translator_config.example.json").read_text(encoding="utf-8")
        )

    def setUp(self):
        self.original_config = translate.CONFIG.copy()

    def tearDown(self):
        translate.CONFIG.clear()
        translate.CONFIG.update(self.original_config)

    def _write_config(self, directory, **updates):
        config = dict(self.example)
        config.update(updates)
        path = Path(directory) / ".translator_config.json"
        path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        return path

    def test_server_url_is_loaded_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            expected_url = "https://inference.example/v1/chat/completions/"
            path = self._write_config(directory, server_url=expected_url)

            config = translate.load_config(path, ask_if_missing=False)

        self.assertEqual(config["server_url"], expected_url)

    def test_default_model_is_optional_when_models_url_is_configured(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(
                directory,
                default_model="",
                models_url="https://inference.example/models",
            )

            config = translate.load_config(path, ask_if_missing=False)

        self.assertEqual(config["default_model"], "")

    def test_default_model_or_models_url_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory, default_model="", models_url="")

            with self.assertRaises(translate.ConfigError):
                translate.load_config(path, ask_if_missing=False)

    def test_api_format_is_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory, api_format="unknown")

            with self.assertRaises(translate.ConfigError):
                translate.load_config(path, ask_if_missing=False)

    def test_api_format_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory)
            config = json.loads(path.read_text(encoding="utf-8"))
            config.pop("api_format")
            path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            with self.assertRaises(translate.ConfigError):
                translate.load_config(path, ask_if_missing=False)

    def test_model_discovery_is_not_derived_from_server_url(self):
        translate.CONFIG.clear()
        translate.CONFIG.update(
            server_url="https://inference.example/custom-endpoint",
            default_model="custom-model",
        )

        with patch.object(translate.requests, "get") as get:
            models = translate.TranslatorApp._fetch_models(object())

        self.assertEqual(models, ["custom-model"])
        get.assert_not_called()

    def test_available_models_are_loaded_when_default_is_empty(self):
        translate.CONFIG.clear()
        translate.CONFIG.update(
            api_format="ollama",
            server_url="https://inference.example/chat",
            models_url="https://inference.example/models",
            default_model="",
        )
        response = Mock()
        response.json.return_value = {
            "models": [{"name": "model-a"}, {"name": "model-b"}]
        }

        with patch.object(translate.requests, "get", return_value=response) as get:
            models = translate.TranslatorApp._fetch_models(object())

        self.assertEqual(models, ["model-a", "model-b"])
        get.assert_called_once_with(
            "https://inference.example/models",
            headers=None,
            timeout=10,
        )

    def test_openai_models_response_uses_data_ids(self):
        models = translate._parse_models_response(
            {"data": [{"id": "model-a"}, {"id": "model-b"}]},
            "openai",
        )

        self.assertEqual(models, ["model-a", "model-b"])

    def test_openai_payload_does_not_send_ollama_think(self):
        translate.CONFIG["api_format"] = "openai"
        translate.CONFIG["think"] = True
        translate.CONFIG["server_url"] = "https://inference.example/v1/chat/completions"

        payload = translate._build_chat_payload("model-a", "Bonjour", stream=True)

        self.assertNotIn("think", payload)
        self.assertEqual(
            payload["messages"],
            [{"role": "user", "content": "Bonjour"}],
        )
        self.assertNotIn("prompt", payload)
        self.assertTrue(payload["stream"])

    def test_openai_completion_endpoint_uses_prompt(self):
        translate.CONFIG["api_format"] = "openai"
        translate.CONFIG["server_url"] = "https://inference.example/v1/completions"

        payload = translate._build_chat_payload("model-a", "Bonjour", stream=True)

        self.assertEqual(payload["prompt"], "Bonjour")
        self.assertNotIn("messages", payload)

    def test_openai_endpoint_detection_ignores_query_and_trailing_slash(self):
        self.assertEqual(
            translate._openai_endpoint_kind(
                "https://inference.example/v1/completions/?deployment=one"
            ),
            "completion",
        )
        self.assertEqual(
            translate._openai_endpoint_kind(
                "https://inference.example/v1/chat/completions/"
            ),
            "chat",
        )

    def test_openai_streaming_sse_content_is_parsed(self):
        line = b'data: {"choices":[{"delta":{"content":"Bonjour"}}]}'

        content = translate._parse_stream_chunk(line, "openai")

        self.assertEqual(content, "Bonjour")
        self.assertEqual(translate._parse_stream_chunk(b"data: [DONE]", "openai"), "")

    def test_openai_completion_streaming_text_is_parsed(self):
        line = b'data: {"choices":[{"text":"Bonjour"}]}'

        content = translate._parse_stream_chunk(line, "openai")

        self.assertEqual(content, "Bonjour")

    def test_openai_non_streaming_content_is_parsed(self):
        content = translate._parse_chat_response(
            {"choices": [{"message": {"content": "Alternative"}}]},
            "openai",
        )

        self.assertEqual(content, "Alternative")

    def test_openai_completion_non_streaming_text_is_parsed(self):
        content = translate._parse_chat_response(
            {"choices": [{"text": "Alternative"}]},
            "openai",
        )

        self.assertEqual(content, "Alternative")

    def test_config_editor_save_validates_before_replacing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory)
            original_text = path.read_text(encoding="utf-8")

            with self.assertRaises(translate.ConfigError):
                translate.save_config_text('{"server_url":', path)

            self.assertEqual(path.read_text(encoding="utf-8"), original_text)

    def test_config_editor_save_returns_immediately_usable_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory)
            config_data = dict(self.example)
            config_data["server_url"] = "https://inference.example/exact"
            config_data["models_url"] = ""

            config = translate.save_config_text(
                json.dumps(config_data, ensure_ascii=False, indent=2),
                path,
            )

        self.assertEqual(config["server_url"], "https://inference.example/exact")
        self.assertEqual(config["models_url"], "")

    def test_last_model_is_persisted_next_to_active_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory)
            config = translate.load_config(path, ask_if_missing=False)

            translate.save_last_model(config, "model-used-last")

            self.assertEqual(translate.load_last_model(config), "model-used-last")
            self.assertTrue((Path(directory) / ".translator_state.json").is_file())

            changed_config = dict(config, server_url="https://other.example/chat")
            self.assertEqual(translate.load_last_model(changed_config), "")


if __name__ == "__main__":
    unittest.main()
