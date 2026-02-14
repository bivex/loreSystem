---
name: json-formatter
description: JSON formatting rules for lore entity output. Enforces strict JSON, UUID identifiers, arrays per entity type, cross-references, and loreSystem schema compliance.
user-invocable: false
---
# json-formatter

Base skill for JSON output formatting. All extraction skills produce JSON following these rules.

## Rules

1. **Valid JSON**: Output must be parseable JSON — no trailing commas, no comments
2. **UUID for id**: Every entity gets a unique UUID v4 identifier
3. **Arrays per type**: Each entity type is a top-level key containing an array of entities
4. **Cross-references**: References to entities owned by other skills go in `cross_references` array
5. **Metadata**: Include `_metadata` with source file, skill name, timestamp, entity count
6. **Schema compliance**: Follow loreSystem domain model field names and types exactly

## Output Structure

```json
{
  "entity_type": [
    { "id": "uuid", "name": "Entity Name", "description": "..." }
  ],
  "cross_references": [
    {
      "source_type": "entity_type",
      "source_id": "uuid",
      "target_type": "other_type",
      "target_skill": "other-skill",
      "target_hint": "Referenced entity name or description"
    }
  ],
  "_metadata": {
    "source": "filename.txt",
    "skill": "skill-name",
    "extracted_at": "ISO-8601",
    "entity_count": 1
  }
}
```

## Required Fields

Every entity MUST have: `id` (UUID v4), `name` (string, max 255), `description` (string).

## Additional Resources

- For entity type ownership (which skill owns which types), see [entity-ownership.md](entity-ownership.md)
- For detailed schema, enums, and validation rules, see [output-schema.md](output-schema.md)
