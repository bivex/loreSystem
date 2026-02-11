# Quick Reference Cards

One-page cheat sheets for common MythWeave tasks. Print these out or keep them open while working!

---

## 🌍 World Creation Card

### Quick Steps

| Step | Action | Requirement |
|------|--------|-------------|
| 1 | Go to "Worlds" tab | - |
| 2 | Enter name | 3-100 characters |
| 3 | Enter description | 10-5000 characters |
| 4 | Click "Add World" | Name must be unique |

### Validation Errors

| Error | Solution |
|-------|----------|
| "Name too short" | Use at least 3 characters |
| "Name already exists" | Choose a different name |
| "Description too short" | Use at least 10 characters |

### Tips

✅ World names should evoke the setting's theme
✅ Describe the atmosphere, geography, and unique features
✅ Think about what makes this world different from others

---

## 👤 Character Creation Card

### Quick Steps

| Step | Action | Requirement |
|------|--------|-------------|
| 1 | Go to "Characters" tab | - |
| 2 | Select world from dropdown | Must exist |
| 3 | Enter name | 3-100 characters |
| 4 | Write backstory | ≥100 characters |
| 5 | Set status | `active` or `inactive` |
| 6 | Add abilities | See Ability Card |
| 7 | Click "Add Character" | Must pass all validation |

### Validation Errors

| Error | Solution |
|-------|----------|
| "Backstory too short" | Add more detail (100+ chars) |
| "Power level must be 1-10" | Adjust power level |
| "Cannot add duplicate ability" | Choose different name |

### Backstory Checklist

Include these for a rich backstory:
- [ ] Origin (where did they come from?)
- [ ] Motivations (what do they want?)
- [ ] Key life event (what shaped them?)
- [ ] Role in the world (who are they to others?)

---

## ⚡ Ability Card

### Quick Steps

| Step | Action | Requirement |
|------|--------|-------------|
| 1 | Click "Add Ability" | - |
| 2 | Enter name | Unique per character |
| 3 | Enter description | 10-500 characters |
| 4 | Set power level | 1-10 |
| 5 | Click "OK" | - |
| 6 | Repeat for all abilities | - |

### Power Level Guide

| Level | Strength | Examples |
|-------|----------|----------|
| **1-3** | Minor, novice | Fire Spark, Minor Heal |
| **4-6** | Competent, useful | Ice Shard, Lightning Bolt |
| **7-8** | Powerful, rare | Storm Calling, Void Blast |
| **9** | Legendary, master | Dragon Bond, Time Freeze |
| **10** | Godlike, world-changing | Reality Manipulation |

### Tips

✅ Most characters: 2-4 abilities
✅ New characters: Power levels 3-6
✅ Save 8+ for rare, special abilities
✅ Quality over quantity

---

## 💾 Data Management Card

### File Operations

| Action | Button | When to Use |
|--------|--------|-------------|
| Save | "Save" | Update current file |
| Save As | "Save As" | Create backup / new file |
| Load | "Load" | Open existing lore file |
| New | "New" | Start fresh |

### Git Quick Start

```bash
# Initialize
git init

# Add file
git add my_world.json

# Commit
git commit -m "Added Crystal Peaks world"

# View history
git log

# Revert to version
git checkout <commit-hash>
```

### Backup Strategy

| Frequency | Action |
|-----------|--------|
| Every session | "Save" |
| Major changes | "Save As" with version |
| End of day | Git commit |
| Weekly | External backup |

---

## 🎭 Common Workflows Card

### Creating a New World (30-60 min)

1. Launch GUI
2. Create world (World Card)
3. Add 2-3 characters (Character Card)
4. Add abilities (Ability Card)
5. Save As: `my_world.json`
6. Git commit: "Initial world"

### Expanding Story (20-40 min)

1. Load: `my_world.json`
2. Review existing content
3. Add new characters/events
4. Update existing content
5. Save
6. Git commit: "Added Zephyr Stormrider"

### Testing Progression (30-60 min)

1. Load test lore
2. Run progression simulator
3. Verify rules pass
4. Document results
5. Report bugs if found

