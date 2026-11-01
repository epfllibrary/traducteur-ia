import json
import tempfile
import unittest
from pathlib import Path

import translate


class UiPreferenceTests(unittest.TestCase):
    def test_zoom_and_last_model_do_not_overwrite_each_other(self):
        with tempfile.TemporaryDirectory() as directory:
            config = {'_config_source': str(Path(directory) / 'config.json'),
                      'api_format': 'ollama', 'server_url': 'http://localhost/api/chat'}
            translate.save_last_model(config, 'first')
            translate._save_user_state(config, ui_scale=125)
            self.assertEqual(translate.load_last_model(config), 'first')
            translate.save_last_model(config, 'second')
            self.assertEqual(translate.load_ui_scale(config), 125)
            self.assertEqual(translate.load_last_model(config), 'second')
            config['server_url'] = 'http://another-server/api/chat'
            self.assertEqual(translate.load_last_model(config), '')
            self.assertEqual(translate.load_ui_scale(config), 125)

    def test_invalid_or_missing_zoom_uses_windows_default(self):
        with tempfile.TemporaryDirectory() as directory:
            config = {'_config_source': str(Path(directory) / 'config.json')}
            self.assertEqual(translate.load_ui_scale(config), 100)
            path = translate._model_state_path(config)
            for value in (None, True, '125', 0, -100, 900, [], {}):
                with self.subTest(value=value):
                    path.write_text(json.dumps({'ui_scale': value}), encoding='utf-8')
                    self.assertEqual(translate.load_ui_scale(config), 100)
            path.write_text('invalid json', encoding='utf-8')
            self.assertEqual(translate.load_ui_scale(config), 100)
