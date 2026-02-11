# Frequently Asked Questions

## Getting Started

### Q: Do I need to install a database?
**A:** No! The GUI works with JSON files by default. You can add PostgreSQL later if you need multi-user collaboration or advanced features.

### Q: What is the minimum computer requirement?
**A:** Any computer that can run Python 3.11+ should work. The GUI is lightweight and doesn't require gaming hardware.

### Q: Can I use this on macOS?
**A:** Yes! The GUI runs on macOS, Windows, and Linux. See [platform-specific guides](platform/WINDOWS_SETUP.md) for setup details.

### Q: I don't know Python - can I still use MythWeave?
**A:** Absolutely! The GUI is a visual application. You only need Python installed - you don't need to write any code or understand programming.

### Q: How long does it take to get started?
**A:** You can be running in 2-5 minutes:
- Windows: Double-click `launch_gui.bat` - done!
- macOS/Linux: Run 4 commands - see [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md)

---

## Using the GUI

### Q: Why does my character need a 100-character backstory?
**A:** This is a business rule to ensure characters have depth and detail. Short backstories tend to be generic - longer ones help build rich, memorable characters.

**Tip:** If you're stuck, include:
- The character's origin and upbringing
- Their motivations and goals
- A key life event that shaped them
- Their role in the world

**Example:**
> Born in the slums of Ardent City, Lyra learned to fight before she learned to read. After witnessing her family's murder by the city guard, she vowed to overthrow the corrupt ruling council. Now she leads the underground resistance, using her street smarts and dual daggers to strike from the shadows.

### Q: What's the difference between a "world" and an "event"?
**A:** Think of it like this:
- **World**: The setting (a continent, a kingdom, a universe)
- **Event**: Something that happens (a quest, a war, a discovery)

Characters and abilities exist within worlds. Events happen in worlds, involving characters.

### Q: Can I delete a world if I made a mistake?
**A:** Yes! The GUI will ask for confirmation before deleting. However, deleting a world will also delete all characters and events in that world. Make sure you export/backup first.

### Q: What are power levels? How do I choose the right one?
**A:** Power levels rate ability strength from 1-10:
- **1-3**: Minor abilities, novice level
  - Example: Fire Spark (creates a small flame)
- **4-6**: Competent, useful abilities
  - Example: Ice Shard (creates a projectile of ice)
- **7-8**: Powerful, rare abilities
  - Example: Storm Calling (summon lightning and control weather)
- **9**: Master-level, legendary abilities
  - Example: Dragon Bond (telepathic connection with a dragon)
- **10**: Godlike, world-changing power
  - Example: Reality Manipulation (rewrite the laws of physics)

**Tip:** For starting characters, most abilities should be 3-5. Save 8+ for powerful, rare abilities.

### Q: How many abilities should a character have?
**A:** There's no limit! However, consider:
- **New characters:** 2-4 abilities
- **Experienced characters:** 5-7 abilities
- **Legendary characters:** 8+ abilities

**Focus on quality over quantity** - better to have 3 well-defined abilities than 10 vague ones.

### Q: Can I have the same ability name on different characters?
**A:** Yes! Different characters can have abilities with the same name. The uniqueness rule only applies within a single character.

**Example:** Both Aria and Zephyr could have a "Fireball" ability, even though they're different characters.

### Q: What does "active" vs "inactive" status mean?
**A:**
- **Active**: The character is currently alive, present, and participating in the story
- **Inactive**: The character is missing, presumed dead, or not currently involved

This helps you track which characters are available for new events.

---

## Data Management

### Q: Can I share my lore file with my team?
**A:** Absolutely! The JSON file is plain text and version-control friendly. You can:
- Email the file to teammates
- Use Git to track changes and collaborate
- Share via cloud storage (Dropbox, Google Drive, etc.)

**Recommendation:** For teams, use Git with GitHub or GitLab. This lets you:
- See who changed what
- Compare different versions
- Review changes before merging
- Roll back if something goes wrong

### Q: What happens if I accidentally overwrite my lore file?
**A:** The GUI has "Save As" functionality, so you can always create backups. For production work, we recommend:
- Using Git for version control (init on day one!)
- Regular "Save As" backups with version numbers (e.g., `my_world_v1.json`, `my_world_v2.json`)
- Using a database backend with proper backups (advanced)

### Q: Can I convert my existing lore to MythWeave format?
**A:** Yes! If your lore is in a digital format (text files, spreadsheets, another database), you'll need to convert it to the MythWeave JSON format.

