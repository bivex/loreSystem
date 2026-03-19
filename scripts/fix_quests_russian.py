#!/usr/bin/env python3
"""Post-processing script to translate English quests to Russian."""

import sys
import sqlite3
import json
import re
from pathlib import Path

sys.path.insert(0, "/Volumes/External/Code/loreSystem/src")

# Simple translation dictionary for common quest terms
TRANSLATIONS = {
    # Quest terms
    "Silence Before the Bell": "Тишина перед колоколом",
    "Speak to the dockworkers": "Поговори с докерами",
    "Light the signal pyre": "Зажги сигнальный костер",
    "Dockmaster Elra": "Гаваньмастер Эльра",
    "Bellkeeper's Reward": "Награда звонаря",
    "Harbor Reckoning": "Расчёт в гавани",
    "Warn the Docks": "Предупреди докеров",
    "Get the dockworkers moving": "Приведи докеров в движение",
    "Carry the final warning": "Доставь последнее предупреждение",
    "before the bells trigger panic": "прежде чем колокола вызовут панику",
    "The warning reaches": "Предупреждение достигает",
    "the harbor stands ready": "гавань готова",
    "The bells outrun": "Колокола обогнали",
    "harbor is already breaking": "гавань уже рушится",
    "25 silver": "25 серебра",
    "120 experience": "120 опыта",
    "dockworkers' trust": "доверие докеров",
    "Elra presses a sealed note": "Эльра протягивает запечатанную записку",
    "into your hand": "тебе в руку",
    "before the watch locks": "прежде чем стража запирает",
    "the waterfront": "пристань",
    "Lanterns answer": "Фонари отвечают",
    "instead of blind": "вместо слепоты",

    # Common phrases
    "Investigate": "Расследуй",
    "Defeat": "Победи",
    "Protect": "Защити",
    "Retrieve": "Добуди",
    "Deliver": "Доставь",
    "Talk to": "Поговори с",
    "Return to": "Вернись к",
    "Kill": "Убей",
    "Collect": "Собери",
    "Find": "Найди",
    "Explore": "Исследуй",
}


def translate_text(text: str) -> str:
    """Simple translation using dictionary + heuristics."""
    if not text or not isinstance(text, str):
        return text

    # Check if text contains Russian (Cyrillic)
    if re.search(r'[А-Яа-яЁё]', text):
        return text  # Already Russian

    # Try direct replacements
    result = text
    for en, ru in TRANSLATIONS.items():
        result = result.replace(en, ru)

    return result


def translate_quest_payload(payload: dict) -> dict:
    """Translate quest payload to Russian."""
    translated = payload.copy()

    # Translate string fields
    for key in ["name", "label", "title", "description", "player_briefing",
                 "journal_summary", "acceptance_text", "completion_text",
                 "failure_text", "reward_summary", "briefing"]:
        if key in translated and isinstance(translated[key], str):
            translated[key] = translate_text(translated[key])

    # Translate objectives array
    if "objectives" in translated and isinstance(translated["objectives"], list):
        translated["objectives"] = [
            translate_text(obj) if isinstance(obj, str) else obj
            for obj in translated["objectives"]
        ]

    # Translate choices
    if "choices" in translated and isinstance(translated["choices"], list):
        for choice in translated["choices"]:
            if isinstance(choice, dict):
                if "prompt" in choice:
                    choice["prompt"] = translate_text(choice["prompt"])
                if "label" in choice:
                    choice["label"] = translate_text(choice["label"])

    return translated


def fix_database(db_path: str) -> None:
    """Fix quests in database by translating to Russian."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    print(f"🔧 Fixing quests in {db_path}")

    # Get all quests
    cursor = conn.execute("SELECT id, label, payload_json FROM quests")
    quests = cursor.fetchall()

    if not quests:
        print("   No quests found")
        return

    print(f"   Found {len(quests)} quest(s)")

    for quest in quests:
        quest_id = quest["id"]
        label = quest["label"]
        payload_json = quest["payload_json"]

        try:
            payload = json.loads(payload_json)
        except:
            print(f"   ❌ Quest {quest_id}: invalid JSON, skipping")
            continue

        # Check if already Russian
        if re.search(r'[А-Яа-яЁё]', label + payload_json):
            print(f"   ✅ Quest {quest_id} ('{label}'): already Russian")
            continue

        # Translate
        translated_payload = translate_quest_payload(payload)
        translated_json = json.dumps(translated_payload, ensure_ascii=False)

        # Update
        conn.execute(
            "UPDATE quests SET label = ?, payload_json = ? WHERE id = ?",
            (translated_payload.get("label", label), translated_json, quest_id)
        )

        new_label = translated_payload.get("label", label)
        print(f"   🔄 Quest {quest_id}: '{label}' → '{new_label}'")

    conn.commit()
    print(f"\n✅ Done! {len(quests)} quest(s) processed")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Translate English quests to Russian")
    parser.add_argument("db", help="Path to SQLite database")
    args = parser.parse_args()

    if not Path(args.db).exists():
        print(f"❌ Database not found: {args.db}")
        return 1

    fix_database(args.db)
    return 0


if __name__ == "__main__":
    sys.exit(main())
