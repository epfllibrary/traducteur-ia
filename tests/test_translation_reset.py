import queue
import threading
import unittest
from unittest.mock import Mock, patch

import translate


class TranslationResetTests(unittest.TestCase):
    def make_app(self):
        app = Mock()
        app.running = True
        app.is_translating = True
        app.stop_event = threading.Event()
        app.output_queue = queue.Queue()
        app._build_prompt.return_value = "Texte de test"
        return app

    def test_clear_discards_queued_and_late_updates(self):
        app = self.make_app()
        old_request = app.stop_event
        app.output_queue.put(("translation", (old_request, "insert", "Déjà reçu")))
        translate.TranslatorApp.clear_text(app)
        self.assertTrue(old_request.is_set())
        self.assertIsNot(app.stop_event, old_request)
        app.set_status_text.reset_mock()
        callback = Mock()
        for kind, data in (
            ("insert", "Réponse tardive"), ("time", 12.0),
            ("history", {"target": "Ancien résultat"}),
            ("call", (callback, ())), ("status", "Ancienne erreur"),
            ("done", None),
        ):
            app.output_queue.put(("translation", (old_request, kind, data)))
        # Une nouvelle requête a pu commencer immédiatement après l'effacement.
        app.is_translating = True
        translate.TranslatorApp._process_queue(app)
        app.target_text.insert.assert_not_called()
        app.set_status_text.assert_not_called()
        app._add_history_item.assert_not_called()
        callback.assert_not_called()
        self.assertTrue(app.is_translating)

    def test_current_request_still_updates_result_and_finishes(self):
        app = self.make_app()
        for kind, data in (("insert", "Nouveau résultat"), ("time", 1.5), ("done", None)):
            app.output_queue.put(("translation", (app.stop_event, kind, data)))
        translate.TranslatorApp._process_queue(app)
        app.target_text.insert.assert_called_once_with(translate.tk.END, "Nouveau résultat")
        self.assertEqual(app.translation_time, 1.5)
        self.assertFalse(app.is_translating)

    def test_worker_keeps_its_original_cancellation_event(self):
        app = self.make_app()
        old_request = app.stop_event
        response = Mock()

        def chunks():
            yield b'{"message":{"content":"Premier morceau"}}'
            translate.TranslatorApp.clear_text(app)
            app.is_translating = True  # Une nouvelle génération est lancée.
            yield b'{"message":{"content":"A ignorer"}}'

        response.iter_lines.side_effect = chunks
        with patch.dict(translate.CONFIG, api_format="ollama"), \
                patch.object(translate.requests, "post", return_value=response):
            translate.TranslatorApp._translate_thread(
                app, "Texte", "Texte", "translate", "en", "fr", "model", old_request
            )
        translate.TranslatorApp._process_queue(app)
        app.target_text.insert.assert_not_called()
        app._add_history_item.assert_not_called()
        self.assertTrue(app.is_translating)
        response.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
