# historical-research

Domain skill for historian subagent. Specific extraction rules and expertise.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract historical entities"
- "analyze eras and timelines"
- "identify festivals and ceremonies"
- "historical events and calendars"
- "cultural events and tournaments"

## Domain Expertise

- **Historical periods**: Eras, ages, epochs, historical timelines
- **Chronology**: Timelines, cause-effect relationships, historical flow
- **Cultural events**: Festivals, tournaments, ceremonies, celebrations
- **Calendars**: Different timekeeping systems, calendar formats
- **Historical transitions**: Wars, revolutions, golden ages, era changes

## Entity Types (10 total)

- **era** - Historical eras, ages, time periods
- **era_transition** - Era transitions, period changes
- **timeline** - Timelines, chronological sequences
- **calendar** - Calendar systems, timekeeping
- **festival** - Festivals, recurring celebrations
- **celebration** - Celebrations, joyous events
- **ceremony** - Ceremonies, ritual observances
- **exhibition** - Exhibitions, displays, showcases
- **tournament** - Tournaments, competitions
- **competition** - Competitions, contests

## Processing Guidelines

When extracting historical entities from chapter text:

1. **Identify historical references**:
   - Past eras mentioned (Age of Magic, Great War era, Industrial Age)
   - Historical events described (wars, revolutions, discoveries)
   - Cultural traditions or rituals (annual festivals, ceremonies)
   - Calendar systems or time references (lunar calendar, solar cycle)

2. **Extract historical details**:
   - Era names, timeframes, characteristics (Golden Age, Dark Times)
   - Timeline events, dates, sequences (what happened when)
   - Cultural practices, festivals, traditions (annual celebrations)
   - Calendar systems, holidays, special dates

3. **Contextualize in history**:
   - When did events happen relative to each other (chronological order)
   - What caused era transitions (wars, discoveries, cataclysms)
   - How historical context affects current story events
   - Multiple perspectives on history (different cultures may have different accounts)

4. **Analyze cultural significance**:
   - Meaning behind festivals and ceremonies
   - Historical importance of tournaments
   - Cultural memory and historical identity
   - How the past influences the present

## Output Format

Generate `entities/historical.json` with schema-compliant entities following this structure:
```json
{
  "era": {
    "id": "uuid",
    "name": "Age of Magic",
    "start_date": "ancient",
    "end_date": "pre-great_war",
    "description": "Time when magic was abundant"
  },
  "era_transition": {
    "id": "uuid",
    "from_era_id": "...",
    "to_era_id": "...",
    "cause": "Great War",
    "description": "Magic waned after the Great War"
  },
  "timeline": {
    "id": "uuid",
    "name": "Eldorian History",
    "events": ["Age of Magic", "Great War", "Age of Restoration"]
  },
  "festival": {
    "id": "uuid",
    "name": "Festival of Lights",
    "frequency": "annual",
    "season": "winter",
    "significance": "Remembers the lost"
  }
}
```

## Key Considerations

- **Relative time**: Not all systems use absolute dates (some use "cycles" or "ages")
- **Cultural significance**: Festivals often have deeper meanings beyond celebration
- **Historical impact**: Past events affect current story state and character motivations
- **Multiple perspectives**: History may differ by culture (victors write history)
- **Chronological context**: Establish what came before and after
- **Historical memory**: How characters remember and relate to the past

## Example

**Input:**
> "The elder spoke of the Age of Magic, when sorcerers ruled the skies. But the Great War changed everything. Now, in the Age of Restoration, we gather each winter for the Festival of Lights, remembering those lost."

**Extract:**
```json
{
  "era": {
    "id": "uuid",
    "name": "Age of Magic",
    "timeframe": "ancient",
    "characteristics": "sorcerers ruled the skies, magic abundant",
    "status": "past"
  },
  "era": {
    "id": "uuid",
    "name": "Age of Restoration",
    "timeframe": "current",
    "characteristics": "post-war rebuilding",
    "status": "current"
  },
  "era_transition": {
    "id": "uuid",
    "name": "The Great War Transition",
    "from_era": "Age of Magic",
    "to_era": "Age of Restoration",
    "cause": "Great War",
    "description": "Magic waned, world changed forever"
  },
  "festival": {
    "id": "uuid",
    "name": "Festival of Lights",
    "frequency": "annual",
    "season": "winter",
    "significance": "Remembers those lost in the Great War",
    "traditions": "gathering, lighting lights"
  },
  "timeline": {
    "id": "uuid",
    "name": "Eldorian Historical Timeline",
    "sequence": ["Age of Magic", "Great War", "Age of Restoration"],
    "description": "Major eras of Eldorian history"
  }
}
```
