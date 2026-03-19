#!/usr/bin/env python3
"""Run narrative generation with LM Studio local model.

Usage:
    python3 scripts/run_lm_studio.py --prompt "Create a dark fantasy quest"
    python3 scripts/run_lm_studio.py --file narrative.txt --limit 5
"""

import os
import sys
import argparse

# Add src to path
sys.path.insert(0, "/Volumes/External/Code/loreSystem/src")


# Default system prompts for different entity types
SYSTEM_PROMPTS = {
    "quest": """Ты — мастер гейм-дизайна RPG игр в жанре dark fantasy.
Создавай квесты на русском языке с атмосферой мрака, отчаяния и надежды.
Формат вывода JSON:
{
  "name": "Название квеста",
  "description": "Описание",
  "objectives": ["цель 1", "цель 2"],
  "rewards": "награда"
}""",

    "character": """Ты — мастер создания персонажей для dark fantasy RPG.
Создавай глубоких, трагичных персонажей на русском языке.
Формат вывода JSON:
{
  "name": "Имя",
  "role": "роль",
  "backstory": "предыстория",
  "personality": "черты характера"
}""",

    "event": """Ты — мастер событий для dark fantasy мира.
Создавай атмосферные события на русском языке.
Формат вывода JSON:
{
  "name": "Название события",
  "description": "Описание",
  "consequences": "последствия"
}""",

    "rumor": """Ты — мастер слухов и сплетен для dark fantasy мира.
Создавай загадочные слухи на русском языке.
Формат вывода JSON:
{
  "text": "текст слуха",
  "source": "источник",
  "truth_level": "уровень правды"
}""",
}


def main():
    parser = argparse.ArgumentParser(description="Generate narrative with LM Studio")
    parser.add_argument("--prompt", help="Direct prompt text")
    parser.add_argument("--file", help="Read prompts from file (one per line)")
    parser.add_argument("--type", choices=["quest", "character", "event", "rumor"], default="quest", help="Entity type")
    parser.add_argument("--model", default="l3-8b-stheno-v3.2-mlx", help="Model name in LM Studio")
    parser.add_argument("--url", default="http://127.0.0.1:1234", help="LM Studio API URL")
    parser.add_argument("--temp", type=float, default=0.8, help="Temperature")
    parser.add_argument("--limit", type=int, help="Limit number of generations")
    args = parser.parse_args()

    # Set environment for CAMEL bridge
    os.environ.update({
        "CAMEL_MODEL_PLATFORM": "OPENAI",
        "CAMEL_MODEL_BASE_URL": args.url,
        "CAMEL_MODEL_TYPE": args.model,
        "CAMEL_MODEL_TEMPERATURE": str(args.temp),
    })

    print(f"🤖 LM Studio Narrative Generator")
    print(f"   URL: {args.url}")
    print(f"   Model: {args.model}")
    print(f"   Type: {args.type}")
    print(f"   Temp: {args.temp}")
    print()

    from src.application.integration.camel_bridge import CamelChatBackend

    backend = CamelChatBackend()
    system_prompt = SYSTEM_PROMPTS[args.type]

    # Get prompts
    if args.prompt:
        prompts = [args.prompt]
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
    else:
        # Default prompts
        prompts = [
            "Создай квест о спасении деревни от нежити",
            "Создай квест о поиске древнего артефакта",
            "Создай квест о мести предателю",
        ]

    if args.limit:
        prompts = prompts[:args.limit]

    print(f"📝 Generating {len(prompts)} {args.type}s\n")

    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {prompt[:60]}...")
        try:
            result = backend.generate(
                system_message=system_prompt,
                user_message=prompt
            )
            print(f"   ✅ {len(result)} chars")
            print()
            print("─" * 60)
            print(result)
            print("─" * 60)
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n✅ Done!")


if __name__ == "__main__":
    main()
