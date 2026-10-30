import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import translate


class BrowserLinkTests(unittest.TestCase):
    def test_absolute_web_urls_are_allowed(self):
        for url in (
            "https://example.org/path?q=test#section",
            "http://localhost:8080/",
            "HTTPS://example.org/",
            "https://[::1]:443/",
            "https://example.org/a%20b",
        ):
            with self.subTest(url=url):
                self.assertTrue(translate.is_safe_browser_url(url))

    def test_unsafe_or_malformed_urls_are_rejected(self):
        for url in (
            "file:///C:/Windows/system32/calc.exe",
            "javascript:alert(1)", "data:text/html,test", "mailto:test@example.org",
            "ms-settings:display", "//example.org", "C:\\test.exe",
            "https:///missing-host", "https://", "https://[broken",
            "https://example.org:invalid", "https://example.org:65536",
            "https://example.org:0", "https://trusted.org@evil.org/",
            "https://example.org\\evil", "https://example.org/\nfile:test",
            "\thttps://example.org", " https://example.org", "https://example.org/\x00",
            "https://example.org/\x7f", "", None,
        ):
            with self.subTest(url=url):
                self.assertFalse(translate.is_safe_browser_url(url))

    def test_clipboard_file_link_is_not_clickable(self):
        parser = translate.ClipboardHtmlParser()
        parser.feed('<a href="file:///C:/test.exe">Document</a>')
        self.assertEqual(parser.text, "Document")
        app = SimpleNamespace(_link_tag_counter=0, _link_tag_urls={})
        widget = Mock()
        translate.TranslatorApp._add_rich_link_tag(
            app, widget, "source", "1.0", "1.8", "file:///C:/test.exe"
        )
        widget.tag_add.assert_not_called()
        self.assertEqual(app._link_tag_urls, {})

    def test_click_rechecks_url_before_calling_browser(self):
        widget = Mock()
        widget.tag_names.return_value = ("link", "source_rich_link_0")
        app = SimpleNamespace(
            _link_tag_urls={"source_rich_link_0": "file:///C:/test.exe"},
            status_label=Mock(), set_status_text=Mock(),
        )
        with patch.object(translate.webbrowser, "open") as browser:
            result = translate.TranslatorApp._open_link_at_event(
                app, widget, SimpleNamespace(x=5, y=5)
            )
        self.assertEqual(result, "break")
        browser.assert_not_called()

    def test_web_link_still_opens_in_browser(self):
        widget = Mock()
        widget.tag_names.return_value = ("source_rich_link_0",)
        url = "https://example.org/"
        app = SimpleNamespace(
            _link_tag_urls={"source_rich_link_0": url},
            status_label=Mock(), set_status_text=Mock(),
        )
        with patch.object(translate.webbrowser, "open") as browser:
            translate.TranslatorApp._open_link_at_event(
                app, widget, SimpleNamespace(x=5, y=5)
            )
        browser.assert_called_once_with(url)


if __name__ == "__main__":
    unittest.main()
