#!/usr/bin/env python3
"""Test LM Studio local model via CAMEL bridge."""

import os
import sys

# Add src to path
sys.path.insert(0, "/Volumes/External/Code/loreSystem/src")

os.environ.update({
    "CAMEL_MODEL_PLATFORM": "OPENAI",
    "CAMEL_MODEL_BASE_URL": "http://127.0.0.1:1234",
    "CAMEL_MODEL_TYPE": "l3-8b-stheno-v3.2-mlx",
    "CAMEL_MODEL_TEMPERATURE": "0.8",
})

from application.integration.camel_bridge.backend import CamelChatBackend


def main():
    print("🔌 Testing LM Studio connection...")
    print(f"   URL: {os.getenv('CAMEL_MODEL_BASE_URL')}")
    print(f"   Model: {os.getenv('CAMEL_MODEL_TYPE')}")
    print()

    backend = CamelChatBackend()

    system = "Ты — русский гейм-дизайнер. Отвечай только на русском."
    user = "Создай короткий квест для RPG игры: название, описание, награда."

    print("📝 Generating quest in Russian...")
    print(f"   System: {system[:50]}...")
    print(f"   User: {user[:50]}...")
    print()

    try:
        result = backend.generate(system, user)
        print("✅ Success!")
        print()
        print("─" * 60)
        print(result)
        print("─" * 60)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
