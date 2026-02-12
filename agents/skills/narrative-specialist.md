---
name: loresystem-narrative
description: Extract narrative entities (story, chapter, act, episode, prologue, epilogue, plot_branch, branch_point) from loreSystem source files into structured JSON.
---

# Narrative Specialist

## Purpose

The Narrative Specialist extracts narrative entities from loreSystem source files, focusing on the structural elements of stories, acts, chapters, and branching narrative paths.

## Entity Types

### Primary Entities

- **story**: Top-level narrative container for complete story arcs
- **chapter**: Individual narrative segments within stories or acts
- **act**: Major narrative divisions within a story
- **episode**: Self-contained narrative units (for episodic content)
- **prologue**: Opening narrative segments before the main story
- **epilogue**: Closing narrative segments after the main story

### Branching Entities

- **plot_branch**: Alternative narrative paths based on player choices
- **branch_point**: Decision nodes where the narrative diverges

## Extraction Process

1. Read source file content
2. Identify narrative structure markers
3. Extract entity attributes (title, description, sequence, connections)
4. Build relationships between entities (parent-child, sequential, conditional)
5. Output valid JSON structure

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (optional)
