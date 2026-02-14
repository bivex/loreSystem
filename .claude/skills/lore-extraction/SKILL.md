---
name: lore-extraction
description: Base extraction rules for all lore subagents. Governs entity identification, contextual analysis, relationship mapping, and JSON output formatting.
user-invocable: false
---
# lore-extraction

Base skill for all loreSystem extraction subagents. Common rules for extracting entities from narrative text.

## Extraction Pipeline

1. **Read** the source text completely before extracting
2. **Identify** entities — look for named things, described systems, relationships
3. **Classify** each entity to its correct type from the entity ownership map
4. **Extract** fields — name, description, type-specific attributes
5. **Link** related entities via ID references or cross-references
6. **Validate** against domain model constraints
7. **Output** as JSON following the json-formatter schema

## Entity Identification Rules

- Named entities (proper nouns, titles) → extract with exact name
- Described systems (magic system, economy) → extract with descriptive name
- Implied entities (unnamed but significant) → extract with contextual name
- Groups/collections → extract as single entity with members in description

## Cross-Domain References

When text mentions an entity owned by another skill:
- Do NOT create the entity — it belongs to the other skill
- Add a `cross_references` entry pointing to the other skill
- Include enough context in `target_hint` for the lead to merge

## Quality Rules

- Extract only what the text explicitly states or strongly implies
- Do not invent details not supported by the text
- Mark uncertain extractions with `"confidence": "low"` in metadata
- Prefer fewer high-quality entities over many low-quality ones
