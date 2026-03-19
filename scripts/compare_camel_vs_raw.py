#!/usr/bin/env python3
"""Compare CAMEL.Bridge vs raw LM Studio generation quality."""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, "/Volumes/External/Code/loreSystem/src")

os.environ.update({
    "CAMEL_MODEL_PLATFORM": "OPENAI",
    "CAMEL_MODEL_BASE_URL": "http://127.0.0.1:1234",
    "CAMEL_MODEL_TYPE": "l3-8b-stheno-v3.2-mlx",
    "CAMEL_MODEL_TEMPERATURE": "0.8",
})

from src.application.integration.camel_bridge import CamelChatBackend


def test_raw_generation(backend: CamelChatBackend) -> dict:
    """Test raw prompt without CAMEL structure."""
    print("\n" + "="*60)
    print("📝 TEST 1: Raw Generation (no CAMEL)")
    print("="*60)

    raw_prompt = """Create a dark fantasy rumor about a cursed castle.
Return as JSON with fields: name, description, source_name."""

    start = datetime.now()
    response = backend.generate("You are a game designer.", raw_prompt)
    elapsed = (datetime.now() - start).total_seconds()

    print(f"Time: {elapsed:.1f}s")
    print(f"Length: {len(response)} chars")
    print(f"\nResponse:\n{response[:500]}...")

    # Try to parse as JSON
    try:
        parsed = json.loads(response)
        print(f"\n✅ Valid JSON: {list(parsed.keys())}")
        return {"valid_json": True, "fields": list(parsed.keys()), "time": elapsed}
    except:
        print(f"\n❌ Not valid JSON")
        return {"valid_json": False, "fields": [], "time": elapsed}


def test_camel_rumor(backend: CamelChatBackend) -> dict:
    """Test CAMEL.Bridge rumor generation."""
    print("\n" + "="*60)
    print("📝 TEST 2: CAMEL.Bridge Rumor Generation")
    print("="*60)

    # CAMEL's actual rumor prompt
    system_prompt = """
Output language: Russian.
ALL textual content MUST be in Russian unless explicitly noted.

You are a DARK FANTASY rumor generator. Create rumors that are:
- Vivid, dramatic, and suitable for codex seeding
- Socially contagious (people WANT to share them)
- Uncertain in truth (mix of fact and speculation)

Format: JSON with fields:
{
  "name": "rumor_name",
  "description": "vivid_description",
  "source_name": "speaker_persona",
  "truth_level": "verified|unverified|debunked",
  "spread_speed": number (1-100),
  "credibility_score": number (0-100)
}
"""

    user_prompt = """
Output language: Russian.
ALL textual content MUST be in Russian.

Theme: Dark Fantasy - Проклятый замок
Context: Древний замок проклят, нежить бродит по коридорам
Count: 1

Generate 1 rumor with fields: name, description, source_name, truth_level, spread_speed, credibility_score.
Speaker persona: Городской сумасшедший
"""

    start = datetime.now()
    response = backend.generate(system_prompt, user_prompt)
    elapsed = (datetime.now() - start).total_seconds()

    print(f"Time: {elapsed:.1f}s")
    print(f"Length: {len(response)} chars")
    print(f"\nResponse:\n{response[:500]}...")

    # Try to parse as JSON
    try:
        parsed = json.loads(response)
        print(f"\n✅ Valid JSON: {list(parsed.keys())}")
        required = ["name", "description", "source_name", "truth_level", "spread_speed", "credibility_score"]
        has_all = all(k in parsed for k in required)
        print(f"   Has all required fields: {has_all}")
        return {"valid_json": True, "fields": list(parsed.keys()), "has_required": has_all, "time": elapsed}
    except:
        print(f"\n❌ Not valid JSON")
        return {"valid_json": False, "fields": [], "has_required": False, "time": elapsed}


def test_camel_batch(backend: CamelChatBackend) -> dict:
    """Test CAMEL batch generation (rumors + events + relationships)."""
    print("\n" + "="*60)
    print("📝 TEST 3: CAMEL.Bridge Batch Generation")
    print("="*60)

    # Simpler batch test
    system_prompt = """
Generate 2 dark fantasy rumors in Russian.

Format: JSON array with objects containing:
{
  "name": "rumor_name",
  "description": "vivid_description",
  "source_name": "speaker",
  "truth_level": "unverified",
  "spread_speed": 50,
  "credibility_score": 50
}
"""

    start = datetime.now()
    response = backend.generate(system_prompt, "Theme: Проклятые руины в тёмном лесу")
    elapsed = (datetime.now() - start).total_seconds()

    print(f"Time: {elapsed:.1f}s")
    print(f"Length: {len(response)} chars")

    # Try to parse as JSON array
    try:
        parsed = json.loads(response)
        if isinstance(parsed, list):
            print(f"\n✅ Valid JSON Array with {len(parsed)} rumors")
            fields = list(parsed[0].keys()) if parsed else []
            return {"valid_json": True, "count": len(parsed), "fields": fields, "time": elapsed}
        else:
            print(f"\n⚠️  Valid JSON but not array")
            return {"valid_json": True, "count": 0, "fields": list(parsed.keys()), "time": elapsed}
    except:
        print(f"\n❌ Not valid JSON")
        return {"valid_json": False, "count": 0, "fields": [], "time": elapsed}


def main():
    print("🔬 CAMEL.Bridge vs Raw Generation Comparison")
    print("=" * 60)
    print(f"Model: {os.getenv('CAMEL_MODEL_TYPE')}")
    print(f"URL: {os.getenv('CAMEL_MODEL_BASE_URL')}")
    print()

    backend = CamelChatBackend()

    # Warmup - ensure model is loaded
    print("🔥 Warming up (loading model)...")
    for _ in range(3):
        try:
            backend.generate("Тест", "Скажи: ОК")
            break
        except Exception as e:
            if "unloaded" in str(e).lower() or "400" in str(e) or "No models" in str(e):
                print("   Waiting for model to load...")
                import time
                time.sleep(2)
                continue
            raise
    print()

    results = {
        "raw": test_raw_generation(backend),
        "camel_rumor": test_camel_rumor(backend),
        "camel_batch": test_camel_batch(backend),
    }

    print("\n" + "="*60)
    print("📊 RESULTS SUMMARY")
    print("="*60)

    print("\n{:<20} {:<12} {:<20} {:<10}".format("Test", "Valid JSON", "Fields", "Time"))
    print("-"*65)

    r = results["raw"]
    mark = "✅" if r['valid_json'] else "❌"
    print("{:<20} {:<12} {:<20} {:.1f}s".format("Raw Generation", mark, f"{len(r['fields'])} fields", r['time']))

    r = results["camel_rumor"]
    mark = "✅" if r['valid_json'] else "❌"
    print("{:<20} {:<12} {:<20} {:.1f}s".format("CAMEL Rumor", mark, f"{len(r['fields'])} fields", r['time']))

    r = results["camel_batch"]
    mark = "✅" if r['valid_json'] else "❌"
    print("{:<20} {:<12} {:<20} {:.1f}s".format("CAMEL Batch", mark, f"{r.get('count', 0)} items", r['time']))

    print("\n" + "="*60)
    print("💡 KEY INSIGHTS:")
    print("="*60)
    print("""
CAMEL.Bridge adds:
1. Structured system prompts per entity type
2. Required field validation in prompts
3. Russian language enforcement
4. JSON schema in prompt
5. Batch generation support

Without CAMEL:
- Simpler but less structured
- No field validation
- May need post-processing
    """)


if __name__ == "__main__":
    main()
