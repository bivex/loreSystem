---
name: narrative-writing
description: Extract narrative structure entities from text. Use when analyzing stories, chapters, acts, episodes, prologues, epilogues, plot branches, and story arc progression.
---
# narrative-writing

Domain skill for narrative-specialist subagent. Specific extraction rules and expertise.

## Domain Expertise

Narrative structure, storytelling, and dramatic elements:
- **Narrative structure**: Three-act structure, hero's journey, story arcs
- **Dramaturgy**: Pacing, tension, climaxes, resolutions
- **Chapter organization**: How chapters build on each other
- **Plot branching**: When and how stories diverge
- **Prologues/epilogues**: Setup and payoff, framing devices

## Entity Types (8 total)

- **story** - Main narrative container
- **chapter** - Individual story chapters
- **act** - Story acts (major divisions)
- **episode** - Story episodes (subdivisions)
- **prologue** - Introduction/backstory
- **epilogue** - Conclusion/aftermath
- **plot_branch** - Story branch points
- **branch_point** - Decision points in narrative

## Processing Guidelines

When extracting narrative entities from chapter text:

1. **Identify story structure**
   - Is this a new story or continuation?
   - What act/chapter/episode does this represent?
   - Are there prologue/epilogue elements?

2. **Extract narrative elements**
   - Story arc progression
   - Chapter boundaries and transitions
   - Branching decisions or multiple outcomes
   - Setup/payoff moments

3. **Create entities** following loreSystem schema

4. **Link entities**
   - All chapters reference their story
   - Episodes reference their chapters
   - Branch points reference their parent entities

## Output Format

Generate `entities/narrative.json` with all extracted entities:

```json
{
  "story": { "id": "uuid", "title": "...", "summary": "..." },
  "chapter": { "id": "uuid", "story_id": "...", "number": 1, "title": "..." },
  "act": { "id": "uuid", "story_id": "...", "number": 1, "title": "..." }
}
```

## Key Considerations

- **Continuity**: Ensure chapter numbers and references are consistent
- **Pacing**: Identify where acts/episodes should break
- **Branching**: Capture all possible narrative paths
- **Thematic elements**: Note recurring themes, motifs, symbolism

## Example

**Input:**
> "Chapter 7: The Awakening. As dawn broke over Eldoria, Kira realized her journey was just beginning. Two paths lay before her..."

**Extract:**
- Chapter 7 with proper ordering
- Potential plot branch (two paths before Kira)
- Act structure (beginning vs middle of story)
