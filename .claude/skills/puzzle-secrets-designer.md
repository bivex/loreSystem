---
name: loresystem-puzzle
description: Extract puzzle entities (secret_area, hidden_path, easter_egg, mystery, enigma, riddle, puzzle, trap) from loreSystem source files into structured JSON.
---

# puzzle-secrets-designer

**OpenClaw Subagent** - Puzzles, secrets, and hidden content analysis for loreSystem.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract puzzle entities"
- "analyze secrets and mysteries"
- "identify hidden content"
- "extract puzzle/riddle/trap/secret"
- "puzzle design analysis"

## Domain Expertise

Puzzles, secrets, traps, and hidden content:
- **Puzzles**: Logic puzzles, mechanical puzzles, riddles
- **Secrets**: Hidden areas, secret paths, Easter eggs
- **Traps**: Mechanical, magical, environmental hazards
- **Mysteries**: Unsolved enigmas, lore mysteries
- **Difficulty scaling**: Puzzles from trivial to impossible
- **Hint systems**: Clues, gradual reveal, optional difficulty settings

## Entity Types (7 total)

- **hidden_path** - Hidden paths
- **easter_egg** - Easter eggs
- **mystery** - Mysteries
- **enigma** - Enigmas
- **riddle** - Riddles
- **puzzle** - Puzzles
- **trap** - Traps

## Processing Guidelines

When extracting puzzle and secret entities from chapter text:

1. **Identify puzzle/secret elements**
   - Riddles or clues mentioned
   - Hidden paths or secret passages
   - Puzzles or mechanical challenges
   - Traps or hazards
   - Easter eggs or secrets
   - Mysteries or enigmas

2. **Extract puzzle/secret details**
   - Puzzle types, solutions, difficulty
   - Hidden path access methods
   - Trap triggers and effects
   - Riddle content and answers
   - Easter egg locations and rewards

3. **Analyze puzzle/secret context**
   - Optional vs required content
   - Hint availability (optional hints, fair puzzles)
   - Difficulty scaling (early game vs late game)
   - Reward scaling (better secrets = better rewards)

4. **Create entities** following loreSystem schema

## Output Format

Generate `entities/puzzle.json` with schema-compliant entities:

```json
{
  "puzzle": {
    "id": "uuid",
    "name": "Rune Circle Puzzle",
    "type": "logic_mechanical",
    "location_id": "ancient_ruins",
    "difficulty": "medium",
    "hint_available": true,
    "solution": "light_runes_in_clockwise_order",
    "reward": "ancient_artifact"
  },
  "riddle": {
    "id": "uuid",
    "name": "Gatekeeper's Riddle",
    "type": "word_play",
    "content": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
    "answer": "echo",
    "attempts_allowed": 3,
    "hint": "Think about sound and mountains"
  },
  "trap": {
    "id": "uuid",
    "name": "Floor Trigger",
    "type": "mechanical_pressure",
    "location_id": "ancient_ruins_hallway",
    "trigger": "step_on_pressure_plate",
    "effect": "poison_dart_cloud",
    "damage": "50_poison",
    "disarm_method": "disable_pressure_plate",
    "disarm_difficulty": "easy_perception_check"
  }
}
```

## Key Considerations

- **Fairness**: Puzzles should have logical solutions
- **Hint systems**: Players should have access to hints if stuck
- **Optional content**: Secrets shouldn't block main story
- **Difficulty scaling**: Puzzles should match player progress
- **Multiple solutions**: Some puzzles allow creative solutions
- **Trap balance**: Traps shouldn't be unfair or instant-death

## Example

**Input:**
> "The gatekeeper stood before the ancient ruins. 'Answer this riddle: I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?' Kira thought—echo! The wall shimmered, revealing a secret path. Inside, she nearly stepped on a pressure plate, but noticed it. Traps—poison darts. The prophecy fragment read: 'When light meets shadow, the third path opens.'"

**Extract:**
- Riddle: Gatekeeper's riddle (word play, answer: echo, 3 attempts, hint: sound and mountains)
- Hidden path: Secret Grove Entrance (illusion wall, solve riddle access, low discovery rate, secret shrine + rare herbs)
- Trap: Floor Trigger (mechanical pressure plate, poison darts, 50 damage, disarm: disable plate, easy perception check)
- Enigma: Ancient Prophecy Fragment (cryptic text, solar eclipse or conflict interpretations, third path)
- Puzzle context: Riddle → hidden path → trap avoidance → enigma
- Difficulty balance: Riddle = fair (hint available), Trap = fair (noticeable, disarable)
- Secret scaling: Low discovery rate = valuable contents (shrine + herbs)
- Mystery connection: Prophecy fragment tied to main quest ("third path opens")
- Optional content: Hidden path and prophecy are optional side content
- Player agency: Multiple solution paths (solve riddle, notice trap, interpret prophecy)
