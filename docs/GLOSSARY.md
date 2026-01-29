# MythWeave Documentation Glossary

This glossary explains technical terms and concepts used throughout the MythWeave documentation. If you encounter a term you don't understand, this is the place to look.

---

## Technical Terms (For Non-Technical Users)

### Aggregate
**What it means:** A group of related items that must stay consistent together.

**Example:** A "World" is an aggregate containing characters, events, and abilities. If you delete the world, everything in it is deleted too. You can't have a character without a world.

**Why it matters:** Ensures your lore stays consistent - related items are managed as a unit.

---

### Domain
**What it means:** The subject matter or problem area the software solves.

**Example:** The MythWeave "domain" is game lore management - worlds, characters, events, progression rules, and all the things that make up a game's story universe.

**Why it matters:** Understanding the domain helps you use the software for its intended purpose - managing game lore, not anything else.

---

### Entity
**What it means:** An object with a unique identity that persists over time.

**Example:** Each character is an entity. Even if two characters are named "John Smith," they're different entities with different IDs. If you rename a character from "John" to "Johnathan," it's still the same entity.

**Why it matters:** Entities help the system track items uniquely, preventing confusion and enabling proper versioning and history tracking.

---

### Invariant
**What it means:** A rule that must always be true - the system will never allow it to be broken.

**Example:** "Character backstories must be at least 100 characters" is an invariant. No matter what you do, the system will never save a character with a shorter backstory.

**Why it matters:** Invariants keep your data consistent and prevent invalid states that could break your game or story.

---

### Repository
**What it means:** A storage system that saves and retrieves data.

**Example:** Currently, MythWeave uses JSON files as a repository. The system saves your lore to JSON files and loads it back when you open the GUI. In the future, it could use a database as the repository.

**Why it matters:** You can change how data is stored (from JSON to database) without changing how you use the GUI. The repository is hidden behind the scenes.

---

### Value Object
**What it means:** An object defined by its attributes, not its identity.

**Example:** "Power Level 7" is a value object. Two characters both having power level 7 means they have equal power - they're not "different" power levels.

**Why it matters:** Value objects have built-in validation (e.g., power level must be 1-10) and ensure consistency across the system.

---

### Hexagonal Architecture
**What it means:** A design pattern that separates the core business logic from external systems (databases, user interfaces, APIs).

**Why it matters:** Makes the software flexible - you can swap databases, add new interfaces (CLI, web API), or change how data is stored without breaking the core logic.

**Analogy:** Think of it like a car - the engine (core logic) is the same, but you can change the tires, seats, or steering wheel without redesigning the engine.

---

### SOLID Principles
**What it means:** A set of five design principles that make software maintainable, flexible, and understandable:
- **S**ingle Responsibility - Each class does one thing
- **O**pen/Closed - Open for extension, closed for modification
- **L**iskov Substitution - Subtypes must be substitutable
- **I**nterface Segregation - Small, focused interfaces
- **D**ependency Inversion - Depend on abstractions, not concretions

**Why it matters:** Following these principles makes the code easier to maintain and extend. For users, it means more reliable, bug-free software.

---

### Validation
**What it means:** The process of checking that data meets all the rules before it's saved.

**Example:** When you create a character, the system validates:
- Name is 3-100 characters ✓
- Backstory is at least 100 characters ✓
- All abilities have power levels 1-10 ✓

If validation fails, the system shows an error and doesn't save the data.

**Why it matters:** Prevents bad data from entering your lore. Ensures all entries follow the rules.

---

## Game Design Terms

### Gacha
**What it means:** A game mechanic where players randomly collect characters or items (like pulling from a pack of trading cards or buying loot boxes).

**Example:** MythWeave supports tracking gacha banners (pools of characters), drop rates (chances of getting each rarity), and pity systems (guarantees after certain pulls).

**Why it matters:** Common in mobile games (Genshin Impact, Fate/Grand Order). MythWeave helps you design balanced gacha systems.

---

### Pity System
**What it means:** A guarantee that players will get a rare item after a certain number of unsuccessful pulls.

**Example:** "Hard pity at 90 pulls" means if a player pulls 90 times without getting a rare character, they're guaranteed one on the 91st pull.

**Why it matters:** Makes gacha systems fairer - players won't pull forever without getting something good.

---

### 50/50 System
**What it means:** When players pull a rare item in a gacha game, there's a 50% chance it's the featured (special) character. If not, the next rare is guaranteed to be featured.

**Example:** You pull a 5★ character. There's a 50% chance it's the featured character on the banner. If you lose the 50/50, your next 5★ pull is guaranteed to be the featured one.

**Why it means:** Used in games like Genshin Impact. Adds strategy to pulling.

---

### Backstory
**What it means:** A character's history, personality, and motivations written out in narrative form.

**Example:** In MythWeave, backstories must be at least 100 characters to ensure character depth and prevent generic characters.

**Why it matters:** Rich backstories create memorable characters that players care about. They inform how characters act and react in the story.

---

