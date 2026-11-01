import json
import queue
import tempfile
import threading
import unittest
from pathlib import Path
from types import MethodType
from unittest.mock import Mock, patch

import translate


class ConfigSwitchingTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(translate.CONFIG)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.example = json.loads((Path(__file__).resolve().parents[1] /
                                   '.translator_config.example.json').read_text(encoding='utf-8'))
        self.patcher = patch.object(translate, '_automatic_config_path',
                                    return_value=self.root / '.translator_config.json')
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def tearDown(self):
        translate.CONFIG.clear()
        translate.CONFIG.update(self.original)

    def config(self, name, **updates):
        path = self.root / name
        path.write_text(json.dumps(dict(self.example, models_url='', **updates)), encoding='utf-8')
        return translate.load_config(path, ask_if_missing=False)

    def app(self):
        app = Mock()
        app._config_editor = None
        app._config_generation = object()
        app._pending_lookups = []
        app.stop_event = threading.Event()
        app.is_translating = True
        app.source_lang.get.return_value = 'auto'
        app.target_lang.get.return_value = 'fr'
        app.output_queue = queue.Queue()
        app.running = True
        return app

    def test_remembers_absolute_path_and_explicit_choice_takes_precedence(self):
        first = self.config('.translator_config.json')
        second = self.config('EPFL.json', api_key='fake-test-key')
        translate.remember_config_path(second['_config_source'])
        self.assertEqual(translate.load_config(ask_if_missing=False)['_config_source'], second['_config_source'])
        self.assertEqual(translate.load_config(first['_config_source'])['_config_source'], first['_config_source'])
        preferences = json.loads(translate._startup_preferences_path().read_text())
        self.assertEqual(preferences, {'last_config': second['_config_source']})

    def test_missing_remembered_file_does_not_silently_change_server(self):
        self.config('.translator_config.json')
        translate.remember_config_path(self.root / 'missing.json')
        with self.assertRaises(translate.ConfigError):
            translate.load_config(ask_if_missing=False)

    def test_cancel_and_invalid_file_keep_current_configuration_and_request(self):
        app = self.app()
        invalid = self.root / 'invalid.json'
        invalid.write_text('{}')
        for choice in ('', str(invalid)):
            with patch.object(translate.filedialog, 'askopenfilename', return_value=choice), \
                    patch.object(translate.messagebox, 'showerror'):
                translate.TranslatorApp.open_configuration(app)
            app._apply_runtime_config.assert_not_called()
            self.assertFalse(app.stop_event.is_set())
            self.assertEqual(translate.CONFIG, self.original)

    def test_switch_cancels_old_work_without_deleting_text(self):
        app = self.app()
        old_stop, old_generation = app.stop_event, app._config_generation
        config = self.config('Ollama.json')
        translate.TranslatorApp._apply_runtime_config(app, config)
        self.assertTrue(old_stop.is_set())
        self.assertIsNot(old_generation, app._config_generation)
        self.assertFalse(app.is_translating)
        app.source_text.delete.assert_not_called()
        app.target_text.delete.assert_not_called()
        self.assertEqual(translate.CONFIG['_config_source'], config['_config_source'])
        callback = Mock()
        app.output_queue.put(('configuration', (old_generation, 'call', (callback, ()))))
        app.output_queue.put(('translation', (old_stop, 'insert', 'old result')))
        translate.TranslatorApp._process_queue(app)
        callback.assert_not_called()
        app.target_text.insert.assert_not_called()

    def test_old_scheduled_translation_is_not_sent_to_new_configuration(self):
        app = self.app()
        callback = Mock()
        translate.TranslatorApp._after_for_configuration(app, 100, callback)
        scheduled = app.after.call_args.args[1]
        app._config_generation = object()
        scheduled()
        callback.assert_not_called()

    def test_worker_uses_original_server_credentials_and_prompt(self):
        old = self.config('Old.json', server_url='http://old.example/chat', api_key='fake-old-key')
        new = self.config('New.json', server_url='http://new.example/chat', api_key='fake-new-key')
        app = self.app()
        app._build_prompt = MethodType(translate.TranslatorApp._build_prompt, app)
        translate.CONFIG.clear()
        translate.CONFIG.update(new)
        response = Mock()
        response.iter_lines.return_value = []
        with patch.object(translate.requests, 'post', return_value=response) as post:
            translate.TranslatorApp._translate_thread(app, 'text', 'text', 'translate',
                                                      'en', 'fr', 'old-model', app.stop_event, old)
        self.assertEqual(post.call_args.args[0], old['server_url'])
        self.assertEqual(post.call_args.kwargs['headers'], {'Authorization': 'Bearer fake-old-key'})
        response.close.assert_called_once()

    def test_cancelled_worker_does_not_start_request(self):
        app = self.app()
        app.stop_event.set()
        with patch.object(translate.requests, 'post') as post:
            translate.TranslatorApp._translate_thread(app, 'text', 'text', 'translate',
                                                      'en', 'fr', 'model', app.stop_event)
        post.assert_not_called()

    def test_editor_must_be_closed_before_switch(self):
        app = self.app()
        app._config_editor = Mock()
        with patch.object(translate.filedialog, 'askopenfilename') as chooser, \
                patch.object(translate.messagebox, 'showinfo'):
            translate.TranslatorApp.open_configuration(app)
        chooser.assert_not_called()
        app._apply_runtime_config.assert_not_called()
