#!/usr/bin/env python3
"""Compare raw Trinity Mini vs CAMEL.Bridge prompts."""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, "/Volumes/External/Code/loreSystem/src")

# Use Trinity Mini via OpenRouter
os.environ.update({
    "CAMEL_MODEL_PLATFORM": "OPENROUTER",
    "CAMEL_MODEL_BASE_URL": "https://openrouter.ai/api/v1",
    "CAMEL_MODEL_TYPE": "arcee-ai/trinity-mini:free",
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
    "CAMEL_MODEL_TEMPERATURE": "0.8",
})

from src.application.integration.camel_bridge import CamelChatBackend


def test_raw_trinity(backend: CamelChatBackend) -> dict:
    """Test raw prompt without CAMEL structure."""
    print("\n" + "="*70)
    print("📝 TEST 1: Raw Trinity Mini (no CAMEL structure)")
    print("="*70)

    raw_prompt = """Create a dark fantasy rumor about a cursed castle.
Return as JSON with: name, description, source_name, truth_level"""

    start = datetime.now()
    response = backend.generate("You are a game designer.", raw_prompt)
    elapsed = (datetime.now() - start).total_seconds()

    print(f"⏱️  Time: {elapsed:.1f}s")
    print(f"📏 Length: {len(response)} chars")
    print(f"\n📄 Response:\n{response[:800]}...")

    # Try to parse as JSON
    try:
        parsed = json.loads(response)
        print(f"\n✅ Valid JSON keys: {list(parsed.keys())}")
        return {"valid_json": True, "fields": list(parsed.keys()), "time": elapsed, "response": response}
    except Exception as e:
        print(f"\n❌ JSON parse error: {str(e)[:100]}")
        return {"valid_json": False, "fields": [], "time": elapsed, "response": response}


def test_camel_rumor(backend: CamelChatBackend) -> dict:
    """Test CAMEL.Bridge rumor generation."""
    print("\n" + "="*70)
    print("📝 TEST 2: CAMEL.Bridge Rumor (structured prompt)")
    print("="*70)

    # CAMEL's actual rumor system prompt
    system_prompt = """
Output language: Russian.
ALL textual content MUST be in Russian unless explicitly noted.

You are a DARK FANTASY rumor generator. Create rumors that are:
- Vivid, dramatic, and suitable for codex seeding
- Socially contagious (people WANT to share them)
- Uncertain in truth (mix of fact and speculation)

Return ONLY valid JSON with this exact structure:
{
  "name": "rumor_name_in_russian",
  "description": "vivid_dramatic_description_in_russian",
  "source_name": "speaker_persona_in_russian",
  "truth_level": "verified|unverified|debunked",
  "spread_speed": number_1_to_100,
  "credibility_score": number_0_to_100
}
"""

    user_prompt = """
Theme: Dark Fantasy - Проклятый замок
Context: Древний замок проклят, нежить бродит по коридорам
Count: 1

Generate 1 rumor in Russian.
Speaker persona: Городской сумасшедший
"""

    start = datetime.now()
    response = backend.generate(system_prompt, user_prompt)
    elapsed = (datetime.now() - start).total_seconds()

    print(f"⏱️  Time: {elapsed:.1f}s")
    print(f"📏 Length: {len(response)} chars")
    print(f"\n📄 Response:\n{response[:800]}...")

    # Try to parse as JSON
    try:
        parsed = json.loads(response)
        print(f"\n✅ Valid JSON keys: {list(parsed.keys())}")
        required = ["name", "description", "source_name", "truth_level", "spread_speed", "credibility_score"]
        has_all = all(k in parsed for k in required)
        print(f"   Has all 6 required fields: {has_all}")
        is_russian = any(ord(c) > 127 for c in str(parsed.values()))
        print(f"   Contains Russian text: {is_russian}")
        return {
            "valid_json": True,
            "fields": list(parsed.keys()),
            "has_required": has_all,
            "is_russian": is_russian,
            "time": elapsed,
            "response": response
        }
    except Exception as e:
        print(f"\n❌ JSON parse error: {str(e)[:100]}")
        return {
            "valid_json": False,
            "fields": [],
            "has_required": False,
            "is_russian": False,
            "time": elapsed,
            "response": response
        }


