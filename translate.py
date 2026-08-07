#!/usr/bin/env python3
"""
Traducteur 1.0 - Interface moderne et optimisée
"""

import json
import os
import queue
import re
import sys
import threading
import time
import tkinter as tk
import webbrowser
import ctypes
from html.parser import HTMLParser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import requests

APP_NAME = "Traducteur"
APP_VERSION = "1.0"
APP_MUTEX_NAME = "TraducteurAppMutex-8E28A203-8A35-4F78-BE6B-FD0718E146AD"
START_HIDDEN = any(argument.lower() in {"--hidden", "--startup"} for argument in sys.argv[1:])
_APP_MUTEX_HANDLE = None

try:
    import customtkinter as ctk
    CTK_SUPPORT = True
except ImportError:
    CTK_SUPPORT = False

# Imports conditionnels pour les fichiers
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

# Imports pour system tray et raccourcis globaux
TRAY_SUPPORT = False
KEYBOARD_SUPPORT = False

try:
    import pystray
    from PIL import Image
    TRAY_SUPPORT = True
except Exception:
    # pystray nécessite Gtk sur Linux (pas disponible en WSL)
    TRAY_SUPPORT = False

try:
    from pynput import keyboard
    from pynput.keyboard import Listener
    KEYBOARD_SUPPORT = True
except Exception:
    KEYBOARD_SUPPORT = False

CLIPBOARD_SETTLE_DELAY_MS = 350
AUTO_TRANSLATE_DELAY_MS = 500
MODE_LABELS = {
    "translate": "Traduire",
    "rewrite": "Réécrire",
    "email": "E-mail",
}
MODE_KEYS_BY_LABEL = {label: key for key, label in MODE_LABELS.items()}
PROMPT_KEY_ALIASES = {
    "translate": "translate",
    "traduire": "translate",
    "translation": "translate",
    "rewrite": "rewrite",
    "réécrire": "rewrite",
    "reecrire": "rewrite",
    "reécrire": "rewrite",
    "email": "email",
    "e-mail": "email",
    "mail": "email",
    "lookup": "lookup",
    "synonymes": "lookup",
    "alternatives": "lookup",
}
REQUIRED_PROMPTS = ("translate", "rewrite", "email", "lookup")
REQUIRED_LANGUAGES = ("auto", "fr", "en", "de", "it", "es", "pt")
PROMPT_VARIABLES = {
    "source_language": "",
    "target_language": "",
    "text": "",
    "translation": "",
    "selection": "",
}
URL_PATTERN = re.compile(r"https?://[^\s<>'\"\]\)]+[^\s<>'\"\]\).,;:!?]")
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s<>\)]+)\)")
HEADING_STYLES = tuple(f"heading{level}" for level in range(1, 7))
RICH_STYLE_NAMES = {"bold", "italic", *HEADING_STYLES}
HEADING_FONT_SIZES = {1: 20, 2: 18, 3: 16, 4: 14, 5: 12, 6: 11}


