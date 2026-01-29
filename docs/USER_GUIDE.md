# MythWeave Chronicles User Guide

## Front Matter
**Title:** MythWeave Chronicles User Guide
**Version:** 2.0
**Date:** January 29, 2026
**Authors:** MythWeave Development Team
**Revision History:**
- v1.0 (January 23, 2026): Initial structure
- v2.0 (January 29, 2026): Complete rewrite with user-focused content

---

## What is MythWeave?

**MythWeave Chronicles is a lore management platform for game developers and storytellers.**

Think of it as a structured database for your game's world, characters, events, and storylines. Whether you're building an RPG, writing a novel, or managing a collaborative world-building project, MythWeave helps you:

✅ Keep your lore organized and consistent
✅ Enforce business rules automatically
✅ Track changes over time
✅ Collaborate with your team
✅ Validate progression systems and game mechanics

## Who This Guide Is For

This guide helps you install, configure, use, and troubleshoot MythWeave. It's written for:

- **Game Designers**: Creating and managing game worlds, tracking character progression
- **Writers**: Developing character backstories, maintaining narrative consistency
- **QA Testers**: Verifying game content matches lore specifications
- **Project Managers**: Tracking lore development progress, managing team contributions

## Table of Contents

1. [Quick Start](#quick-start) - Get running in 5 minutes
2. [Installation and Configuration](#installation-and-configuration) - Detailed setup instructions
3. [User Personas](#user-personas) - Find the section for your role
4. [Creating Your First World](#creating-your-first-world) - Step-by-step tutorial
5. [Managing Characters](#managing-characters) - Building memorable characters
6. [Working with Events](#working-with-events) - Tracking story beats
7. [Data Management](#data-management) - Save, load, export, import
8. [Common Workflows](#common-workflows) - Real-world usage examples
9. [Troubleshooting](#troubleshooting) - Solve common problems
10. [Uninstallation](#uninstallation) - Removing MythWeave safely

---

## Quick Start

### You Can Be Running in 5 Minutes

**Option 1: Windows (Easiest)**
1. Navigate to the `loreSystem` folder
2. Double-click `launch_gui.bat`
3. Wait for automatic setup to complete
4. The MythWeave GUI will open automatically

**That's it!** No manual steps required.

---

**Option 2: macOS/Linux (4 Commands)**

Open a terminal and run:

```bash
cd /path/to/loreSystem
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 run_gui.py
```

### What Happens Next?

1. The GUI opens with three tabs: **Worlds**, **Characters**, **Events**
2. Click **"Load"** and navigate to `examples/sample_lore.json`
3. Explore the sample data to see how MythWeave structures lore
4. When ready, click **"New"** to create your own world

**For a detailed walkthrough**, see [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md).

---

## Installation and Configuration

### System Requirements

**Minimum Requirements:**
- Python 3.11 or higher
- 100 MB free disk space
- Any modern operating system (Windows, macOS, Linux)

**Recommended:**
- 512 MB free disk space (for lore files and backups)
- A code editor (optional, but helpful)

**You do NOT need:**
- ❌ A database (PostgreSQL is optional)
- ❌ Specialized hardware
- ❌ Programming knowledge
- ❌ Internet connection (runs offline)

### Full Installation Guide

#### Step 1: Verify Python Installation

Open a terminal or command prompt:

```bash
python --version
# OR
python3 --version
```

You should see: `Python 3.11.0` or higher.

**If Python is not installed:**
- Download from [python.org](https://python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation
- Restart your terminal after installation

---

#### Step 2: Navigate to Project Directory

```bash
cd /path/to/loreSystem
```

**If you don't know the path:**
- Windows: Right-click the `loreSystem` folder → "Copy as path"
- macOS/Linux: Drag the folder into the terminal

---

#### Step 3: Create Virtual Environment (Recommended)

A virtual environment keeps MythWeave's dependencies separate from your system Python.

```bash
python3 -m venv venv
```

**What this does:** Creates a `venv` folder with an isolated Python environment.

---

#### Step 4: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate.bat
```

**How to know it's activated:** Your terminal prompt will show `(venv)` at the beginning.

---

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

**What this installs:** All required Python packages including PyQt6 (the GUI framework).

**This may take a few minutes.**

---

#### Step 6: Launch the GUI

```bash
python run_gui.py
```

The MythWeave GUI should open!

### Advanced Configuration (Optional)

**For most users, no configuration is needed.** The GUI works with JSON files by default.

**Advanced users** can customize behavior by editing `config/config.yaml`:

```yaml
database:
  type: json  # or "postgresql" for multi-user support
  host: localhost
  port: 5432

search:
  type: none  # or "elasticsearch" for full-text search

git:
  enabled: true
  repository_path: ./lore-repo
```

**When to configure:**
- You need multi-user collaboration (use PostgreSQL)
- You need advanced search (use Elasticsearch)
- You want automatic Git integration (enable Git)

**When to skip configuration:**
- Individual creator
- Small team sharing via Git manually
- Rapid prototyping
- Learning and experimentation

---

## User Personas

Choose the section below that matches your role:

### 🎮 Scenario 1: Game Designer - Creating a New World

**You are:** Building a fantasy RPG from scratch
**You need to:** Create worlds, define characters, establish game rules
**Jump to:** [Creating Your First World](#creating-your-first-world)

### 📖 Scenario 2: Writer - Expanding an Existing Story

**You are:** Adding new characters and events to an established world
**You need to:** Edit existing lore, add new storylines, ensure consistency
**Jump to:** [Managing Characters](#managing-characters)

### 🧪 Scenario 3: QA Tester - Verifying Game Content

**You are:** Checking that game implementation matches lore specifications
**You need to:** Search lore, validate rules, compare against game data
**Jump to:** [Common Workflows → Testing Game Progression Systems](#workflow-4-testing-game-progression-systems)

### 👥 Scenario 4: Project Manager - Tracking Progress

**You are:** Managing a team building game content
**You need to:** Review changes, manage version history, coordinate team efforts
**Jump to:** [Common Workflows → Reviewing Team Contributions](#workflow-3-reviewing-team-contributions)

### ⚙️ Scenario 5: Advanced User - Full Stack Setup

**You are:** Implementing the complete system with database and search
**You need to:** Configure PostgreSQL, Elasticsearch, Git integration
**Jump to:** [Advanced Configuration](#advanced-configuration-optional) or see [design/IMPLEMENTATION_GUIDE.md](design/IMPLEMENTATION_GUIDE.md)

---

## Creating Your First World

### Step 1: Launch the GUI and Go to Worlds Tab

1. Start the GUI (see [Quick Start](#quick-start))
2. Click the **"Worlds"** tab at the top

You'll see a table on the left (currently empty) and a form on the right.

### Step 2: Enter World Details

Fill in the form fields:

**Name:** `Crystal Peaks`
- **Requirement:** 3-100 characters
- **Tip:** Choose a name that evokes the world's theme

**Description:** `Towering mountains of crystallized magic where dragons make their homes and ancient wizards seek enlightenment. The peaks shimmer with elemental energy, and ancient ruins dot the landscape, hinting at a forgotten civilization.`
- **Requirement:** 10-5000 characters
- **Tip:** Describe the setting, atmosphere, and unique features

### Step 3: Add the World

Click the **"Add World"** button.

**What happens:**
- The world is validated against business rules
- A success message appears
- The world appears in the table on the left
- The form clears, ready for the next world

### Common Validation Errors

**❌ "Name too short"** - Use at least 3 characters
**❌ "Name already exists"** - Each world needs a unique name
**❌ "Description too short"** - Use at least 10 characters

### Step 4: Create Additional Worlds (Optional)

Repeat steps 2-3 to create more worlds.

**Example worlds to try:**
- `Shadowmere Wastes` - A dark, corrupted realm
- `Ardent Kingdom` - A bustling medieval kingdom
- `Eldritch Depths` - An underwater civilization

---

## Managing Characters

### Step 1: Go to Characters Tab

Click the **"Characters"** tab at the top of the GUI.

### Step 2: Select a World

Use the dropdown menu to choose which world your character belongs to.

**Example:** Select "Crystal Peaks" (the world you just created)

### Step 3: Enter Character Details

Fill in the character form:

**Name:** `Zephyr Stormrider`
- **Requirement:** 3-100 characters
- **Tip:** Choose a name that fits the world's theme

**Backstory:** A dragon rider bonded with the legendary storm dragon Tempest. Raised among the clouds of Crystal Peaks, Zephyr mastered the art of aerial combat and weather manipulation at a young age. Now serves as guardian of the mountain realm, protecting it from those who would exploit its magical crystals.

**Requirement:** At least 100 characters!

**Why the minimum?** Short backstories tend to be generic. Longer backstories create rich, memorable characters.

**If you're stuck on backstory, include:**
- Where the character came from
- What motivates them
- A key life event that shaped them
- Their role in the world

**Status:** `active` (or `inactive` if the character is missing/dead)

### Step 4: Add Abilities

Abilities define what a character can do. Click **"Add Ability"** for each ability:

**Ability 1:**
- **Name:** `Dragon Bond`
- **Description:** `Telepathic connection with storm dragon Tempest`
- **Power Level:** `9`

**Ability 2:**
- **Name:** `Storm Calling`
- **Description:** `Summon lightning and control weather patterns`
- **Power Level:** `7`

**Understanding Power Levels:**
- **1-3**: Minor abilities, novice level
- **4-6**: Competent, useful abilities
- **7-8**: Powerful, rare abilities
- **9**: Master-level, legendary abilities
- **10**: Godlike, world-changing power

**Tip:** Most characters should have 2-4 abilities. For new characters, aim for power levels 3-6.

### Step 5: Add the Character

Click **"Add Character"** to save your character.

**What happens:**
- The character is validated (backstory length, ability power levels, etc.)
- A success message appears
- The character appears in the table on the left

### Common Validation Errors

**❌ "Backstory too short"** - Add more detail (aim for 100+ characters)
**❌ "Power level must be between 1 and 10"** - Adjust the power level
**❌ "Cannot add duplicate ability"** - Each ability name must be unique per character

### Editing a Character

1. Select the character in the table
2. Modify the form fields
3. Click **"Update Character"**

**Note:** The version number automatically increments when you update.

### Deleting a Character

1. Select the character in the table
2. Click **"Delete Character"**
3. Confirm the deletion

**⚠️ Warning:** This cannot be undone. Make sure you have a backup if needed.

---

## Working with Events

### What is an Event?

Events are story beats - quests, battles, discoveries, or any significant occurrence in your world.

**Example Events:**
- "The Great Reforging" - Characters forge a legendary weapon
- "Discovery of Lost Archives" - Characters find ancient knowledge
- "Shadowmere Invasion" - An army attacks the kingdom

### Creating an Event

**Note:** As of this version, the Events tab is still under development. You can create events via JSON export/import or wait for the GUI update.

**For now:**
1. Create worlds and characters in the GUI
2. Export your lore as JSON
3. Edit the JSON to add events (see [GUI_IMPLEMENTATION_SUMMARY.md](gui/GUI_IMPLEMENTATION_SUMMARY.md#data-format))
4. Import the updated JSON back into the GUI

**Events GUI coming soon!** Watch the GitHub repository for updates.

---

## Data Management

### Saving Your Work

**Save:** Updates the current file
1. Click **"Save"** in the bottom toolbar
2. Changes are saved to the currently open file

**Save As:** Creates a new file
1. Click **"Save As"** in the bottom toolbar
2. Choose a location and filename
3. Click **"Save"**

**Recommended filename:** `my_world.json` or `campaign_name.json`

### Loading Existing Lore

1. Click **"Load"** in the bottom toolbar
2. Navigate to your `.json` lore file
3. Click **"Open"**

The GUI will display all worlds, characters, and events from the file.

### Starting Fresh

1. Click **"New"** in the bottom toolbar
2. Confirm you want to clear all data
3. Start creating from scratch

**⚠️ Warning:** This clears all current data. Make sure to save first!

### Export and Import

**Export:** Save your lore as a JSON file
- **Format:** Plain text, human-readable
- **Use case:** Backup, sharing, version control

**Import:** Load a JSON lore file
- **Use case:** Restore backup, load team contributions

### Version Control with Git (Recommended)

For serious projects, use Git to track changes:

```bash
# Initialize a Git repository
git init

# Add your lore file
git add my_world.json

# Commit changes
git commit -m "Initial world creation: Crystal Peaks and Zephyr Stormrider"
```

**Benefits:**
- See complete history of changes
- Compare different versions
- Revert mistakes
- Collaborate with teammates

**For Git workflows, see [Common Workflows → Reviewing Team Contributions](#workflow-3-reviewing-team-contributions)**

---

## Common Workflows

### Workflow 1: Creating a New Game World from Scratch

**Use this when:** You're building a brand new game or story universe.

**Steps:**

1. **Launch the GUI** - See [Quick Start](#quick-start)
2. **Create your first world:**
   - Go to the "Worlds" tab
   - Enter a name and description
   - Click "Add World"
3. **Add characters:**
   - Go to the "Characters" tab
   - Select your world from the dropdown
   - Create characters with backstories and abilities
4. **Define events:**
   - (Currently via JSON - see [Working with Events](#working-with-events))
   - Create story events and quests
5. **Save your work:**
   - Click "Save As"
   - Name your file (e.g., `my_world.json`)
6. **Version control (recommended):**
   ```bash
   git init
   git add my_world.json
   git commit -m "Initial world creation"
   ```

**Time estimate:** 30-60 minutes for a basic world with 2-3 characters

---

### Workflow 2: Expanding an Existing Story

**Use this when:** You're adding new content to an established world.

**Steps:**

1. **Load your lore file:**
   - Click "Load" in the GUI
   - Select your existing `.json` file
2. **Review existing content:**
   - Check worlds, characters, and events
   - Note which characters need new abilities
   - Identify story gaps
3. **Add new characters:**
   - Create new characters fitting the world's theme
   - Write detailed backstories linking to existing characters
4. **Add new events:**
   - (Currently via JSON)
   - Create story events involving existing characters
   - Ensure events follow logical progression
5. **Update existing content:**
   - Modify character backstories as the story evolves
   - Add abilities when characters level up
6. **Save and commit:**
   - Click "Save" to update the file
   - Commit changes to Git with descriptive message

**Time estimate:** 20-40 minutes per major story addition

---

### Workflow 3: Reviewing Team Contributions

**Use this when:** You're managing a team and need to review proposed lore changes.

**Steps:**

1. **Set up Git repository:**
   - Initialize Git for your lore files
   - Create a GitHub/GitLab repository
   - Give your team access
2. **Establish workflow:**
   - Each team member creates a branch for their changes
   - They submit Pull Requests (PRs) when ready for review
3. **Review PRs:**
   - Load their branch's lore file in the GUI
   - Check for consistency with existing lore
   - Verify all validation rules pass
   - Test progression mechanics if relevant
4. **Merge or request changes:**
   - If good: Merge the PR
   - If issues: Request changes with specific feedback
5. **Update main lore:**
   - Pull latest changes to your local repository
   - Verify in GUI
   - Tag release (e.g., `v1.2.0`) for version tracking

**Time estimate:** 10-20 minutes per PR review

---

### Workflow 4: Testing Game Progression Systems

**Use this when:** You're a QA tester verifying character advancement or gacha mechanics.

**Steps:**

1. **Load test lore:**
   - Create or load lore with characters and progression rules
2. **Use the progression simulator:**
   - See [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md)
   - Simulate experience gain and level ups
   - Verify stat increases follow game rules
3. **Test gacha mechanics:**
   - Set up test banners with known drop rates
   - Run simulations to verify pity systems
   - Check that rates sum to 100%
4. **Document issues:**
   - Take screenshots of simulation results
   - Note any violations of game rules
   - Create bug reports with specific test cases

**Time estimate:** 30-60 minutes per progression system test

---

## Troubleshooting

### Common Problems

#### Problem: GUI Won't Start

**Symptoms:** Nothing happens when you run `python run_gui.py`, or you see an error.

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   ```
   Must be Python 3.11 or higher.

2. **Make sure PyQt6 is installed:**
   ```bash
   pip list | grep PyQt6
   ```
   If not installed, run: `pip install PyQt6`

3. **Check virtual environment is activated:**
   - Terminal should show `(venv)` at the start
   - Activate if needed:
     - macOS/Linux: `source venv/bin/activate`
     - Windows: `venv\Scripts\activate.bat`

4. **Check for error messages:**
   - Read the console output carefully
   - Error messages usually indicate the problem

**Still stuck?** See [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md#troubleshooting) for more details.

---

#### Problem: "Backstory too short" Error

**Symptoms:** You try to create a character and get this error.

**Solution:**

Your backstory needs at least 100 characters.

**Quick fix:**
- Add 1-2 more sentences about the character
- Describe their motivations and goals
- Include a key life event

**Example of a good backstory (200+ characters):**
> Born in the slums of Ardent City, Lyra learned to fight before she learned to read. After witnessing her family's murder by the city guard, she vowed to overthrow the corrupt ruling council. Now she leads the underground resistance, using her street smarts and dual daggers to strike from the shadows.

---

#### Problem: "Name already exists" Error

**Symptoms:** You try to create a world and get this error.

**Solution:**

Each world must have a unique name.

**Option 1:** Choose a different name
- "Crystal Peaks" → "Crystal Mountains"

**Option 2:** Edit the existing world instead of creating a new one
- Select the existing world in the table
- Modify the description
- Click "Update World"

---

#### Problem: "Power level must be between 1 and 10" Error

**Symptoms:** You try to add an ability and get this error.

**Solution:**

Ability power levels are constrained to 1-10.

**Adjust the power level in the ability dialog:**
- **1-3**: Weak abilities
- **4-6**: Normal abilities
- **7-8**: Powerful abilities
- **9**: Legendary abilities
- **10**: Godlike abilities

**Most abilities should be 3-7.** Save 8+ for rare, special abilities.

---

#### Problem: "Cannot add duplicate ability" Error

**Symptoms:** You try to add an ability with a name that already exists on the character.

**Solution:**

Each character can only have one ability with a given name.

**Option 1:** Choose a different name
- "Fireball" → "Inferno" or "Flame Burst"

**Option 2:** Remove the existing ability first
- Click the "Remove" button next to the duplicate ability
- Add the new ability

**Option 3:** Update the existing ability
- Select the ability in the list
- Modify the description and power level
- Click "Update"

---

#### Problem: Can't Save File

**Symptoms:** You click "Save" and nothing happens, or you get a permission error.

**Solutions:**

1. **Check write permissions:**
   - Make sure you have permission to write to the directory
   - On Windows, try running as Administrator

2. **Check file is not locked:**
   - Close any other programs that might be using the file
   - Check if the file is open in another editor

3. **Ensure file extension is .json:**
   - The file must end in `.json`
   - Example: `my_world.json` (not `my_world.txt`)

---

#### Problem: Lost My Lore File

**Symptoms:** You can't find your lore file, or it was accidentally deleted.

**Solutions:**

**If you used Git:**
```bash
git log  # See history
git checkout <commit-hash>  # Restore from history
```

**If you have backups:**
- Check for `.bak` or `_v2.json` files in your directory
- Check cloud storage (Dropbox, Google Drive)

**If no backups:**
Unfortunately, the file may be lost.

**Prevention:**
- Use Git from day one (see [Version Control](#version-control-with-git-recommended))
- Regular "Save As" backups
- Consider a database with automatic backups

---

## Uninstallation

### When to Uninstall

- You're finished with the project
- You need to reinstall due to corruption
- You're switching to a different lore management system

### Backup Before Uninstalling

**Important:** Export all lore data before uninstalling!

1. Open the GUI
2. Load your lore file
3. Click "Save As" and save to a safe location (e.g., Desktop, external drive)
4. Repeat for all lore files

### Uninstallation Steps

**Step 1: Deactivate virtual environment**
```bash
deactivate
```

**Step 2: Remove virtual environment**
```bash
# On macOS/Linux
rm -rf venv

# On Windows
rmdir /s venv
```

**Step 3: Remove project directory**
```bash
# On macOS/Linux
rm -rf /path/to/loreSystem

# On Windows
rmdir /s /q C:\path\to\loreSystem
```

**Step 4: Remove database (if you used PostgreSQL)**
```bash
# Connect to PostgreSQL and drop the database
psql -U postgres
DROP DATABASE mythweave;
\q
```

**Step 5: Remove Elasticsearch indices (if you used Elasticsearch)**
```bash
curl -XDELETE 'localhost:9200/lore_*'
```

---

## Additional Resources

### Documentation

- [README.md](README.md) - Documentation index and overview
- [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md) - Detailed GUI walkthrough
- [FAQ.md](FAQ.md) - Frequently asked questions
- [GLOSSARY.md](GLOSSARY.md) - Terminology explained

### Feature Guides

- [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md) - Testing character advancement
- [MUSIC_SYSTEM.md](features/MUSIC_SYSTEM.md) - Music and audio integration

### Technical Documentation

- [PROJECT_SUMMARY.md](design/PROJECT_SUMMARY.md) - Architecture and design
- [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) - Domain rules and validation

### Support

- **GitHub Issues**: Report bugs and request features
- **Discord**: Join our community for real-time help
- **Documentation**: Browse all docs in [docs/README.md](README.md)

---

## Appendix: Quick Reference

### Validation Rules at a Glance

| Entity | Field | Requirement |
|--------|-------|-------------|
| **World** | Name | 3-100 characters, unique |
| | Description | 10-5000 characters |
| **Character** | Name | 3-100 characters |
| | Backstory | ≥100 characters |
| | Status | `active` or `inactive` |
| | Ability power level | 1-10 |
| **Ability** | Name | Unique per character |
| | Power level | 1-10 |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Tab | Move to next form field |
| Shift+Tab | Move to previous form field |
| Enter | Submit form |

**Future shortcuts:** Ctrl+S (save), Ctrl+O (open), Ctrl+N (new)

---

**Happy lore building!** 📚✨

If you need help, check the [FAQ](FAQ.md) or [Glossary](GLOSSARY.md).