---

## ⚠️ Troubleshooting Card

### Error → Solution Quick Match

| Error | Quick Fix |
|-------|-----------|
| "Backstory too short" | Add 1-2 more sentences |
| "Name already exists" | Choose different name |
| "Power level 1-10" | Adjust power level |
| "Duplicate ability" | Change ability name |
| GUI won't start | Check Python 3.11+ |
| PyQt6 not found | `pip install PyQt6` |
| Can't save file | Check permissions |

### Before Asking for Help

Check these in order:
1. [ ] Python version is 3.11+
2. [ ] Virtual environment activated
3. [ ] PyQt6 installed
4. [ ] Read error message
5. [ ] Checked FAQ.md
6. [ ] Searched documentation

---

## 📊 Validation Rules Summary

### Worlds
- Name: 3-100 chars
- Description: 10-5000 chars
- Unique per tenant

### Characters
- Name: 3-100 chars
- Backstory: ≥100 chars
- Status: active/inactive
- Abilities: Power level 1-10

### Abilities
- Name: Unique per character
- Description: 10-500 chars
- Power level: 1-10

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Tab | Next field |
| Shift+Tab | Previous field |
| Enter | Submit form |

**Coming soon:** Ctrl+S (save), Ctrl+O (open), Ctrl+N (new)

---

## 🎯 Quality Checklist

### Character Review

- [ ] Backstory ≥100 characters
- [ ] Backstory includes origin, motivations, key event
- [ ] 2-7 abilities
- [ ] Power levels balanced (3-6 for normal, 8+ for rare)
- [ ] Ability names descriptive
- [ ] Status correct (active/inactive)

### World Review

- [ ] Name unique and evocative
- [ ] Description ≥10 characters
- [ ] Describes geography/atmosphere
- [ ] At least 2 characters (if populated)

### Lore Review

- [ ] All names spelled consistently
- [ ] Character relationships documented
- [ ] Events follow logical progression
- [ ] No duplicate names (within scope)
- [ ] Git commit messages descriptive

---

## 🔍 Search Tips (Future)

When search is implemented:

### Character Search
- "dragon" → Find all characters with "dragon" in backstory
- "ability:fire" → Find characters with fire abilities
- "world:crystal" → Find characters in Crystal Peaks world

### World Search
- "magic" → Find worlds with "magic" in description
- "characters:5+" → Find worlds with 5+ characters

### Event Search
- "war" → Find all war events
- "participant:Aria" → Find events involving Aria

---

## 📝 Naming Conventions

### World Names
✅ **Good:** Crystal Peaks, Shadowmere Wastes, Ardent Kingdom
❌ **Bad:** World 1, Test World, A

### Character Names
✅ **Good:** Zephyr Stormrider, Lyra Iceweaver, Grom Stonefist
❌ **Bad:** Char1, Test Char, Bob

### Ability Names
✅ **Good:** Dragon Bond, Storm Calling, Void Manipulation
❌ **Bad:** Ability 1, Fire Thing, Big Attack

---

## 🚀 Next Steps

### After Creating Basic Lore

1. **Add Events** (via JSON or wait for GUI)
2. **Set Up Git** for version control
3. **Create Backup Strategy**
4. **Test Progression** (if making RPG)
5. **Invite Team** (if collaborating)

### Learning Resources

- [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md) - Full walkthrough
- [FAQ.md](FAQ.md) - Common questions
- [GLOSSARY.md](GLOSSARY.md) - Terminology
- [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) - Domain rules

---

## 💡 Pro Tips

### Character Creation
- Write backstories as if meeting at a tavern
- Give characters flaws and weaknesses
- Link characters to each other (friends, enemies, family)
- Think about character arcs (how will they change?)

### World Building
- Start with one unique feature
- Build around that feature
- Consider history, culture, politics
- Leave room for expansion

### Workflow
- Save early, save often
- Use Git from day one
- Create regular backups
- Document major decisions

---

**Print these cards and keep them handy!** 📄

For detailed information, see the full documentation in [docs/README.md](README.md).
