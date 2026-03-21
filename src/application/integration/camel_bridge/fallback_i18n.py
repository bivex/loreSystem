"""Internationalization fallback dictionary for CAMEL bridge."""

from typing import Dict, Any

# Russian translations for fallback content
RU_FALLBACK: Dict[str, str] = {
    # Common terms
    "Campaign": "Кампания",
    "Chronicle": "Хроника",
    "Before the First Whisper": "До Первого Шепота",

    # Acts
    "Act I - Setup": "Акт I - Завязка",
    "Act II - Confrontation": "Акт II - Конфронтация",
    "Act III - Resolution": "Акт III - Разрешение",

    # Chapters
    "Chapter 1": "Глава 1",
    "Chapter 2": "Глава 2",
    "Chapter 3": "Глава 3",

    # Episodes
    "Episode 1": "Эпизод 1",
    "Episode 2": "Эпизод 2",
    "Episode 3": "Эпизод 3",

    # Storylines
    "Main Line": "Основная Линия",

    # Characters
    "Mara Voss": "Мара Восс",
    "Iven Hale": "Ивен Хейл",

    # Character variants
    "Bellwarden Disguise": "Маскировка Звонаря",

    # Character profiles
    "Hears the harbor bells in every silence.": "Слышит колокола гавани в каждой тишине.",

    # Quests
    "Silence Before the Bell": "Тишина Перед Колоколом",
    "Speak to the dockworkers": "Поговори с докерами",
    "Light the signal pyre": "Зажги сигнальный костер",
    "Complete Silence Before the Bell": "Заверши Тишина Перед Колоколом",

    # Quest chains
    "Harbor Reckoning": "Расчёт в Гавани",

    # Quest nodes
    "Warn the Docks": "Предупреди Докеров",

    # Quest givers
    "Dockmaster Elra": "Гаваньмастер Эльра",

    # Quest rewards
    "Bellkeeper's Reward": "Награда Звонаря",

    # Motion/Voice
    "Harbor Warning Gesture": "Жест Предупреждения Гавани",
    "Talan Reed": "Талан Рид",

    # Factions
    "Harbor Guard": "Стража Гавани",
}


def t(key: str, lang: str = "en") -> str:
    """Translate a fallback key to the target language."""
    if lang == "ru":
        return RU_FALLBACK.get(key, key)
    return key


def get_default_characters(lang: str = "en") -> tuple:
    """Get default fallback character names."""
    if lang == "ru":
        return ("Мара Восс", "Ивен Хейл")
    return ("Mara Voss", "Iven Hale")


def get_default_theme_suffix(lang: str = "en") -> dict:
    """Get default theme suffixes for fallback content."""
    if lang == "ru":
        return {
            "whisper": "Шепот",
            "rising": "Восстание",
            "default_theme": "Гавань",
            "campaign": "Кампания",
            "chronicle": "Хроника",
        }
    return {
        "whisper": "Whisper",
        "rising": "Rising",
        "default_theme": "Harbor",
        "campaign": "Campaign",
        "chronicle": "Chronicle",
    }


def localize_fallback_draft(draft: Any, lang: str = "en") -> Any:
    """
    Localize a fallback draft object in-place.
    This function mutates the draft object and returns it.
    """
    if lang != "ru":
        return draft

    # Helper to localize string or tuple of strings
    def _localize_value(value: Any) -> Any:
        if isinstance(value, str):
            return t(value, lang)
        elif isinstance(value, tuple):
            return tuple(_localize_value(v) for v in value)
        elif isinstance(value, list):
            return [_localize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: _localize_value(v) for k, v in value.items()}
        return value

    # Localize common draft attributes
    if hasattr(draft, 'title'):
        draft.title = _localize_value(draft.title)
    if hasattr(draft, 'name'):
        draft.name = _localize_value(draft.name)
    if hasattr(draft, 'description'):
        draft.description = _localize_value(draft.description)
    if hasattr(draft, 'label'):
        draft.label = _localize_value(draft.label)

    # For QuestDraft - localize all text fields
    if hasattr(draft, 'objectives'):
        draft.objectives = _localize_value(draft.objectives)
    if hasattr(draft, 'participant_names'):
        draft.participant_names = _localize_value(draft.participant_names)
    if hasattr(draft, 'reward_tier_names'):
        draft.reward_tier_names = _localize_value(draft.reward_tier_names)

    return draft