The JSON structure is simple and documented in [GUI_IMPLEMENTATION_SUMMARY.md](gui/GUI_IMPLEMENTATION_SUMMARY.md#data-format).

**Tip:** Start with a few characters or a single world to test the format, then do a bulk conversion.

### Q: Is my data private?
**A:** Yes! By default, all data is stored locally on your computer in JSON files. Nothing is sent to external servers unless you explicitly set up a database or Git integration.

---

## Technical Questions

### Q: What file formats does MythWeave support?
**A:** Currently, the GUI supports JSON files for import/export. JSON is plain text, human-readable, and works well with version control.

Future versions may support additional formats (CSV, YAML, etc.).

### Q: Can I use MythWeave offline?
**A:** Yes! The GUI runs entirely on your computer. No internet connection is required.

### Q: What's the difference between the GUI and the simulator?
**A:**
- **GUI**: Visual interface for creating and managing lore (worlds, characters, events)
- **Progression Simulator**: Advanced tool for testing character advancement and gacha mechanics

Most users start with the GUI. The simulator is for game designers and QA testers who need to verify progression systems.

### Q: When should I use PostgreSQL instead of JSON files?
**A:** Consider PostgreSQL when:
- You have multiple users working simultaneously
- You need advanced search capabilities across thousands of entries
- You want robust backups and transaction support
- You're building production systems

JSON files are great for:
- Individual creators
- Small teams sharing via Git
- Rapid prototyping
- Learning and experimentation

**Start with JSON.** You can always migrate to PostgreSQL later.

### Q: Can I export my data from JSON to PostgreSQL?
**A:** Yes! Migration tools will be provided to move data from JSON to PostgreSQL when you're ready. The data structure is compatible.

---

## Advanced Features

### Q: What is "progression simulation"?
**A:** This is a tool for testing character advancement mechanics (like in RPGs or gacha games). It helps ensure progression systems are balanced and consistent with lore rules.

**Use cases:**
- Test if characters level up at the right pace
- Verify gacha drop rates are fair
- Check if stat increases follow game rules
- Find unintended valid builds

See [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md) for details.

### Q: What are "requirements" and "improvements"?
**A:**
- **Requirements**: Business rules that must always be true (e.g., "Main character cannot die before Act 3")
- **Improvements**: Proposed changes to lore (e.g., "Add a new ability to Zephyr")

Before applying an improvement, the system checks if it violates any requirements. If it does, the improvement is rejected.

This ensures your lore never breaks the rules you've established.

### Q: What is the gacha system?
**A:** Gacha is a game mechanic where players randomly collect characters or items (like pulling from a pack of cards). MythWeave supports:
- Banner management (different character pools)
- Drop rate configuration (e.g., 0.6% SSR rate)
- Pity systems (guaranteed rare after N pulls)
- 50/50 systems (50% chance featured on rare pull)

See [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) for gacha rules and guarantees.

### Q: Can I integrate MythWeave with my game engine?
**A:** Not directly in the current version. However, you can:
- Export lore as JSON
- Write scripts to convert JSON to your game's format
- Use the database backend and query from your game

Future versions may include direct game engine integrations.

---

## Troubleshooting

### Q: The GUI won't start. What do I do?
**A:** Follow these steps:

1. **Check Python version:**
   ```bash
   python --version
   ```
   You need Python 3.11 or higher.

2. **Make sure you're in the virtual environment:**
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Verify PyQt6 is installed:**
   ```bash
   pip list | grep PyQt6
   ```

4. **Check the console output for error messages**

5. **Try the Windows launcher** (if on Windows):
   - Double-click `launch_gui.bat`

If you're still stuck, see the [Troubleshooting section](gui/QUICKSTART_GUI.md#troubleshooting) for more details.

### Q: "Backstory too short" error - what do I do?
**A:** Your backstory needs more detail. Here's a quick checklist:

- [ ] Where is the character from?
- [ ] What motivates them?
- [ ] What's a defining life event?
- [ ] What's their role in the world?

**Aim for 3-4 sentences.** If you're still stuck, imagine you're meeting this character at a tavern. What story would they tell you about themselves?

### Q: "Name already exists" error - what do I do?
**A:** Each world needs a unique name. You have two options:
1. Choose a different name (e.g., "Crystal Peaks" → "Crystal Mountains")
2. Edit the existing world instead of creating a new one

### Q: "Power level must be between 1 and 10" error - what do I do?
**A:** Ability power levels are constrained to 1-10. Adjust the power level in the ability dialog.

**Remember:** 1 is weak, 10 is godlike. Most abilities should be 3-7.

### Q: "Cannot add duplicate ability" error - what do I do?
**A:** Each character can only have one ability with a given name. Either:
1. Choose a different ability name (e.g., "Fireball" → "Inferno")
2. Remove the existing ability first
3. Update the existing ability instead of adding a new one

### Q: I lost my lore file! Can I recover it?
**A:** Recovery options depend on what you did:

**If you used Git:**
```bash
git log  # See history
git checkout <commit-hash>  # Restore from history
```

**If you have backups:**
- Look for `.bak` or `_v2.json` files in your directory
- Check cloud storage (Dropbox, Google Drive)

**If no backups:**
Unfortunately, the file may be lost. We recommend:
- Using Git from day one
- Regular "Save As" backups
- Consider a database with automatic backups

**Prevention is better than cure!**

---

## Best Practices

### Q: How should I organize my lore files?
**A:** Here's a recommended structure:

```
my_project/
├── lore/
│   ├── worlds/
│   │   ├── crystal_peaks.json
│   │   └── shadowmere_wastes.json
│   ├── characters/
│   │   ├── zephyr.json
│   │   └── aria.json
│   └── events/
│       ├── great_reforging.json
│       └── discovery_archives.json
├── campaigns/
│   ├── frostfall.json
│   └── ardent_civil_war.json
└── archives/
    └── old_versions/
```

This keeps your lore organized and makes it easy to find what you need.

### Q: How often should I save?
**A:**
- **After every major change** (new character, major event)
- **Before risky operations** (deleting worlds/characters)
- **At the end of each session**

**Pro tip:** Use Git for automatic version tracking. Every commit is a save point.

### Q: Should I use separate files or one big file?
**A:** It depends on your needs:

**One big file (good for):**
- Small projects (1-2 worlds, <20 characters)
- Quick prototyping
- Simple sharing

**Multiple files (good for):**
- Large projects (many worlds, 50+ characters)
- Teams working on different areas
- Better organization
- Faster loading (load only what you need)

You can always split or merge files later.

### Q: How detailed should my lore be?
**A:** Balance detail with manageability:

**For main characters and worlds:**
- High detail (250+ word backstories)
- Multiple abilities
- Detailed event participation

**For supporting characters:**
- Medium detail (100-150 word backstories)
- 2-3 abilities
- Selective event participation

**For minor characters/NPCs:**
- Minimal detail (100-120 word backstories)
- 1-2 abilities
- Limited event participation

**Tip:** You can always expand later. Start with the essentials, add detail as needed.

---

## Future and Roadmap

### Q: What features are coming soon?
**A:** Planned features include:
- [ ] Events tab in the GUI (currently only available via JSON)
- [ ] Search and filter functionality
- [ ] Export to different formats (PDF, Markdown)
- [ ] Visual relationship graphs
- [ ] Direct game engine integrations
- [ ] Multi-user collaboration features

Check the GitHub issues or project board for the latest roadmap.

### Q: Can I request features?
**A:** Absolutely! We welcome feature requests. Please:
1. Check existing GitHub issues first
2. Search the documentation
3. Open a new issue with:
   - Clear description of the feature
   - Why it would be useful
   - Examples or use cases

---

## Community and Support

### Q: Where can I get help?
**A:** Multiple options:
- **Documentation**: Start here! Check [USER_GUIDE.md](USER_GUIDE.md) and [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md)
- **GitHub Issues**: Report bugs and request features
- **Discord/Community**: Join our Discord for real-time help (link in README)

### Q: Can I contribute to the documentation?
**A:** Yes! Documentation contributions are welcome:
1. Fork the repository
2. Make your changes
3. Submit a Pull Request

We especially appreciate:
- Fixes to unclear sections
- Additional examples
- Screenshots and diagrams
- Translations to other languages

### Q: I found a bug. What do I do?
**A:** Please report bugs via GitHub issues. Include:
- Steps to reproduce the bug
- What you expected to happen
- What actually happened
- Error messages (if any)
- Your OS and Python version

---

**Still have questions?**

- Browse the full documentation in [docs/README.md](README.md)
- Check the [Glossary](GLOSSARY.md) for terminology
- Open an issue on GitHub

Happy lore building! 📚✨
