---
name: political-analysis
description: Extract political and legal entities from narrative text. Use when analyzing governments, laws, courts, crimes, punishments, treaties, constitutions, and legal systems.
---
# political-analysis

Domain skill for political and legal system extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `government` | Ruling body or political system |
| `law` | Law, regulation, or decree |
| `legal_system` | Legal framework or justice system |
| `court` | Court or judicial body |
| `judge` | Judge or magistrate |
| `jury` | Jury or decision panel |
| `lawyer` | Lawyer, advocate, or legal representative |
| `crime` | Crime or offense |
| `punishment` | Punishment or penalty |
| `evidence` | Evidence or proof |
| `witness` | Witness or testimony |
| `treaty` | Treaty or international agreement |
| `constitution` | Constitution or founding document |

## Extraction Rules

1. **Government structure**: Type (monarchy, democracy, theocracy, oligarchy), who rules
2. **Laws**: What is legal/illegal, penalties, enforcement
3. **Legal proceedings**: Trials, hearings, verdicts, judicial process
4. **Crimes**: Type, severity, accused, victim
5. **Treaties**: Parties involved, terms, enforcement mechanisms

## Output Format

Write to `entities/society.json` (society-team file):

```json
{
  "government": [
    {
      "id": "uuid",
      "name": "Eldorian Council",
      "description": "Oligarchic council of elders ruling Eldoria",
      "type": "oligarchy"
    }
  ],
  "law": [
    {
      "id": "uuid",
      "name": "Anti-Magic Decree",
      "description": "Forbids use of dark magic within city walls",
      "punishment": "imprisonment"
    }
  ],
  "cross_references": [
    {
      "source_type": "government",
      "source_id": "uuid",
      "target_type": "faction",
      "target_skill": "faction-design",
      "target_hint": "Eldorian Council is also a political faction"
    }
  ],
  "_metadata": { "source": "...", "skill": "political-analysis", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Implicit laws**: Cultural norms not written as statutes
- **Power corruption**: Official systems vs actual power (de jure vs de facto)
- **Multiple legal systems**: Different groups may have different laws
- **Cross-references**: Governments → factions; judges → characters