### Power Level
**What it means:** A numeric rating (1-10) representing how strong an ability is in the game.

**Scale:**
- **1-3**: Minor abilities, novice level (e.g., Fire Spark)
- **4-6**: Competent, useful abilities (e.g., Ice Shard)
- **7-8**: Powerful, rare abilities (e.g., Storm Calling)
- **9**: Master-level, legendary abilities (e.g., Dragon Bond)
- **10**: Godlike, world-changing power (e.g., Reality Manipulation)

**Why it matters:** Helps balance characters and create progression systems. Characters start with lower power abilities and unlock stronger ones over time.

---

### Event
**What it means:** Something that happens in your story world - a quest, a battle, a discovery, or any significant occurrence.

**Example:** "The Great Reforging" is an event where characters Aria and Valorian work together to forge a legendary weapon.

**Components:**
- Name (what it's called)
- Description (what happens)
- Participants (which characters are involved)
- Outcome (SUCCESS, FAILURE, or ONGOING)
- Start and end dates (when it happens)

**Why it matters:** Events are the story beats that move your narrative forward. They connect characters and drive the plot.

---

### World
**What it means:** A setting or universe in your story - a continent, a kingdom, a planet, or an entire dimension.

**Example:** "Crystal Peaks" is a world of mountains filled with crystallized magic, dragons, and ancient wizards.

**Components:**
- Name (unique identifier)
- Description (what the world is like)
- Characters (who lives there)
- Events (what happens there)

**Why it matters:** Worlds are the foundation of your lore. Characters and events exist within worlds. You can have multiple worlds (different planets, dimensions, or regions).

---

### Tenant
**What it means:** In multi-user systems, a "tenant" is a separate user or organization with their own isolated data.

**Example:** If multiple game teams use MythWeave, each team is a separate tenant. They can have worlds with the same name (e.g., both could have a "Crystal Mountains") without conflict.

**Why it matters:** In the current version, you're the only tenant, so this doesn't affect you. In multi-user versions, it prevents data conflicts between teams.

---

## Database Terms

### PostgreSQL
**What it means:** A powerful, open-source relational database system.

**Why it matters:** Optional backend for MythWeave when you need:
- Multi-user collaboration (multiple people working simultaneously)
- Advanced search across thousands of entries
- Robust backups and transaction support
- Production-grade reliability

**Comparison:** PostgreSQL is like a professional filing cabinet - organized, searchable, scalable. JSON files are like a notebook - simple, portable, good for individuals.

---

### Elasticsearch
**What it means:** A search engine optimized for full-text search across large amounts of data.

**Why it matters:** Optional component for MythWeave when you need to search across thousands of lore entries quickly. Like Google for your lore.

**Example:** "Find all characters whose backstories mention 'dragon' or 'ancient magic'."

---

### Migration
**What it means:** The process of updating the database schema (structure) as the software evolves.

**Example:** When MythWeave adds a new field to characters, a migration updates existing character data to include that field.

**Why it matters:** Ensures your data is preserved when updating to new versions of MythWeave. You don't lose your lore when the software changes.

---

### Check Constraint
**What it means:** A database rule that validates data before it's saved.

**Example:** The database has a constraint that HP cannot be negative. If you try to save a character with HP = -50, the database rejects it.

**Why it matters:** Database constraints are the final safety net for data quality. Even if validation fails in the GUI, the database won't accept bad data.

---

### Transaction
**What it means:** A group of database operations that succeed or fail together. If one operation fails, all are rolled back.

**Example:** Creating a character involves saving the character data AND their abilities. If saving abilities fails, the character creation is completely undone.

**Why it matters:** Ensures data consistency. You never end up with half-saved or corrupted data.

---

### Schema
**What it means:** The structure of a database - tables, columns, relationships, and constraints.

**Example:** The MythWeave schema defines that characters have a name, backstory, abilities, status, and world_id.

**Why it matters:** The schema ensures all data follows a consistent structure. Like a template for your data.

---

## Version Control Terms

### Git
**What it means:** A version control system that tracks changes to files over time.

**Why it matters:** Allows you to:
- See who changed what, and when
- Compare different versions of your lore
- Revert to previous versions if you make a mistake
- Collaborate with teammates without overwriting each other

**Analogy:** Like "Track Changes" in Microsoft Word, but much more powerful.

---

### Commit
**What it means:** Saving a set of changes in Git.

**Example:** After creating a new character, you might commit the change with a message like "Added Zephyr Stormrider - dragon rider with storm abilities."

**Why it matters:** Each commit is a save point. You can go back to any commit at any time.

---

### Branch
**What it means:** A separate line of development in Git. Each branch can have its own changes.

**Example:** Create a branch called "add-dark-faction" to experiment with new characters without affecting your main lore file. If it doesn't work out, delete the branch. If it does, merge it into the main branch.

**Why it matters:** Allows experimentation without risk. You can try new ideas safely.

---

### Merge
**What it means:** Combining changes from one branch into another.

**Example:** After testing new characters on a branch, merge them into the main branch to include them in the official lore.

**Why it matters:** How team members combine their work. When multiple people work on the same lore, merging brings all changes together.

---

### Pull Request (PR)
**What it means:** A request to merge changes from one branch into another, usually with code review.

**Example:** A team member submits a PR titled "Add 3 new characters for Crystal Peaks world." The lead designer reviews the characters, approves or requests changes, and then the PR is merged.

**Why it matters:** The standard way to review and approve changes in teams. Ensures quality and consistency.

---

### Repository (Git)
**What it means:** A directory where Git tracks your files and their history.

**Example:** Run `git init` in your lore directory to create a Git repository. Now Git tracks all changes to your lore files.

**Why it matters:** Without a Git repository, you can't use version control features like history, branches, or commits.

---

### Remote
**What it means:** A version of your Git repository hosted on a server (like GitHub or GitLab).

**Example:** Push your local repository to a GitHub remote to back it up and share it with teammates.

**Why it matters:** Remotes provide backup and collaboration. If your computer crashes, your lore is safe on the remote.

---

## Software Development Terms

### Value Object (revisited)
**Technical definition:** An immutable object defined by its attributes, compared by value not identity.

**Example in code:**
```python
class PowerLevel:
    def __init__(self, value):
        if value < 1 or value > 10:
            raise ValueError("Power level must be 1-10")
        self.value = value
```

**Why it matters:** Encapsulates validation and ensures all power levels in the system follow the same rules.

---

### DTO (Data Transfer Object)
**What it means:** An object used to transfer data between different parts of the system.

**Example:** When you create a character in the GUI, a DTO carries the character data from the GUI to the application layer.

**Why it matters:** Decouples different layers of the software. The GUI doesn't need to know about the database, and the database doesn't need to know about the GUI.

---

### Use Case
**What it means:** A specific task or operation the system can perform.

**Example:** "CreateCharacterUseCase" is a use case that handles creating a new character, including validation, database storage, and error handling.

**Why it matters:** Organizes functionality around user goals, not technical components.

---

### API (Application Programming Interface)
**What it means:** A set of rules that allow different software systems to communicate.

**Example:** Future versions of MythWeave may have a REST API, allowing game engines to request lore data programmatically.

**Why it matters:** Enables integration with other systems (game engines, websites, mobile apps).

---

### CLI (Command Line Interface)
**What it means:** A text-based interface for controlling software.

**Example:** Future versions of MythWeave may have a CLI, allowing you to create characters via commands like `mythweave create-character --name "Zephyr"`.

**Why it matters:** Useful for automation, scripting, and power users who prefer command lines.

---

## Common Acronyms

| Acronym | Full Term | Meaning |
|---------|-----------|---------|
| CRUD | Create, Read, Update, Delete | Basic database operations |
| API | Application Programming Interface | Rules for system communication |
| CLI | Command Line Interface | Text-based user interface |
| GUI | Graphical User Interface | Visual interface (buttons, menus) |
| JSON | JavaScript Object Notation | Data format for storing lore |
| SQL | Structured Query Language | Language for talking to databases |
| DDD | Domain-Driven Design | Approach to software development |
| SOLID | Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion | Design principles |
| DTO | Data Transfer Object | Object for moving data between layers |
| UUID | Universally Unique Identifier | Unique ID for entities |
| UTC | Coordinated Universal Time | Time zone for timestamps |

---

## MythWeave-Specific Terms

### Ability
**What it means:** A power, skill, or capability a character possesses. Each ability has:
- Name (unique per character)
- Description (what it does)
- Power level (1-10)

**Example:** "Dragon Bond" - Telepathic connection with a dragon. Power Level 9.

---

### Status
**What it means:** Whether a character is currently active in the story.

**Values:**
- **ACTIVE**: Character is alive, present, and participating
- **INACTIVE**: Character is missing, dead, or not currently involved

---

### Version
**What it means:** A number that increments each time a character or world is modified.

**Example:** A world starts at version 1. After editing, it's version 2. Another edit makes it version 3.

**Why it matters:** Helps track changes and enables features like undo/redo in the future.

---

### Tenant ID
**What it means:** A unique identifier for a user or organization in multi-user systems.

**Example:** In a multi-user version, Team A has tenant_id=1 and Team B has tenant_id=2. They can have different rules and their own isolated data.

**Why it matters:** In the current version, you're the only tenant (tenant_id=1), so this doesn't affect you.

---

## Still Confused?

**If you don't find the term you're looking for:**

1. **Check the context** - Read the surrounding paragraph to infer the meaning
2. **Search the documentation** - Use Ctrl+F (or Cmd+F) to find where the term is defined
3. **Ask in the community** - Join our Discord or open a GitHub issue
4. **Start with the basics** - Read [USER_GUIDE.md](USER_GUIDE.md) and [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md) for foundational concepts

---

**Remember:** You don't need to understand all these technical terms to use MythWeave! The GUI handles the technical details for you. This glossary is here for when you encounter a term and want to learn more.

Happy lore building! 📚✨
