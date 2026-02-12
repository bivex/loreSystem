---
name: loresystem-political
description: Extract political entities (government, law, legal_system, court, judge, jury, lawyer, crime, punishment, evidence, witness, treaty, constitution) from loreSystem source files into structured JSON.
---

# Political Scientist

## Purpose

The Political Scientist extracts political and legal entities from loreSystem source files, covering governments, laws, courts, crimes, and international relations.

## Entity Types

### Governance

- **government**: Ruling bodies and political systems
- **law**: Specific laws and regulations
- **legal_system**: Overall legal frameworks
- **treaty**: Agreements between factions/nations
- **constitution**: Founding legal documents

### Legal Proceedings

- **court**: Judicial bodies and venues
- **judge**: Judicial authorities
- **jury**: Decision-making bodies in trials
- **lawyer**: Legal representatives and advocates

### Crime and Justice

- **crime**: Illegal acts and offenses
- **punishment**: Penalties and sentences
- **evidence**: Proof and documentation in legal cases
- **witness**: Testifiers in legal proceedings

## Extraction Process

1. Identify government types and structures
2. Extract laws and legal provisions
3. Document court systems and procedures
4. Note key legal figures (judges, lawyers)
5. Extract crime definitions and categories
6. Document punishment types and severity
7. Map treaties and agreements
8. Track legal precedents and constitutions

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for legal hierarchy and treaty participants)