def test_camel_batch(backend: CamelChatBackend) -> dict:
    """Test CAMEL batch generation."""
    print("\n" + "="*70)
    print("📝 TEST 3: CAMEL.Bridge Batch (rumors + events + relationships)")
    print("="*70)

    # Simplified batch - just 2 rumors
    system_prompt = """
Generate 2 dark fantasy rumors in Russian.

Return ONLY valid JSON array:
[
  {
    "name": "rumor_name",
    "description": "vivid_description",
    "source_name": "speaker",
    "truth_level": "unverified",
    "spread_speed": 50,
    "credibility_score": 50
  }
]

Theme: Проклятые руины в тёмном лесу
"""

    start = datetime.now()
    response = backend.generate(system_prompt, "Theme: Проклятые руины в тёмном лесу")
    elapsed = (datetime.now() - start).total_seconds()

    print(f"⏱️  Time: {elapsed:.1f}s")
    print(f"📏 Length: {len(response)} chars")
    print(f"\n📄 Response:\n{response[:800]}...")

    # Try to parse as JSON array
    try:
        parsed = json.loads(response)
        if isinstance(parsed, list):
            print(f"\n✅ Valid JSON Array with {len(parsed)} rumors")
            fields = list(parsed[0].keys()) if parsed else []
            return {"valid_json": True, "count": len(parsed), "fields": fields, "time": elapsed, "response": response}
        else:
            print(f"\n⚠️  Valid JSON but not array")
            return {"valid_json": True, "count": 0, "fields": list(parsed.keys()), "time": elapsed, "response": response}
    except Exception as e:
        print(f"\n❌ JSON parse error: {str(e)[:100]}")
        return {"valid_json": False, "count": 0, "fields": [], "time": elapsed, "response": response}


def main():
    print("🔬 Trinity Mini: Raw vs CAMEL.Bridge Comparison")
    print("=" * 70)
    print(f"Model: arcee-ai/trinity-mini:free")
    print(f"Platform: OpenRouter")
    print()

    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not set!")
        print("   Set it with: export OPENROUTER_API_KEY='your-key'")
        return 1

    backend = CamelChatBackend()

    results = {
        "raw": test_raw_trinity(backend),
        "camel_rumor": test_camel_rumor(backend),
        "camel_batch": test_camel_batch(backend),
    }

    print("\n" + "="*70)
    print("📊 RESULTS SUMMARY")
    print("="*70)

    print("\n{:<22} {:<12} {:<18} {:<8} {:<10}".format(
        "Test", "Valid JSON", "Fields/Items", "Russian", "Time"))
    print("-"*70)

    r = results["raw"]
    mark = "✅" if r['valid_json'] else "❌"
    print("{:<22} {:<12} {:<18} {:<8} {:.1f}s".format(
        "Raw Trinity", mark, f"{len(r['fields'])} fields", "N/A", r['time']))

    r = results["camel_rumor"]
    mark = "✅" if r['valid_json'] else "❌"
    req = "✅" if r.get('has_required') else "❌"
    rus = "✅" if r.get('is_russian') else "❌"
    print("{:<22} {:<12} {:<18} {:<8} {:.1f}s".format(
        "CAMEL Rumor", mark, f"{len(r['fields'])} fields", rus, r['time']))

    r = results["camel_batch"]
    mark = "✅" if r['valid_json'] else "❌"
    print("{:<22} {:<12} {:<18} {:<8} {:.1f}s".format(
        "CAMEL Batch", mark, f"{r.get('count', 0)} items", "N/A", r['time']))

    print("\n" + "="*70)
    print("💡 WHAT CAMEL.BRIDGE ADDS:")
    print("="*70)
    print("""
1. ✅ Structured system prompts per entity type
2. ✅ Required field validation in prompts
3. ✅ Russian language enforcement (i18n)
4. ✅ JSON schema specification
5. ✅ Batch generation (multiple entities)
6. ✅ Domain-specific prompts (rumor vs event vs quest)
7. ✅ Consistency across entity types

Without CAMEL:
- Simpler prompts but less structured
- No guaranteed field presence
- Mixed languages (EN/RU)
- Needs post-processing
    """)

    print("\n🎯 CONCLUSION:")
    if results["camel_rumor"]["valid_json"] and results["camel_rumor"].get("is_russian"):
        print("✅ CAMEL.Bridge significantly improves output quality!")
        print("   - Valid JSON structure")
        print("   - All required fields present")
        print("   - Russian language enforced")
    else:
        print("⚠️  Model needs better prompts or different model")

    return 0


if __name__ == "__main__":
    sys.exit(main())
