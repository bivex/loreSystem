"""
Internationalization support for MythWeave.
"""
import json
from pathlib import Path


class I18n:
    def __init__(self, locale: str | None = None):
        self.locale = locale or 'en'
        self._dict: dict = {}
        self.load(self.locale)

    def load(self, locale: str):
        self.locale = locale
        base = Path(__file__).parent / 'i18n'
        path = base / f"{locale}.json"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                self._dict = json.load(f)
        else:
            # fallback to en
            fallback = base / 'en.json'
            if fallback.exists():
                with open(fallback, 'r', encoding='utf-8') as f:
                    self._dict = json.load(f)
            else:
                self._dict = {}

    def t(self, key: str, default: str | None = None) -> str:
        return self._dict.get(key, default or key)


# singleton
I18N = I18n()