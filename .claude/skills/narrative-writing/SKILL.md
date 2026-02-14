---
name: narrative-writing
description: Extract narrative structure entities from text. Use when analyzing stories, chapters, acts, episodes, prologues, epilogues, plot branches, campaigns, events, and story arc progression.
---
# narrative-writing

Domain skill for narrative structure extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `story` | Main narrative container |
| `chapter` | Individual story chapter |
| `act` | Major story division (three-act structure) |
| `episode` | Story episode or subdivision |
| `prologue` | Introduction, backstory setup |
| `epilogue` | Conclusion, aftermath |
| `plot_branch` | Story branch or divergence |
| `branch_point` | Decision point in narrative |
| `alternate_reality` | Alternative timeline or reality |
| `consequence` | Outcome of a decision or event |
| `ending` | Story ending variant |
| `campaign` | Multi-story campaign container |
| `event` | Narrative event or incident |
| `event_chain` | Sequence of linked events |

## Extraction Rules

1. **Identify narrative structure**: Is this a new story or continuation? What act/chapter/episode?
2. **Extract hierarchy**: Stories contain acts, acts contain chapters, chapters contain episodes
3. **Track branching**: Decision points, alternative paths, multiple outcomes
4. **Link events**: Events chain together; track cause-and-effect sequences
5. **Note pacing**: Where acts break, where tension rises/falls

## Output Format

Write to `entities/narrative.json`:

```json
{
  "story": [
    { "id": "uuid", "name": "The Shadow War", "description": "...", "type": "linear" }
  ],
  "chapter": [
    { "id": "uuid", "name": "Chapter 1: Awakening", "description": "...", "story_id": "story-uuid", "number": 1 }
  ],
  "event": [
    { "id": "uuid", "name": "The Great Battle", "description": "...", "outcome": "ongoing" }
  ],
  "cross_references": [],
  "_metadata": { "source": "...", "skill": "narrative-writing", "extracted_at": "...", "entity_count": 3 }
}
```

## Key Considerations

- **Continuity**: Chapter numbers and story references must be consistent
- **Hierarchy**: All chapters reference their story; episodes reference chapters
- **Branching**: Capture all possible narrative paths at branch points
- **Events own characters by reference**: Characters mentioned in events go to cross_references targeting character-design