class ClipboardHtmlParser(HTMLParser):
    """Extrait le texte, les liens et les styles depuis le HTML du presse-papiers."""

    BLOCK_TAGS = {
        "address", "article", "aside", "blockquote", "div", "footer", "h1", "h2",
        "h3", "h4", "h5", "h6", "header", "li", "main", "nav", "p", "section", "tr",
    }
    IGNORED_CONTENT_TAGS = {"script", "noscript", "title"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.links = []
        self.styles = []
        self._href_stack = []
        self._style_elements = []
        self._css_class_styles = {}
        self._style_block_depth = 0
        self._style_chunks = []
        self._head_depth = 0
        self._ignored_content_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()

        if tag == "head":
            self._head_depth += 1
            return
        if tag == "style":
            self._style_block_depth += 1
            return
        if self._style_block_depth or self._head_depth:
            return
        if tag in self.IGNORED_CONTENT_TAGS:
            self._ignored_content_depth += 1
            return
        if self._ignored_content_depth:
            return

        if tag == "a":
            self._href_stack.append(attrs.get("href", ""))
        elif (tag == "br" or tag in self.BLOCK_TAGS) and self.text and not self.text.endswith("\n"):
            self.parts.append("\n")

        opened_styles = set()
        if tag in {"b", "strong"}:
            opened_styles.add("bold")
        if tag in {"i", "em"}:
            opened_styles.add("italic")
        if re.fullmatch(r"h[1-6]", tag):
            opened_styles.add(f"heading{tag[1]}")

        for class_name in attrs.get("class", "").split():
            self._apply_css_styles(opened_styles, self._css_class_styles.get(class_name, {}))
        self._apply_css_styles(opened_styles, self._parse_style_declarations(attrs.get("style", "")))

        if opened_styles:
            self._style_elements.append(
                (tag, [(style, len(self.text)) for style in sorted(opened_styles)])
            )

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == "style" and self._style_block_depth:
            self._style_block_depth -= 1
            if not self._style_block_depth:
                self._parse_css_rules("".join(self._style_chunks))
                self._style_chunks.clear()
            return
        if tag == "head" and self._head_depth:
            self._head_depth -= 1
            return
        if self._style_block_depth or self._head_depth:
            return
        if tag in self.IGNORED_CONTENT_TAGS and self._ignored_content_depth:
            self._ignored_content_depth -= 1
            return
        if self._ignored_content_depth:
            return

        if tag == "a" and self._href_stack:
            self._href_stack.pop()

        for index in range(len(self._style_elements) - 1, -1, -1):
            element_tag, opened_styles = self._style_elements[index]
            if element_tag != tag:
                continue
            del self._style_elements[index]
            end = len(self.text)
            for style, start in opened_styles:
                if start < end:
                    self.styles.append((start, end, style))
            break

        # Le retour de fin de bloc ne fait pas partie du style du contenu.
        if tag in self.BLOCK_TAGS and self.text and not self.text.endswith("\n"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not data:
            return
        if self._style_block_depth:
            self._style_chunks.append(data)
            return
        if self._head_depth or self._ignored_content_depth:
            return
        # L'indentation entre deux blocs HTML n'est pas du texte rendu par le
        # navigateur. Elle ne doit donc pas créer de paragraphes vides.
        if data.isspace() and ("\n" in data or "\r" in data):
            if not self.text or self.text.endswith("\n"):
                return
        start = len(self.text)
        self.parts.append(data)
        href = self._current_href()
        if href:
            end = start + len(data)
            self.links.append((start, end, href))

    @property
    def text(self):
        return "".join(self.parts)

    def _current_href(self):
        for href in reversed(self._href_stack):
            if href:
                return href
        return ""

    @staticmethod
    def _parse_style_declarations(css):
        """Extrait les propriétés typographiques utiles d'une déclaration CSS."""
        styles = {}
        for declaration in str(css or "").split(";"):
            if ":" not in declaration:
                continue
            property_name, value = declaration.split(":", 1)
            property_name = property_name.strip().lower()
            value = re.sub(r"\s*!important\s*$", "", value.strip().lower())
            if property_name == "font-weight":
                if value in {"bold", "bolder"}:
                    styles["bold"] = True
                elif value in {"normal", "lighter"}:
                    styles["bold"] = False
                elif value.isdigit():
                    styles["bold"] = int(value) >= 600
            elif property_name == "font-style":
                if value in {"italic", "oblique"}:
                    styles["italic"] = True
                elif value == "normal":
                    styles["italic"] = False
        return styles

    @staticmethod
    def _apply_css_styles(opened_styles, css_styles):
        """Applique les activations et désactivations provenant de la cascade CSS."""
        for style, enabled in css_styles.items():
            if enabled:
                opened_styles.add(style)
            else:
                opened_styles.discard(style)

    def _parse_css_rules(self, css):
        """Indexe les règles de classe simples définies dans une balise style."""
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        for selectors, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            parsed_styles = self._parse_style_declarations(declarations)
            if not parsed_styles:
                continue
            for selector in selectors.split(","):
                for class_name in re.findall(r"\.([A-Za-z_][\w-]*)", selector):
                    self._css_class_styles.setdefault(class_name, {}).update(parsed_styles)

    def close_open_styles(self):
        """Ferme proprement les styles laissés ouverts par un HTML incomplet."""
        end = len(self.text)
        for _tag, opened_styles in self._style_elements:
            for style, start in opened_styles:
                if start < end:
                    self.styles.append((start, end, style))
        self._style_elements.clear()


def _extract_clipboard_html_fragment(raw_html):
    """Retourne le fragment HTML utile depuis le format HTML du presse-papiers."""
    if not raw_html:
        return ""

    start_marker = "<!--StartFragment-->"
    end_marker = "<!--EndFragment-->"
    if start_marker in raw_html and end_marker in raw_html:
        start = raw_html.find(start_marker) + len(start_marker)
        end = raw_html.find(end_marker)
        if start < end:
            return raw_html[start:end]

    offsets = {}
    for key in ("StartFragment", "EndFragment"):
        match = re.search(rf"{key}:(\d+)", raw_html)
        if match:
            offsets[key] = int(match.group(1))
    if "StartFragment" in offsets and "EndFragment" in offsets:
        raw_bytes = raw_html.encode("utf-8", errors="replace")
        start = offsets["StartFragment"]
        end = offsets["EndFragment"]
        if 0 <= start < end <= len(raw_bytes):
            return raw_bytes[start:end].decode("utf-8", errors="replace")

    html_start = raw_html.lower().find("<html")
    if html_start >= 0:
        return raw_html[html_start:]
    body_start = raw_html.lower().find("<body")
    if body_start >= 0:
        return raw_html[body_start:]
    return raw_html


def _parse_clipboard_html(raw_html):
    """Convertit le HTML du presse-papiers en texte, liens et styles."""
    fragment = _extract_clipboard_html_fragment(raw_html)
    parser = ClipboardHtmlParser()
    try:
        parser.feed(fragment)
        parser.close()
        parser.close_open_styles()
    except Exception:
        return "", [], []

    raw_text = parser.text
    text = raw_text.strip()
    if not text:
        return "", [], []

    leading_whitespace = len(raw_text) - len(raw_text.lstrip())
    links = []
    for start, end, href in parser.links:
        start -= leading_whitespace
        end -= leading_whitespace
        if href and 0 <= start < end <= len(text):
            links.append((start, end, href))
    styles = []
    for start, end, style in parser.styles:
        start -= leading_whitespace
        end -= leading_whitespace
        if style in RICH_STYLE_NAMES and 0 <= start < end <= len(text):
            styles.append((start, end, style))
    return text, links, styles


def _escape_markdown_link_text(text):
    """Échappe le texte visible d'un lien Markdown."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _html_links_to_markdown(text, links):
    """Remplace les liens HTML extraits par des liens Markdown visibles."""
    markdown_text = text
    for start, end, href in sorted(links, key=lambda item: item[0], reverse=True):
        label = markdown_text[start:end]
        if not label.strip() or not href:
            continue
        replacement = f"[{_escape_markdown_link_text(label)}]({href})"
        markdown_text = markdown_text[:start] + replacement + markdown_text[end:]
    return markdown_text


def _markdown_links_to_text(markdown_text):
    """Convertit les liens Markdown en texte visible + ranges de liens."""
    parts = []
    links = []
    last_end = 0
    for match in MARKDOWN_LINK_PATTERN.finditer(markdown_text):
        parts.append(markdown_text[last_end:match.start()])
        label = match.group(1)
        start = sum(len(part) for part in parts)
        parts.append(label)
        end = start + len(label)
        links.append((start, end, match.group(2)))
        last_end = match.end()
    parts.append(markdown_text[last_end:])
    return "".join(parts), links


MARKDOWN_STYLE_PATTERNS = (
    (re.compile(r"(?<!\*)\*\*\*(?=\S)(.+?)(?<=\S)\*\*\*(?!\*)", re.DOTALL), ("bold", "italic")),
    (re.compile(r"(?<!_)___(?=\S)(.+?)(?<=\S)___(?!_)", re.DOTALL), ("bold", "italic")),
    (re.compile(r"(?<!\*)\*\*(?=\S)(.+?)(?<=\S)\*\*(?!\*)", re.DOTALL), ("bold",)),
    (re.compile(r"(?<!_)__(?=\S)(.+?)(?<=\S)__(?!_)", re.DOTALL), ("bold",)),
    (re.compile(r"(?<!\*)\*(?=\S)(.+?)(?<=\S)\*(?!\*)", re.DOTALL), ("italic",)),
    (re.compile(r"(?<![_\w])_(?=\S)(.+?)(?<=\S)_(?![_\w])", re.DOTALL), ("italic",)),
)


def _markdown_emphasis_to_text(markdown_text):
    """Retire les marqueurs Markdown et retourne les plages de style."""
    occupied = [False] * len(markdown_text)
    removed = set()
    original_styles = []

    for pattern, style_names in MARKDOWN_STYLE_PATTERNS:
        for match in pattern.finditer(markdown_text):
            if any(occupied[match.start():match.end()]):
                continue
            content_start, content_end = match.span(1)
            removed.update(range(match.start(), content_start))
            removed.update(range(content_end, match.end()))
            for index in range(match.start(), match.end()):
                occupied[index] = True
            for style in style_names:
                original_styles.append((content_start, content_end, style))

    clean_parts = []
    boundary_map = [0] * (len(markdown_text) + 1)
    for index, character in enumerate(markdown_text):
        boundary_map[index] = len(clean_parts)
        if index not in removed:
            clean_parts.append(character)
        boundary_map[index + 1] = len(clean_parts)

    styles = [
        (boundary_map[start], boundary_map[end], style)
        for start, end, style in original_styles
        if boundary_map[start] < boundary_map[end]
    ]
    return "".join(clean_parts), styles, boundary_map


def _markdown_headings_to_text(markdown_text):
    """Retire les préfixes de titres Markdown et retourne leurs plages."""
    removed = set()
    original_styles = []
    pattern = re.compile(r"(?m)^ {0,3}(#{1,6})[ \t]+(?=\S)")

    for match in pattern.finditer(markdown_text):
        content_start = match.end()
        content_end = markdown_text.find("\n", content_start)
        if content_end < 0:
            content_end = len(markdown_text)
        if content_start >= content_end:
            continue
        removed.update(range(match.start(), match.end()))
        original_styles.append(
            (content_start, content_end, f"heading{len(match.group(1))}")
        )

    clean_parts = []
    boundary_map = [0] * (len(markdown_text) + 1)
    for index, character in enumerate(markdown_text):
        boundary_map[index] = len(clean_parts)
        if index not in removed:
            clean_parts.append(character)
        boundary_map[index + 1] = len(clean_parts)

    styles = [
        (boundary_map[start], boundary_map[end], style)
        for start, end, style in original_styles
        if boundary_map[start] < boundary_map[end]
    ]
    return "".join(clean_parts), styles, boundary_map


def _markdown_to_rich_text(markdown_text):
    """Convertit les liens, emphases et titres Markdown en texte riche."""
    text_with_emphasis, links = _markdown_links_to_text(markdown_text)
    text_with_headings, styles, emphasis_map = _markdown_emphasis_to_text(text_with_emphasis)
    clean_text, heading_styles, heading_map = _markdown_headings_to_text(text_with_headings)
    adjusted_links = [
        (heading_map[emphasis_map[start]], heading_map[emphasis_map[end]], url)
        for start, end, url in links
        if heading_map[emphasis_map[start]] < heading_map[emphasis_map[end]]
    ]
    adjusted_styles = [
        (heading_map[start], heading_map[end], style)
        for start, end, style in styles
        if heading_map[start] < heading_map[end]
    ]
    return clean_text, adjusted_links, adjusted_styles + heading_styles


def _rich_text_to_markdown(text, links=None, styles=None):
    """Sérialise les plages riches en Markdown sans modifier le texte affiché."""
    openings = {}
    closings = {}
    heading_prefixes = {}

    for start, end, style in styles or []:
        if not (0 <= start < end <= len(text)):
            continue
        if style in HEADING_STYLES:
            if start == 0 or text[start - 1] == "\n":
                level = int(style[len("heading"):])
                heading_prefixes.setdefault(start, []).append(f"{'#' * level} ")
            continue
        if style not in {"bold", "italic"}:
            continue
        marker = "**" if style == "bold" else "*"
        priority = 1 if style == "bold" else 2
        openings.setdefault(start, []).append((end, priority, marker))
        closings.setdefault(end, []).append((start, -priority, marker))

    for start, end, url in links or []:
        if not url or not (0 <= start < end <= len(text)):
            continue
        openings.setdefault(start, []).append((end, 0, "["))
        closings.setdefault(end, []).append((start, 3, f"]({url})"))

    parts = []
    for position in range(len(text) + 1):
        for _start, _priority, marker in sorted(
            closings.get(position, []),
            key=lambda item: (-item[0], item[1]),
        ):
            parts.append(marker)
        for marker in sorted(heading_prefixes.get(position, []), key=len):
            parts.append(marker)
        for _end, _priority, marker in sorted(
            openings.get(position, []),
            key=lambda item: (-item[0], item[1]),
        ):
            parts.append(marker)
        if position < len(text):
            parts.append(text[position])
    return "".join(parts)


def _get_windows_clipboard_html():
    """Lit le format HTML natif du presse-papiers Windows."""
    if sys.platform != "win32":
        return ""

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.RegisterClipboardFormatW.argtypes = [ctypes.c_wchar_p]
    user32.RegisterClipboardFormatW.restype = ctypes.c_uint
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_bool
    user32.GetClipboardData.argtypes = [ctypes.c_uint]
    user32.GetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.restype = ctypes.c_bool
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalSize.argtypes = [ctypes.c_void_p]
    kernel32.GlobalSize.restype = ctypes.c_size_t

    html_format = user32.RegisterClipboardFormatW("HTML Format")
    if not html_format:
        return ""

    if not user32.OpenClipboard(None):
        return ""
    try:
        handle = user32.GetClipboardData(html_format)
        if not handle:
            return ""

        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            return ""
        try:
            size = kernel32.GlobalSize(handle)
            if not size:
                return ""
            data = ctypes.string_at(pointer, size)
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()

    return data.rstrip(b"\x00").decode("utf-8", errors="replace")


def _config_candidates():
    """Emplacements automatiques du fichier de configuration obligatoire."""
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent

    candidates = [
        Path(os.environ["TRANSLATOR_CONFIG"]) if os.environ.get("TRANSLATOR_CONFIG") else None,
        app_dir / ".translator_config.json",
        Path.cwd() / ".translator_config.json",
    ]

    seen = set()
    for path in candidates:
        if path is None:
            continue
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            yield path


class ConfigError(Exception):
    """Erreur empêchant le démarrage avec la configuration demandée."""


def _choose_config_file(error_message=None):
    """Demande à l'utilisateur de sélectionner un fichier de configuration."""
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        if error_message:
            messagebox.showerror("Configuration invalide", error_message, parent=root)
        selected_path = filedialog.askopenfilename(
            parent=root,
            title="Sélectionnez le fichier .translator_config.json",
            filetypes=[("Configuration JSON", "*.json"), ("Tous les fichiers", "*.*")],
        )
        if not selected_path:
            messagebox.showerror(
                "Configuration requise",
                "Un fichier .translator_config.json valide est obligatoire pour démarrer l'application.",
                parent=root,
            )
            raise ConfigError("Sélection du fichier de configuration annulée.")
        return Path(selected_path)
    except tk.TclError as exc:
        raise ConfigError(
            "Aucun fichier .translator_config.json détecté et le sélecteur de fichier "
            f"ne peut pas être affiché : {exc}"
        ) from exc
    finally:
        if root is not None:
            root.destroy()


def _normalize_server_url(server_url):
    """Accepte une URL Ollama complète ou seulement l'URL de base du serveur."""
    server_url = str(server_url or "").strip().rstrip("/")
    if not server_url.endswith("/api/chat"):
        server_url = f"{server_url}/api/chat"
    return server_url


def _as_bool(value):
    """Interprète proprement les booléens venant du JSON ou d'anciennes configs."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "oui", "on"}
    return bool(value)


class PromptValues(dict):
    """Préserve les variables inconnues dans les prompts personnalisés."""

    def __missing__(self, key):
        return "{" + key + "}"


def _read_config(path):
    """Lit et valide les paramètres obligatoires d'un fichier JSON."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except Exception as exc:
        raise ConfigError(f"Impossible de lire la configuration {path} : {exc}") from exc

    if not isinstance(user_config, dict):
        raise ConfigError(f"La configuration {path} doit contenir un objet JSON.")

    server_url = user_config.get("server_url")
    default_model = user_config.get("default_model") or user_config.get("model")
    invalid_fields = []
    if not isinstance(server_url, str) or not server_url.strip():
        invalid_fields.append("server_url")
    if not isinstance(default_model, str) or not default_model.strip():
        invalid_fields.append("default_model")
    if invalid_fields:
        fields = ", ".join(invalid_fields)
        raise ConfigError(
            f"Configuration {path} incomplète ou invalide : champ(s) obligatoire(s) : {fields}."
        )

    user_prompts = user_config.get("prompts")
    prompts = {}
    if isinstance(user_prompts, dict):
        for key, value in user_prompts.items():
            prompt_key = PROMPT_KEY_ALIASES.get(str(key).strip().lower())
            if prompt_key and isinstance(value, str) and value.strip():
                prompts[prompt_key] = value
    missing_prompts = [key for key in REQUIRED_PROMPTS if key not in prompts]
    if missing_prompts:
        names = ", ".join(missing_prompts)
        raise ConfigError(
            f"Configuration {path} incomplète : prompt(s) obligatoire(s) manquant(s) : {names}."
        )

    user_languages = user_config.get("languages")
    languages = {}
    if isinstance(user_languages, dict):
        for code, label in user_languages.items():
            normalized_code = str(code).strip().lower()
            if normalized_code and isinstance(label, str) and label.strip():
                languages[normalized_code] = label.strip()
    missing_languages = [code for code in REQUIRED_LANGUAGES if code not in languages]
    if missing_languages:
        codes = ", ".join(missing_languages)
        raise ConfigError(
            f"Configuration {path} incomplète : langue(s) obligatoire(s) manquante(s) : {codes}."
        )

    config = {
        key: value
        for key, value in user_config.items()
        if value is not None and not str(key).startswith("_comment")
    }
    config["server_url"] = server_url.strip()
    config["default_model"] = default_model.strip()
    config["prompts"] = prompts
    config["languages"] = languages
    config.pop("models", None)
    config["_config_source"] = str(path)

    return config


def load_config(config_path=None, ask_if_missing=True):
    """Charge la configuration obligatoire ou demande son emplacement."""
    path = Path(config_path) if config_path is not None else next(
        (candidate for candidate in _config_candidates() if candidate.is_file()),
        None,
    )

    while True:
        if path is None:
            if not ask_if_missing:
                raise ConfigError("Aucun fichier .translator_config.json détecté.")
            path = _choose_config_file()
        try:
            config = _read_config(path)
            break
        except ConfigError as exc:
            if not ask_if_missing:
                raise
            path = _choose_config_file(str(exc))

    config["server_url"] = _normalize_server_url(config.get("server_url"))
    config["think"] = _as_bool(config.get("think", False))
    config["api_key"] = str(config.get("api_key", "")).strip()
    config["api_key_header"] = str(config.get("api_key_header", "Authorization")).strip() or "Authorization"
    config["hide_window_on_start"] = _as_bool(
        config.get(
            "hide_window_on_start",
            config.get("masquer_fenetre_au_lancement", False),
        )
    )

    default_model = config["default_model"]
    config["default_model"] = default_model
    config["model"] = default_model

    return config


def _acquire_single_instance_mutex():
    """Empêche plusieurs instances de l'application sous Windows."""
    global _APP_MUTEX_HANDLE
    if os.name != "nt":
        return True

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = (ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p)
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel32.CloseHandle.restype = ctypes.c_bool

    ctypes.set_last_error(0)
    handle = kernel32.CreateMutexW(None, False, APP_MUTEX_NAME)
    if not handle:
        return True
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(handle)
        return False

    _APP_MUTEX_HANDLE = handle
    return True


def _notify_already_running():
    """Informe l'utilisateur qu'une instance existe déjà."""
    if START_HIDDEN:
        return
    root = tk.Tk()
    try:
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo(
            APP_NAME,
            "Traducteur est déjà lancé. Utilisez son icône dans la barre système pour l'afficher.",
            parent=root,
        )
    finally:
        root.destroy()


if __name__ == "__main__" and not _acquire_single_instance_mutex():
    _notify_already_running()
    raise SystemExit(0)


try:
    CONFIG = load_config()
except ConfigError as exc:
    print(f"[ERREUR] {exc}", file=sys.stderr)
    raise SystemExit(1) from exc


def _request_headers():
    """Construit les en-têtes HTTP optionnels pour les endpoints protégés."""
    api_key = CONFIG.get("api_key", "")
    if not api_key:
        return None

    header_name = CONFIG.get("api_key_header") or "Authorization"
    if header_name.lower() == "authorization":
        return {header_name: f"Bearer {api_key}"}
    return {header_name: api_key}


class TranslatorApp(tk.Tk if not CTK_SUPPORT else ctk.CTk):
    def __init__(self):
        super().__init__()
        if CTK_SUPPORT:
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1000x600")
        self.resizable(True, True)

        # État
        self.models = self._get_models()
        self.history = []
        self.is_translating = False
        self.word_count = 0
        self.translation_time = 0.0
        self.start_time = 0.0
        self.output_queue = queue.Queue()
        self.stop_event = threading.Event()
        
        # Gestion des threads
        self.running = True
        self.hotkey_thread = None
        self.hotkey_listener = None
        self.tray_icon = None
        self._is_closing = False
        self._last_global_ctrl_c_time = 0.0
        self._last_clipboard_trigger_time = 0.0
        self.translation_thread = None
        self._ui_thread_id = threading.get_ident()
        self._link_refresh_after_id = None
        self._link_tag_counter = 0
        self._link_tag_urls = {}

        # Variables
        self.mode = tk.StringVar(value=MODE_LABELS["translate"])
        default_model = CONFIG["default_model"]
        self.model_var = tk.StringVar(value=default_model if default_model in self.models else self.models[0])
        self.source_lang = tk.StringVar(value="auto")
        self.target_lang = tk.StringVar(value="fr")
        self.target_lookup_selection = ""

        self._setup_ui()
        self._mode_trace_id = self.mode.trace_add("write", self._update_action_button_label)
        self._update_action_button_label()
        self._setup_bindings()
        self._process_queue()
        self._show_config_status()
        
        # La croix masque la fenêtre: l'app reste en veille pour le raccourci global
        self.protocol("WM_DELETE_WINDOW", self._hide_window)
        
        # Setup tray si disponible
        if TRAY_SUPPORT:
            self._setup_tray()
        
        # Raccourci global si disponible
        if KEYBOARD_SUPPORT:
            self._start_global_hotkey()

        hide_on_start = START_HIDDEN or CONFIG.get("hide_window_on_start")
        if hide_on_start and (TRAY_SUPPORT or KEYBOARD_SUPPORT):
            self.after(0, self._hide_window)
        elif hide_on_start:
            self.set_status_text(
                self.status_label,
                "Démarrage masqué ignoré: tray et raccourcis globaux indisponibles",
            )

    def _show_config_status(self):
        """Affiche rapidement quelle configuration est utilisée."""
        label = f"Config: {Path(CONFIG['_config_source']).name}"
        self.set_status_text(self.status_label, f"{label} - {CONFIG['server_url']}")

    def _hide_window(self):
        """Masquer la fenêtre sans quitter l'application."""
        if self._is_closing:
            return
        self.withdraw()

    def _on_closing(self):
        """Quitter l'application proprement"""
        if self._is_closing:
            return
        self._is_closing = True
        self.running = False
        self.stop_event.set()

        # Arrêter le listener pynput: sinon son thread peut garder le processus vivant
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
        
        # Arrêter le hotkey listener si actif
        if self.hotkey_thread and self.hotkey_thread.is_alive():
            try:
                self.hotkey_thread.join(timeout=1)
            except Exception:
                pass
        
        # Arrêter le tray si actif
        if TRAY_SUPPORT and self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        
        # Quitter l'application
        try:
            self.quit()
        finally:
            self.destroy()

    def _setup_tray(self):
        """Créer une icône dans le system tray"""
        if not TRAY_SUPPORT:
            return  # Tray non disponible, ignorer
        
        try:
            # Créer une image minimaliste
            image = Image.new('RGB', (64, 64), color=(0, 122, 204))
            menu = (
                pystray.MenuItem("Afficher", self._show_window),
                pystray.MenuItem("Traduire le presse-papier", self._translate_clipboard),
                pystray.MenuItem("Quitter", self._quit_app),
            )
            self.tray_icon = pystray.Icon("traducteur", image, f"{APP_NAME} {APP_VERSION}", menu)
            
            # Démarrer le tray dans un thread
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
        except Exception as e:
            print(f"Erreur setup tray: {e}")

    def _show_window(self, icon=None, item=None):
        """Afficher la fenêtre"""
        self._run_on_ui_thread(self._show_window_now)

    def _show_window_now(self):
        """Afficher la fenêtre depuis le thread Tkinter."""
        if self._is_closing:
            return
        try:
            self.state("normal")
        except Exception:
            pass
        self.deiconify()
        self.lift()
        self.focus_force()
        # Force brièvement la fenêtre au premier plan après un withdraw sous Windows.
        try:
            self.attributes("-topmost", True)
            self.after(250, lambda: self.attributes("-topmost", False))
        except Exception:
            pass

    def _run_on_ui_thread(self, callback, *args):
        """Planifier une action Tkinter depuis n'importe quel thread."""
        if threading.get_ident() == self._ui_thread_id:
            callback(*args)
        else:
            self.output_queue.put(("call", (callback, args)))

    def _translate_clipboard(self, icon=None, item=None):
        """Traduire le contenu du presse-papier"""
        if self._is_closing:
            return
        now = time.time()
        if now - self._last_clipboard_trigger_time < 1.0:
            return
        self._last_clipboard_trigger_time = now

        self._run_on_ui_thread(self._schedule_clipboard_translation)

    def _schedule_clipboard_translation(self):
        """Attendre que le presse-papier soit à jour avant la traduction."""
        self.set_status_text(self.status_label, "Lecture du presse-papier...")
        self.after(CLIPBOARD_SETTLE_DELAY_MS, self._load_clipboard_and_translate)

    def _load_clipboard_and_translate(self):
        """Charger le presse-papier, afficher la fenêtre, puis lancer la traduction."""
        def do_translate():
            try:
                clipboard_text, clipboard_links, clipboard_styles = self._get_rich_clipboard_content()
                if not clipboard_text:
                    clipboard_text = self.clipboard_get()
                    clipboard_links = []
                    clipboard_styles = []
                if not clipboard_text.strip():
                    messagebox.showwarning("Attention", "Le presse-papier est vide")
                    return
                
                self.source_text.delete("1.0", tk.END)
                self.source_text.mark_set(tk.INSERT, "1.0")
                self._insert_text_with_links(
                    self.source_text,
                    clipboard_text,
                    clipboard_links,
                    clipboard_styles,
                )
                self.update_word_count()
                self._schedule_link_refresh()
                self._show_window_now()
                self.set_status_text(self.status_label, "Traduction automatique...")
                self.after(AUTO_TRANSLATE_DELAY_MS, self._start_clipboard_translation)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'accéder au presse-papier:\n{str(e)}")

        do_translate()

    def _start_clipboard_translation(self):
        """Démarrer la traduction après affichage de la fenêtre."""
        if self.is_translating and self.translation_thread and not self.translation_thread.is_alive():
            self.is_translating = False
        if self.is_translating:
            self.stop_event.set()
            self.set_status_text(self.status_label, "Arrêt de la traduction précédente...")
            self.after(200, self._start_clipboard_translation)
            return
        self.translate()

    def _quit_app(self, icon=None, item=None):
        """Quitter l'application"""
        self._on_closing()

    def _start_global_hotkey(self):
        """Écouter les raccourcis globaux Ctrl+Shift+C et double Ctrl+C"""
        self.hotkey_thread = threading.Thread(target=self._hotkey_listener, daemon=True)
        self.hotkey_thread.start()

    def _hotkey_listener(self):
        """Écouter les touches globales"""
        if not KEYBOARD_SUPPORT:
            return  # Keyboard support non disponible
        
        try:
            # État des touches
            state = {"ctrl": False, "shift": False}

            ctrl_keys = tuple(
                k for k in (
                    getattr(keyboard.Key, "ctrl", None),
                    getattr(keyboard.Key, "ctrl_l", None),
                    getattr(keyboard.Key, "ctrl_r", None),
                )
                if k is not None
            )
            shift_keys = tuple(
                k for k in (
                    getattr(keyboard.Key, "shift", None),
                    getattr(keyboard.Key, "shift_l", None),
                    getattr(keyboard.Key, "shift_r", None),
                )
                if k is not None
            )

            def is_ctrl_key(key):
                return key in ctrl_keys

            def is_shift_key(key):
                return key in shift_keys

            def is_c_key(key):
                # Sous Windows, pynput peut exposer Ctrl+C comme '\x03' ou VK 67 plutôt que 'c'.
                char = getattr(key, "char", None)
                vk = getattr(key, "vk", None)
                return (bool(char) and char.lower() == "c") or char == "\x03" or vk == 67
            
            def on_press(key):
                if not self.running:
                    return False
                try:
                    # Détecter Ctrl
                    if is_ctrl_key(key):
                        state["ctrl"] = True
                    # Détecter Shift
                    elif is_shift_key(key):
                        state["shift"] = True
                    # Détecter C (en minuscules ou majuscules)
                    elif is_c_key(key):
                        if state["ctrl"] and state["shift"]:
                            # CTRL+Shift+C détecté
                            self._translate_clipboard()
                        elif state["ctrl"]:
                            # Double Ctrl+C détecté
                            now = time.time()
                            if now - self._last_global_ctrl_c_time < 0.6:
                                self._translate_clipboard()
                            self._last_global_ctrl_c_time = now
                except (AttributeError, KeyError):
                    pass
            
            def on_release(key):
                if not self.running:
                    return False
                try:
                    # Réinitialiser Ctrl
                    if is_ctrl_key(key):
                        state["ctrl"] = False
                    # Réinitialiser Shift
                    elif is_shift_key(key):
                        state["shift"] = False
                except (AttributeError, KeyError):
                    pass
            
            self.hotkey_listener = Listener(on_press=on_press, on_release=on_release)
            self.hotkey_listener.start()
            self.hotkey_listener.join()
                
        except Exception as e:
            if self.running:
                print(f"Erreur hotkey listener: {e}")

    def _process_queue(self):
        """Traite les messages de la queue (thread-safe)"""
        if not self.running:
            return
        try:
            while True:
                msg_type, data = self.output_queue.get_nowait()
                if msg_type == "insert":
                    self.target_text.insert(tk.END, data)
                    self.target_text.see(tk.END)
                    self._schedule_link_refresh()
                elif msg_type == "status":
                    self.set_status_text(self.status_label, data)
                elif msg_type == "time":
                    self.set_status_text(self.time_label, data)
                elif msg_type == "call":
                    callback, args = data
                    callback(*args)
                elif msg_type == "history":
                    self._add_history_item(data)
        except queue.Empty:
            pass
        if self.running:
            self.after(50, self._process_queue)

    def _get_models(self):
        """Récupère les modèles disponibles"""
        try:
            response = requests.get(
                f"{CONFIG['server_url'].replace('/api/chat', '/api/tags')}",
                headers=_request_headers(),
                timeout=10,
            )
            response.raise_for_status()
            server_models = [m["name"] for m in response.json().get("models", [])]
            if server_models:
                return server_models
        except Exception:
            pass
        return [CONFIG["default_model"]]

    def _setup_ui(self):
        """Configure l'interface"""
        if CTK_SUPPORT:
            self._setup_ctk_ui()
        else:
            self._setup_ttk_ui()

    def _setup_ctk_ui(self):
        """Interface CustomTkinter moderne"""
        # Menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Importer", command=self.import_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Exporter", command=self.export_translation, accelerator="Ctrl+S")
        file_menu.add_separator()
        self.history_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Historique", menu=self.history_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self._on_closing)

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Barre d'outils
        toolbar = ctk.CTkFrame(main_frame, fg_color="transparent", height=40)
        toolbar.pack(fill=tk.X, pady=(0, 12))
        toolbar.pack_propagate(False)

        # Contrôles
        ctk.CTkLabel(toolbar, text="Mode:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 3))
        ctk.CTkOptionMenu(toolbar, variable=self.mode, values=list(MODE_LABELS.values()),
                         width=105, height=32, font=ctk.CTkFont(size=12),
                         fg_color="#f8f9fa", text_color="#495057",
                         button_color="#e9ecef", button_hover_color="#dee2e6",
                         dropdown_font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 12))

        ctk.CTkLabel(toolbar, text="Modèle:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 3))
        ctk.CTkOptionMenu(toolbar, variable=self.model_var, values=self.models,
                         width=140, height=32, font=ctk.CTkFont(size=12),
                         fg_color="#f8f9fa", text_color="#495057",
                         button_color="#e9ecef", button_hover_color="#dee2e6",
                         dropdown_font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 15))

        ctk.CTkLabel(toolbar, text="De:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 3))
        ctk.CTkOptionMenu(toolbar, variable=self.source_lang, values=list(CONFIG["languages"]),
                         width=85, height=32, font=ctk.CTkFont(size=12),
                         fg_color="#f8f9fa", text_color="#495057",
                         button_color="#e9ecef", button_hover_color="#dee2e6",
                         dropdown_font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 8))

        ctk.CTkLabel(toolbar, text="Vers:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 3))
        ctk.CTkOptionMenu(toolbar, variable=self.target_lang,
                         values=[code for code in CONFIG["languages"] if code != "auto"],
                         width=85, height=32, font=ctk.CTkFont(size=12),
                         fg_color="#f8f9fa", text_color="#495057",
                         button_color="#e9ecef", button_hover_color="#dee2e6",
                         dropdown_font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 8))

        # Boutons
        ctk.CTkButton(toolbar, text="<>", command=self.swap_languages,
                     width=35, height=32, font=ctk.CTkFont(size=12),
                     fg_color="#6c757d", hover_color="#5a6268").pack(side=tk.LEFT, padx=(8, 8))

        self.action_button = ctk.CTkButton(
            toolbar,
            text=self.mode.get(),
            command=self.translate,
            width=80,
            height=32,
            fg_color="#007acc",
            hover_color="#005999",
            font=ctk.CTkFont(size=12),
        )
        self.action_button.pack(side=tk.LEFT, padx=(0, 10))

        # Zones de texte
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        # Calcul dynamique de la largeur
        main_frame.update_idletasks()
        total_width = main_frame.winfo_width() or 1000
        half_width = total_width // 2

        # Source
        source_frame = ctk.CTkFrame(paned, fg_color="#f8f9fa", corner_radius=8)
        ctk.CTkLabel(source_frame, text="Texte source", font=ctk.CTkFont(size=12)).pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.source_text = tk.Text(source_frame, wrap=tk.WORD, undo=True, font=("Arial", 11),
                                  bg="#ffffff", fg="#333333", insertbackground="#333333",
                                  relief="flat", padx=10, pady=10)
        scrollbar_source = ctk.CTkScrollbar(source_frame, command=self.source_text.yview)
        self.source_text.config(yscrollcommand=scrollbar_source.set)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=(0, 10))
        scrollbar_source.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(10, 10))
        paned.add(source_frame, width=half_width, stretch="always")

        # Cible
        target_frame = ctk.CTkFrame(paned, fg_color="#f8f9fa", corner_radius=8)
        target_header = ctk.CTkFrame(target_frame, fg_color="transparent")
        target_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        ctk.CTkLabel(target_header, text="Traduction", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT)
        target_actions = ctk.CTkFrame(target_header, fg_color="transparent")
        target_actions.pack(side=tk.RIGHT)
        ctk.CTkButton(target_actions, text="Copier", command=self.copy_translation,
                     width=62, height=26, fg_color="#198754", hover_color="#146c43",
                     font=ctk.CTkFont(size=11)).pack(side=tk.RIGHT)
        self.target_alternatives_button = ctk.CTkButton(
            target_actions,
            text="Alternatives",
            command=self.lookup_target_selection,
            width=88,
            height=26,
            fg_color="#6f42c1",
            hover_color="#5a32a3",
            font=ctk.CTkFont(size=11),
        )
        self.target_alternatives_button_visible = False
        self.target_text = tk.Text(target_frame, wrap=tk.WORD, font=("Arial", 11),
                                  bg="#ffffff", fg="#333333", insertbackground="#333333",
                                  relief="flat", padx=10, pady=10)
        scrollbar_target = ctk.CTkScrollbar(target_frame, command=self.target_text.yview)
        self.target_text.config(yscrollcommand=scrollbar_target.set)
        self.target_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=(0, 10))
        scrollbar_target.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(10, 10))
        paned.add(target_frame, width=half_width, stretch="always")

        # Barre de statut
        status_frame = ctk.CTkFrame(main_frame, fg_color="#e9ecef", height=35, corner_radius=6)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(status_frame, text="Prêt",
                                        font=ctk.CTkFont(size=11), text_color="#495057")
        self.status_label.pack(side=tk.LEFT, padx=15, pady=2)

        metrics_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        metrics_frame.pack(side=tk.RIGHT, padx=15)

        self.word_label = ctk.CTkLabel(metrics_frame, text="Mots: 0",
                                      font=ctk.CTkFont(size=11), text_color="#495057")
        self.word_label.pack(side=tk.LEFT, padx=(0, 15))

        self.time_label = ctk.CTkLabel(metrics_frame, text="Temps: 0.0s",
                                      font=ctk.CTkFont(size=11), text_color="#495057")
        self.time_label.pack(side=tk.LEFT)

    def _setup_ttk_ui(self):
        """Interface Tkinter classique (fallback)"""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#f0f0f0", font=("Arial", 10))
        style.configure("TCombobox", padding=5, font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 10))

        # Menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Importer", command=self.import_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Exporter", command=self.export_translation, accelerator="Ctrl+S")
        file_menu.add_separator()
        self.history_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Historique", menu=self.history_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self._on_closing)

        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Barre d'outils
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(toolbar, textvariable=self.mode,
                     values=list(MODE_LABELS.values()),
                     state="readonly", width=12).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(toolbar, text="Modèle:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(toolbar, textvariable=self.model_var,
                     values=self.models, state="readonly", width=20).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(toolbar, text="De:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(toolbar, textvariable=self.source_lang,
                     values=list(CONFIG["languages"]),
                     state="readonly", width=10).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(toolbar, text="Vers:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(toolbar, textvariable=self.target_lang,
                     values=[code for code in CONFIG["languages"] if code != "auto"],
                     state="readonly", width=10).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="⟷", command=self.swap_languages).pack(side=tk.LEFT, padx=(10, 5))
        self.action_button = ttk.Button(toolbar, text=self.mode.get(), command=self.translate)
        self.action_button.pack(side=tk.LEFT, padx=(5, 5))

        # Zones de texte
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        source_frame = ttk.LabelFrame(paned, text="Texte source")
        self.source_text = tk.Text(source_frame, wrap=tk.WORD, undo=True, font=("Arial", 11))
        scrollbar_source = ttk.Scrollbar(source_frame, command=self.source_text.yview)
        self.source_text.config(yscrollcommand=scrollbar_source.set)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_source.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(source_frame)

        target_frame = ttk.LabelFrame(paned, text="Traduction")
        target_header = ttk.Frame(target_frame)
        target_header.pack(fill=tk.X, padx=4, pady=(0, 4))
        ttk.Button(target_header, text="Copier", command=self.copy_translation).pack(side=tk.RIGHT)
        self.target_alternatives_button = ttk.Button(
            target_header,
            text="Alternatives",
            command=self.lookup_target_selection,
        )
        self.target_alternatives_button_visible = False
        self.target_text = tk.Text(target_frame, wrap=tk.WORD, font=("Arial", 11))
        scrollbar_target = ttk.Scrollbar(target_frame, command=self.target_text.yview)
        self.target_text.config(yscrollcommand=scrollbar_target.set)
        self.target_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_target.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(target_frame)

        # Barre de statut
        status_frame = ttk.Frame(main_frame, relief="sunken")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame, text="Prêt")
        self.status_label.pack(side=tk.LEFT)

        self.word_label = ttk.Label(status_frame, text="Mots: 0")
        self.word_label.pack(side=tk.RIGHT, padx=(0, 10))

        self.time_label = ttk.Label(status_frame, text="Temps: 0.0s")
        self.time_label.pack(side=tk.RIGHT)

    def _setup_bindings(self):
        """Configure les raccourcis clavier"""
        self._setup_link_tags()
        self.bind('<Control-o>', lambda e: self.import_file())
        self.bind('<Control-s>', lambda e: self.export_translation())
        self.bind('<Control-Return>', lambda e: self.translate())
        self.bind('<Control-Shift-C>', lambda e: self.copy_translation())
        self.bind('<Control-l>', lambda e: self.lookup_selection())
        self.source_text.bind('<KeyRelease>', self.update_word_count)
        self.source_text.bind('<ButtonRelease-1>', self._schedule_selection_action_update)
        self.source_text.bind('<KeyRelease>', self._schedule_selection_action_update, add="+")
        self.source_text.bind('<KeyRelease>', self._schedule_link_refresh, add="+")
        self.source_text.bind('<<Paste>>', self._paste_rich_clipboard)
        self.source_text.bind('<Control-v>', self._paste_rich_clipboard)
        self.source_text.bind('<Control-V>', self._paste_rich_clipboard)
        self.source_text.bind('<Shift-Insert>', self._paste_rich_clipboard)
        self.source_text.bind('<Button-3>', self._show_text_context_menu)
        self.target_text.bind('<ButtonRelease-1>', self._schedule_selection_action_update)
        self.target_text.bind('<KeyRelease>', self._schedule_selection_action_update)
        self.target_text.bind('<KeyRelease>', self._schedule_link_refresh, add="+")
        self.target_text.bind('<<Paste>>', self._paste_rich_clipboard)
        self.target_text.bind('<Control-v>', self._paste_rich_clipboard)
        self.target_text.bind('<Control-V>', self._paste_rich_clipboard)
        self.target_text.bind('<Shift-Insert>', self._paste_rich_clipboard)
        self.target_text.bind('<Button-3>', self._show_text_context_menu)
        self._schedule_link_refresh()

    def _setup_link_tags(self):
        """Configure les liens et les styles riches dans les zones de texte."""
        for widget in (self.source_text, self.target_text):
            widget.tag_configure("link", foreground="#0d6efd", underline=True)
            widget.tag_configure("rich_bold", font=("Arial", 11, "bold"))
            widget.tag_configure("rich_italic", font=("Arial", 11, "italic"))
            widget.tag_configure("rich_bold_italic", font=("Arial", 11, "bold italic"))
            widget.tag_raise("rich_bold_italic")
            for level, font_size in HEADING_FONT_SIZES.items():
                tag = f"rich_heading{level}"
                widget.tag_configure(
                    tag,
                    font=("Arial", font_size, "bold"),
                    spacing1=4 if level <= 3 else 2,
                    spacing3=3 if level <= 3 else 1,
                )
                widget.tag_raise(tag)
                italic_tag = f"{tag}_italic"
                widget.tag_configure(
                    italic_tag,
                    font=("Arial", font_size, "bold italic"),
                    spacing1=4 if level <= 3 else 2,
                    spacing3=3 if level <= 3 else 1,
                )
                widget.tag_raise(italic_tag)
            widget.tag_bind(
                "link",
                "<Enter>",
                lambda event, text_widget=widget: text_widget.config(cursor="hand2"),
            )
            widget.tag_bind(
                "link",
                "<Leave>",
                lambda event, text_widget=widget: text_widget.config(cursor="xterm"),
            )
            widget.tag_bind(
                "link",
                "<Button-1>",
                lambda event, text_widget=widget: self._open_link_at_event(text_widget, event),
            )

    def _schedule_link_refresh(self, event=None):
        """Planifie un recalcul des liens détectés."""
        if self._link_refresh_after_id:
            try:
                self.after_cancel(self._link_refresh_after_id)
            except tk.TclError:
                pass
        self._link_refresh_after_id = self.after(120, self._refresh_links)

    def _refresh_links(self):
        """Actualise les liens et les combinaisons de styles riches."""
        self._link_refresh_after_id = None
        for widget, prefix in ((self.source_text, "source"), (self.target_text, "target")):
            self._refresh_widget_links(widget, prefix)
            self._refresh_combined_style_tag(widget)

    def _refresh_widget_links(self, widget, prefix):
        """Applique les tags de liens à un widget Text."""
        widget.tag_remove("link", "1.0", tk.END)
        link_tags = [tag for tag in widget.tag_names() if tag.startswith(f"{prefix}_link_")]
        for tag in link_tags:
            widget.tag_delete(tag)
            self._link_tag_urls.pop(tag, None)

        text = widget.get("1.0", tk.END)
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            url = match.group(2)
            start = widget.index(f"1.0+{match.start()}c")
            end = widget.index(f"1.0+{match.end()}c")
            tag = f"{prefix}_link_{self._link_tag_counter}"
            self._link_tag_counter += 1
            self._link_tag_urls[tag] = url
            widget.tag_add("link", start, end)
            widget.tag_add(tag, start, end)

        for match in URL_PATTERN.finditer(text):
            url = match.group(0)
            start = widget.index(f"1.0+{match.start()}c")
            end = widget.index(f"1.0+{match.end()}c")
            tag = f"{prefix}_link_{self._link_tag_counter}"
            self._link_tag_counter += 1
            self._link_tag_urls[tag] = url
            widget.tag_add("link", start, end)
            widget.tag_add(tag, start, end)

        rich_tags = [tag for tag in widget.tag_names() if tag.startswith(f"{prefix}_rich_link_")]
        for tag in rich_tags:
            ranges = widget.tag_ranges(tag)
            if not ranges:
                widget.tag_delete(tag)
                self._link_tag_urls.pop(tag, None)
                continue
            for start, end in zip(ranges[0::2], ranges[1::2]):
                widget.tag_add("link", start, end)

    def _paste_rich_clipboard(self, event):
        """Colle les liens et styles du presse-papiers riche."""
        widget = event.widget
        text, links, styles = self._get_rich_clipboard_content()
        if not text:
            try:
                text = self.clipboard_get()
            except tk.TclError:
                return "break"

        self._insert_text_with_links(widget, text, links, styles)
        if widget is self.source_text:
            self.update_word_count()
        self._schedule_link_refresh()
        self._schedule_selection_action_update()
        return "break"

    def _get_rich_clipboard_content(self):
        """Retourne le texte, les liens et les styles du presse-papiers HTML."""
        raw_html = _get_windows_clipboard_html()
        if raw_html:
            text, links, styles = _parse_clipboard_html(raw_html)
            if text and (links or styles):
                return text, links, styles

        for clipboard_type in ("HTML Format", "text/html"):
            try:
                raw_html = self.selection_get(selection="CLIPBOARD", type=clipboard_type)
            except tk.TclError:
                continue
            text, links, styles = _parse_clipboard_html(raw_html)
            if text and (links or styles):
                return text, links, styles
        return "", [], []

    def _insert_text_with_links(self, widget, text, links=None, styles=None):
        """Insère du texte et applique ses liens et styles riches."""
        links = links or []
        styles = styles or []
        try:
            if widget.tag_ranges(tk.SEL):
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

        insert_index = widget.index(tk.INSERT)
        widget.insert(insert_index, text)
        prefix = self._link_prefix_for_widget(widget)
        for start_offset, end_offset, url in links:
            if not url:
                continue
            start = widget.index(f"{insert_index}+{start_offset}c")
            end = widget.index(f"{insert_index}+{end_offset}c")
            self._add_rich_link_tag(widget, prefix, start, end, url)
        for start_offset, end_offset, style in styles:
            if style not in RICH_STYLE_NAMES:
                continue
            start = widget.index(f"{insert_index}+{start_offset}c")
            end = widget.index(f"{insert_index}+{end_offset}c")
            widget.tag_add(f"rich_{style}", start, end)
        self._refresh_combined_style_tag(widget)

    def _replace_widget_text_with_links(self, widget, text, links=None, styles=None):
        """Remplace le contenu d'un widget par du texte riche."""
        links = links or []
        styles = styles or []
        prefix = self._link_prefix_for_widget(widget)
        self._clear_rich_link_tags(widget, prefix)
        for tag in (
            "rich_bold",
            "rich_italic",
            "rich_bold_italic",
            *(f"rich_{style}" for style in HEADING_STYLES),
            *(f"rich_{style}_italic" for style in HEADING_STYLES),
        ):
            widget.tag_remove(tag, "1.0", tk.END)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        for start_offset, end_offset, url in links:
            if not url:
                continue
            start = widget.index(f"1.0+{start_offset}c")
            end = widget.index(f"1.0+{end_offset}c")
            self._add_rich_link_tag(widget, prefix, start, end, url)
        for start_offset, end_offset, style in styles:
            if style not in RICH_STYLE_NAMES:
                continue
            start = widget.index(f"1.0+{start_offset}c")
            end = widget.index(f"1.0+{end_offset}c")
            widget.tag_add(f"rich_{style}", start, end)
        self._refresh_combined_style_tag(widget)
        self._schedule_link_refresh()

    def _render_markdown_links_in_widget(self, widget):
        """Rend les liens et styles Markdown dans le widget."""
        markdown_text = widget.get("1.0", tk.END).rstrip("\n")
        clean_text, links, styles = _markdown_to_rich_text(markdown_text)
        if clean_text != markdown_text or links or styles:
            self._replace_widget_text_with_links(widget, clean_text, links, styles)

    def _widget_text_with_links_as_markdown(self, widget):
        """Sérialise les liens et styles cachés du widget en Markdown."""
        text = widget.get("1.0", tk.END).rstrip("\n")
        prefix = self._link_prefix_for_widget(widget)
        links = []
        for tag in widget.tag_names():
            if not tag.startswith(f"{prefix}_rich_link_"):
                continue
            url = self._link_tag_urls.get(tag)
            if not url:
                continue
            ranges = widget.tag_ranges(tag)
            for start_index, end_index in zip(ranges[0::2], ranges[1::2]):
                try:
                    start = self._text_character_offset(widget, start_index)
                    end = self._text_character_offset(widget, end_index)
                except (TypeError, tk.TclError):
                    continue
                if 0 <= start < end <= len(text):
                    links.append((start, end, url))

        styles = []
        style_tags = [("rich_bold", "bold"), ("rich_italic", "italic")]
        style_tags.extend((f"rich_{style}", style) for style in HEADING_STYLES)
        for tag, style in style_tags:
            ranges = widget.tag_ranges(tag)
            for start_index, end_index in zip(ranges[0::2], ranges[1::2]):
                try:
                    start = self._text_character_offset(widget, start_index)
                    end = self._text_character_offset(widget, end_index)
                except (TypeError, tk.TclError):
                    continue
                if 0 <= start < end <= len(text):
                    styles.append((start, end, style))
        return _rich_text_to_markdown(text, links, styles)

    @staticmethod
    def _text_character_offset(widget, index):
        """Retourne un offset fiable, y compris lorsque l'index vaut 1.0."""
        if widget.compare(index, "==", "1.0"):
            return 0
        count = widget.count("1.0", index, "chars")
        return int(count[0]) if count else 0

    def _refresh_combined_style_tag(self, widget):
        """Rend les combinaisons gras/italique et titre/italique."""
        widget.tag_remove("rich_bold_italic", "1.0", tk.END)
        bold_ranges = widget.tag_ranges("rich_bold")
        italic_ranges = widget.tag_ranges("rich_italic")
        for bold_start, bold_end in zip(bold_ranges[0::2], bold_ranges[1::2]):
            for italic_start, italic_end in zip(italic_ranges[0::2], italic_ranges[1::2]):
                start = italic_start if widget.compare(italic_start, ">", bold_start) else bold_start
                end = italic_end if widget.compare(italic_end, "<", bold_end) else bold_end
                if widget.compare(start, "<", end):
                    widget.tag_add("rich_bold_italic", start, end)

        for heading_style in HEADING_STYLES:
            combined_tag = f"rich_{heading_style}_italic"
            widget.tag_remove(combined_tag, "1.0", tk.END)
            heading_ranges = widget.tag_ranges(f"rich_{heading_style}")
            for heading_start, heading_end in zip(heading_ranges[0::2], heading_ranges[1::2]):
                for italic_start, italic_end in zip(italic_ranges[0::2], italic_ranges[1::2]):
                    start = (
                        italic_start
                        if widget.compare(italic_start, ">", heading_start)
                        else heading_start
                    )
                    end = (
                        italic_end
                        if widget.compare(italic_end, "<", heading_end)
                        else heading_end
                    )
                    if widget.compare(start, "<", end):
                        widget.tag_add(combined_tag, start, end)

    def _clear_rich_link_tags(self, widget, prefix):
        """Supprime les liens cachés d'un widget."""
        for tag in list(widget.tag_names()):
            if tag.startswith(f"{prefix}_rich_link_"):
                widget.tag_delete(tag)
                self._link_tag_urls.pop(tag, None)

    def _link_prefix_for_widget(self, widget):
        """Retourne le préfixe de tags de liens pour un widget."""
        return "source" if widget is self.source_text else "target"

    def _add_rich_link_tag(self, widget, prefix, start, end, url):
        """Ajoute un lien cliquable sur un texte visible sans URL apparente."""
        tag = f"{prefix}_rich_link_{self._link_tag_counter}"
        self._link_tag_counter += 1
        self._link_tag_urls[tag] = url
        widget.tag_add("link", start, end)
        widget.tag_add(tag, start, end)

    def _open_link_at_event(self, widget, event):
        """Ouvre le lien cliqué dans le navigateur par défaut."""
        index = widget.index(f"@{event.x},{event.y}")
        for tag in widget.tag_names(index):
            url = self._link_tag_urls.get(tag)
            if url:
                try:
                    webbrowser.open(url)
                    self.set_status_text(self.status_label, f"Lien ouvert: {url}")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'ouvrir le lien:\n{e}")
                return "break"
        return None

    def _schedule_selection_action_update(self, event=None):
        """Met à jour les actions contextuelles après modification de sélection."""
        self.after_idle(self._update_selection_actions)

    def _update_selection_actions(self):
        """Affiche le lookup seulement quand une sélection existe dans la traduction."""
        target_selection = self._get_target_selection()
        if target_selection:
            self.target_lookup_selection = target_selection
            self._show_target_alternatives_button()
        else:
            self.target_lookup_selection = ""
            self._hide_target_alternatives_button()

    def _get_target_selection(self):
        """Retourne la sélection active de la zone de traduction."""
        try:
            if not self.target_text.tag_ranges(tk.SEL):
                return ""
            return self.target_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            return ""

    def _show_target_alternatives_button(self):
        """Rend visible le bouton contextuel Alternatives."""
        if getattr(self, "target_alternatives_button_visible", False):
            return
        if hasattr(self, "target_alternatives_button"):
            self.target_alternatives_button.pack(side=tk.RIGHT, padx=(0, 8))
            self.target_alternatives_button_visible = True

    def _hide_target_alternatives_button(self):
        """Masque le bouton contextuel Alternatives."""
        if not getattr(self, "target_alternatives_button_visible", False):
            return
        if hasattr(self, "target_alternatives_button"):
            self.target_alternatives_button.pack_forget()
            self.target_alternatives_button_visible = False

    def _show_text_context_menu(self, event):
        """Affiche les actions contextuelles sur la sélection."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Alternatives", command=self.lookup_selection)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def set_status_text(self, widget, text):
        """Helper pour gérer les widgets CTk/ttk"""
        try:
            widget.configure(text=text)
        except Exception:
            widget.config(text=text)

    def update_word_count(self, event=None):
        """Met à jour le compteur de mots"""
        text = self.source_text.get("1.0", tk.END).strip()
        self.word_count = len(re.findall(r'\b\w+\b', text))
        if hasattr(self, 'word_label'):
            self.set_status_text(self.word_label, f"Mots: {self.word_count}")

    def swap_languages(self):
        """Échange les langues source et cible, puis reprend la traduction si disponible."""
        source = self.source_lang.get()
        target = self.target_lang.get()
        translated_text = self.target_text.get("1.0", tk.END).strip()
        translated_markdown = self._widget_text_with_links_as_markdown(self.target_text)

        self.source_lang.set(target)
        if source == "auto":
            self.target_lang.set("en" if target == "fr" else "fr")
        else:
            self.target_lang.set(source)

        if translated_text:
            clean_text, links, styles = _markdown_to_rich_text(translated_markdown)
            self._replace_widget_text_with_links(self.source_text, clean_text, links, styles)
            self.target_text.delete("1.0", tk.END)
            self.update_word_count()
            self._schedule_link_refresh()
            self.set_status_text(self.status_label, "Traduction reprise comme source...")
            self.after(150, self._translate_after_swap)

    def _translate_after_swap(self):
        """Relance automatiquement la traduction après une inversion avec texte repris."""
        if self.is_translating and self.translation_thread and self.translation_thread.is_alive():
            self.stop_event.set()
            self.after(150, self._translate_after_swap)
            return
        if self.is_translating:
            self.is_translating = False
        self.translate()

    def translate(self):
        """Lance la traduction"""
        if self.is_translating:
            self.stop_event.set()
            return

        display_text = self.source_text.get("1.0", tk.END).strip()
        prompt_text = self._widget_text_with_links_as_markdown(self.source_text).strip()
        if not display_text:
            self.set_status_text(self.status_label, "Aucun texte à traduire")
            return

        self.is_translating = True
        self.stop_event.clear()
        self.start_time = time.time()
        self.target_text.delete("1.0", tk.END)
        self._hide_target_alternatives_button()
        self._schedule_link_refresh()
        self.set_status_text(self.status_label, "Traduction en cours...")

        mode = self._get_mode_key()
        source_lang = self.source_lang.get()
        target_lang = self.target_lang.get()
        model = self.model_var.get()
        self.translation_thread = threading.Thread(
            target=self._translate_thread,
            args=(prompt_text, display_text, mode, source_lang, target_lang, model),
        )
        self.translation_thread.daemon = True
        self.translation_thread.start()

    def _get_mode_key(self):
        """Retourne la clé interne du mode depuis son intitulé affiché."""
        current_mode = self.mode.get()
        return MODE_KEYS_BY_LABEL.get(current_mode, current_mode)

    def _update_action_button_label(self, *_args):
        """Aligne le bouton d'action sur le mode sélectionné."""
        if hasattr(self, "action_button"):
            self.action_button.configure(text=self.mode.get())

    def _build_prompt(self, mode, source_lang, target_lang, text, extra_values=None):
        """Construit le prompt depuis le modèle défini en configuration."""
        template = CONFIG["prompts"][mode]
        values = PromptValues(
            PROMPT_VARIABLES,
            source_language=CONFIG["languages"].get(source_lang, source_lang),
            target_language=CONFIG["languages"].get(target_lang, target_lang),
            text=text,
        )
        if extra_values:
            values.update(extra_values)
        return template.format_map(values)

    def _translate_thread(self, prompt_text, display_text, mode, source_lang, target_lang, model):
        """Thread de traduction"""
        try:
            prompt = self._build_prompt(mode, source_lang, target_lang, prompt_text)

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "think": CONFIG.get("think", False),
                "stream": True
            }
            response = requests.post(
                CONFIG["server_url"],
                json=payload,
                headers=_request_headers(),
                stream=True,
                timeout=300,
            )
            response.raise_for_status()

            full_response = ""

            for line in response.iter_lines():
                if self.stop_event.is_set():
                    break
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'message' in data and 'content' in data['message']:
                            chunk = data['message']['content']
                            if chunk:  # Éviter les chunks vides
                                full_response += chunk
                                # Insérer via queue (thread-safe)
                                self.output_queue.put(("insert", chunk))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

            self.translation_time = time.time() - self.start_time
            self.output_queue.put(("time", f"Temps: {self.translation_time:.1f}s"))

            if full_response.strip():
                self.output_queue.put(("call", (self._render_markdown_links_in_widget, (self.target_text,))))
                self.output_queue.put(("history", {
                    'source': display_text, 'source_markdown': prompt_text, 'target': full_response,
                    'source_lang': source_lang, 'target_lang': target_lang,
                    'mode': mode, 'timestamp': time.time()
                }))

            self.output_queue.put(("status", "Traduction terminée"))

        except Exception as e:
            self.output_queue.put(("status", f"Erreur: {str(e)}"))
        finally:
            self.is_translating = False

    def _get_selected_text(self):
        """Retourne la sélection active dans la source ou la traduction."""
        for widget, area in ((self.source_text, "source"), (self.target_text, "target")):
            try:
                if widget.tag_ranges(tk.SEL):
                    selection = widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
                    if selection:
                        return selection, area
            except tk.TclError:
                continue
        return "", ""

    def lookup_selection(self):
        """Cherche des alternatives contextuelles pour le texte sélectionné."""
        selection, area = self._get_selected_text()
        if not selection:
            self.set_status_text(self.status_label, "Sélectionnez un mot ou une phrase")
            return
        self._start_lookup(selection, area)

    def lookup_target_selection(self):
        """Cherche des alternatives pour la sélection mémorisée dans la traduction."""
        selection = self._get_target_selection() or self.target_lookup_selection
        if not selection:
            self.set_status_text(self.status_label, "Sélectionnez un mot ou une phrase")
            self._hide_target_alternatives_button()
            return
        self._start_lookup(selection, "target")

    def _start_lookup(self, selection, area):
        """Démarre la recherche d'alternatives pour une sélection donnée."""
        result_text = self._open_lookup_window(selection, area)
        source_text = self.source_text.get("1.0", tk.END).strip()
        target_text = self.target_text.get("1.0", tk.END).strip()
        source_lang = self.source_lang.get()
        target_lang = self.target_lang.get()
        model = self.model_var.get()
        self.set_status_text(self.status_label, "Recherche d'alternatives...")

        lookup_thread = threading.Thread(
            target=self._lookup_thread,
            args=(selection, source_text, target_text, source_lang, target_lang, model, result_text),
            daemon=True,
        )
        lookup_thread.start()

    def _open_lookup_window(self, selection, area):
        """Ouvre la fenêtre de résultats du lookup."""
        title_area = "source" if area == "source" else "traduction"
        popup = tk.Toplevel(self)
        popup.title("Alternatives")
        popup.geometry("520x360")
        popup.transient(self)

        container = ttk.Frame(popup, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text=f"Sélection ({title_area}) : {selection[:90]}",
            wraplength=480,
        ).pack(anchor=tk.W, pady=(0, 8))

        text_frame = ttk.Frame(container)
        text_frame.pack(fill=tk.BOTH, expand=True)

        result_text = tk.Text(text_frame, wrap=tk.WORD, height=12, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(text_frame, command=result_text.yview)
        result_text.config(yscrollcommand=scrollbar.set)
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        result_text.insert("1.0", "Recherche en cours...")
        result_text.config(state=tk.DISABLED)

        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="Fermer", command=popup.destroy).pack(side=tk.RIGHT)

        return result_text

    def _set_text_widget_content(self, widget, content):
        """Remplace le contenu d'un widget Text, même s'il est en lecture seule."""
        try:
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", content.strip())
            widget.config(state=tk.DISABLED)
        except tk.TclError:
            pass

    def _lookup_thread(
        self,
        selection,
        source_text,
        target_text,
        source_lang,
        target_lang,
        model,
        result_text,
    ):
        """Thread de recherche d'alternatives contextuelles."""
        try:
            prompt = self._build_prompt(
                "lookup",
                source_lang,
                target_lang,
                source_text,
                extra_values={
                    "translation": target_text,
                    "selection": selection,
                },
            )

            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "think": CONFIG.get("think", False),
                "stream": False,
            }
            response = requests.post(
                CONFIG["server_url"],
                json=payload,
                headers=_request_headers(),
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()
            if not content:
                content = "Aucune alternative reçue."

            self.output_queue.put(("call", (self._set_text_widget_content, (result_text, content))))
            self.output_queue.put(("status", "Alternatives prêtes"))
        except Exception as e:
            message = f"Erreur lookup: {str(e)}"
            self.output_queue.put(("call", (self._set_text_widget_content, (result_text, message))))
            self.output_queue.put(("status", message))

    def _add_history_item(self, item):
        """Ajoute une traduction à l'historique depuis le thread UI."""
        self.history.append(item)
        self.history = self.history[-10:]
        self._update_history_menu()

    def _update_history_menu(self):
        """Met à jour le menu historique"""
        if hasattr(self, 'history_menu'):
            self.history_menu.delete(0, tk.END)
            for i, item in enumerate(reversed(self.history[-5:])):
                text_preview = item['source'][:30] + "..." if len(item['source']) > 30 else item['source']
                self.history_menu.add_command(
                    label=f"{i+1}. {text_preview}",
                    command=lambda idx=len(self.history)-1-i: self._load_from_history(idx)
                )

    def _load_from_history(self, index):
        """Charge une traduction depuis l'historique"""
        if 0 <= index < len(self.history):
            item = self.history[index]
            source_text = item.get('source_markdown', item['source'])
            source_clean, source_links, source_styles = _markdown_to_rich_text(source_text)
            target_clean, target_links, target_styles = _markdown_to_rich_text(item['target'])
            self._replace_widget_text_with_links(
                self.source_text,
                source_clean,
                source_links,
                source_styles,
            )
            self._replace_widget_text_with_links(
                self.target_text,
                target_clean,
                target_links,
                target_styles,
            )
            self.source_lang.set(item['source_lang'])
            self.target_lang.set(item['target_lang'])
            self.mode.set(MODE_LABELS.get(item['mode'], item['mode']))
            self.update_word_count()
            self._schedule_link_refresh()

    def import_file(self):
        """Importe un fichier texte, PDF ou DOCX"""
        filetypes = [("Fichiers texte", "*.txt")]
        if DOCX_SUPPORT:
            filetypes.append(("Fichiers Word", "*.docx"))
        if PDF_SUPPORT:
            filetypes.append(("Fichiers PDF", "*.pdf"))
        filetypes.append(("Tous les fichiers", "*.*"))

        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            try:
                content = ""
                file_ext = Path(file_path).suffix.lower()

                if file_ext == '.txt':
                    # Fichier texte
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif file_ext == '.docx' and DOCX_SUPPORT:
                    # Fichier Word
                    doc = Document(file_path)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
                elif file_ext == '.pdf' and PDF_SUPPORT:
                    # Fichier PDF
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                content += page_text + '\n'
                else:
                    raise ValueError(f"Format de fichier non supporté: {file_ext}")

                if not content.strip():
                    raise ValueError("Le fichier semble être vide ou ne contient pas de texte extractible")

                self.source_text.delete("1.0", tk.END)
                self.source_text.insert("1.0", content.strip())
                self.update_word_count()
                self._schedule_link_refresh()
                self.set_status_text(self.status_label, f"Fichier importé: {os.path.basename(file_path)}")

            except Exception as e:
                error_msg = f"Impossible d'importer le fichier:\n{str(e)}"
                if "pdfplumber" in str(e).lower() or "docx" in str(e).lower():
                    error_msg += "\n\nAssurez-vous d'avoir installé les dépendances:\npip install pdfplumber python-docx"
                messagebox.showerror("Erreur", error_msg)

    def export_translation(self):
        """Exporte la traduction"""
        content = self.target_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Avertissement", "Aucune traduction à exporter")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.set_status_text(self.status_label, f"Traduction exportée: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'exporter:\n{str(e)}")

    def copy_translation(self):
        """Copie la traduction dans le presse-papiers"""
        content = self.target_text.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.set_status_text(self.status_label, "Traduction copiée")


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
