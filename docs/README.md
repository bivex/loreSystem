# MythWeave Chronicles Documentation

**A lore management platform for game developers and storytellers.**

---

## 📚 What is MythWeave?

MythWeave Chronicles is a **structured database for your game's world, characters, events, and storylines.** Whether you're building an RPG, writing a novel, or managing a collaborative world-building project, MythWeave helps you:

✅ **Organize lore** - Keep worlds, characters, and events in one place
✅ **Enforce rules** - Automatic validation prevents broken game mechanics
✅ **Track changes** - Version history and rollback capability
✅ **Collaborate** - Work with teams using Git and database backends
✅ **Validate systems** - Test progression mechanics and gacha rules

---

## 🎯 Who Should Use MythWeave?

### Game Designers
Create and manage consistent game worlds, track character progression, and ensure story continuity.

### Writers
Develop rich character backstories, maintain narrative consistency across multiple storylines, and track character abilities.

### QA Testers
Verify game content matches lore specifications, test progression systems, and validate character abilities.

### Project Managers
Track lore development progress, manage content across teams, and review proposed changes.

---

## 🚀 Quick Start

### New to MythWeave? Start Here:

1. **Read the [User Guide](USER_GUIDE.md)** - Installation, usage, troubleshooting
2. **Follow the [GUI Quick Start](gui/QUICKSTART_GUI.md)** - 5-minute walkthrough
3. **Check the [FAQ](FAQ.md)** - Common questions answered
4. **Use [Quick Reference Cards](QUICK_REFERENCE.md)** - Cheat sheets for common tasks

### Already Using MythWeave?

- **Need help?** Check [FAQ](FAQ.md) or [Glossary](GLOSSARY.md)
- **Want to upgrade?** See [Advanced Configuration](USER_GUIDE.md#advanced-configuration)
- **Building a game?** Read [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md)
- **Testing progression?** See [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md)

---

## 📖 Documentation by Topic

### Getting Started

| Document | Description | Audience |
|----------|-------------|----------|
| [USER_GUIDE.md](USER_GUIDE.md) | Complete guide: install, use, troubleshoot | All users |
| [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md) | 5-minute walkthrough for the GUI | New users |
| [WINDOWS_SETUP.md](platform/WINDOWS_SETUP.md) | Windows-specific setup instructions | Windows users |
| [FAQ.md](FAQ.md) | Frequently asked questions | All users |
| [GLOSSARY.md](GLOSSARY.md) | Terminology and concepts explained | All users |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | One-page cheat sheets | All users |

### Core Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [Validation Rules](validation/VALIDATION_QUICK_REFERENCE.md) | All domain rules and validation logic | Designers, QA |
| [Player Guarantees](validation/PLAYER_GUARANTEES_RU.md) | What players can expect | Designers, QA |
| [Database Verification](validation/DATABASE_DOMAIN_VERIFICATION.md) | SQL constraints and rules | Developers |
| [Edge Cases](validation/DOMAIN_EDGE_CASES_RU.md) | Testing edge cases and boundaries | Developers, QA |

### Features

| Document | Description | Audience |
|----------|-------------|----------|
| [Progression Simulator](features/PROGRESSION_SIMULATOR_README.md) | Testing character advancement | Designers, QA |
| [Music System](features/MUSIC_SYSTEM.md) | Audio and music integration | Developers |
| [Mutation Testing](features/MUTATION_TESTING_README.md) | Testing lore evolution | Developers |

### Architecture & Design

| Document | Description | Audience |
|----------|-------------|----------|
| [Project Summary](design/PROJECT_SUMMARY.md) | Overview of the system | All users |
| [Implementation Guide](design/IMPLEMENTATION_GUIDE.md) | How to build and extend | Developers |
| [Game Design](design/GAME_DESIGN.md) | Game mechanics and rules | Designers |
| [Structure](design/STRUCTURE.md) | Project structure and organization | Developers |
| [ADRs](design/adr/) | Architectural Decision Records | Developers |

---

## 🗺️ Navigation Guide

### I Want To...

**Get started with MythWeave**
→ [USER_GUIDE.md](USER_GUIDE.md) → Start with "Quick Start" section

**Launch the GUI and create my first world**
→ [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md) → Follow step-by-step tutorial

**Set up on Windows**
→ [WINDOWS_SETUP.md](platform/WINDOWS_SETUP.md) → Use the one-click launcher

**Understand validation rules**
→ [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) → See all business rules

**Test character progression**
→ [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md) → Run simulations

**Find the meaning of a technical term**
→ [GLOSSARY.md](GLOSSARY.md) → Look up the term alphabetically

**Answer a common question**
→ [FAQ.md](FAQ.md) → Search or browse by category

**Get a quick refresher on a task**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → Print the relevant card

**Understand the system architecture**
→ [PROJECT_SUMMARY.md](design/PROJECT_SUMMARY.md) → Read the overview

**Troubleshoot a problem**
→ [USER_GUIDE.md](USER_GUIDE.md#troubleshooting) → Find your error in the list

---

## 🎓 Documentation by Audience

### For Non-Technical Users (Writers, Designers, QA)

**Start here:**
1. [USER_GUIDE.md](USER_GUIDE.md) - Main guide, easy to follow
2. [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md) - Hands-on tutorial
3. [FAQ.md](FAQ.md) - Answers to common questions

**When you're ready:**
4. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cheat sheets for efficiency
5. [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) - Rules your lore must follow

---

### For Technical Users (Developers, DevOps)

**Start here:**
1. [PROJECT_SUMMARY.md](design/PROJECT_SUMMARY.md) - System overview
2. [STRUCTURE.md](design/STRUCTURE.md) - Code organization
3. [IMPLEMENTATION_GUIDE.md](design/IMPLEMENTATION_GUIDE.md) - How to build

**When you're ready:**
4. [GUI_IMPLEMENTATION_SUMMARY.md](gui/GUI_IMPLEMENTATION_SUMMARY.md) - GUI architecture
5. [DATABASE_DOMAIN_VERIFICATION.md](validation/DATABASE_DOMAIN_VERIFICATION.md) - SQL schema
6. [ADRs](design/adr/) - Architectural decisions

---

### For Game Designers

**Start here:**
1. [USER_GUIDE.md](USER_GUIDE.md) - Learn to use the system
2. [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) - Rules and constraints
3. [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md) - Test progression

**When you're ready:**
4. [GAME_DESIGN.md](design/GAME_DESIGN.md) - Game mechanics
5. [PLAYER_GUARANTEES_RU.md](validation/PLAYER_GUARANTEES_RU.md) - Player-facing rules

---

### For QA Testers

**Start here:**
1. [USER_GUIDE.md](USER_GUIDE.md) - Learn the system
2. [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md) - Rules to verify
3. [DOMAIN_EDGE_CASES_RU.md](validation/DOMAIN_EDGE_CASES_RU.md) - Test edge cases

**When you're ready:**
4. [PROGRESSION_SIMULATOR_README.md](features/PROGRESSION_SIMULATOR_README.md) - Test progression
5. [MUTATION_TESTING_README.md](features/MUTATION_TESTING_README.md) - Test lore changes

---

## 🔍 Search and Browse

### By Topic

- **Installation:** [USER_GUIDE.md](USER_GUIDE.md#installation-and-configuration), [WINDOWS_SETUP.md](platform/WINDOWS_SETUP.md)
- **Creating Worlds:** [USER_GUIDE.md](USER_GUIDE.md#creating-your-first-world), [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md#create-your-first-world)
- **Managing Characters:** [USER_GUIDE.md](USER_GUIDE.md#managing-characters), [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md#create-your-first-character)
- **Validation Rules:** [VALIDATION_QUICK_REFERENCE.md](validation/VALIDATION_QUICK_REFERENCE.md), [USER_GUIDE.md#appendix-quick-reference)
- **Troubleshooting:** [USER_GUIDE.md](USER_GUIDE.md#troubleshooting), [QUICKSTART_GUI.md](gui/QUICKSTART_GUI.md#troubleshooting), [FAQ.md](FAQ.md#troubleshooting)

### By Difficulty

| Level | Documents |
|-------|-----------|
| **Beginner** | USER_GUIDE.md, QUICKSTART_GUI.md, FAQ.md, QUICK_REFERENCE.md |
| **Intermediate** | VALIDATION_QUICK_REFERENCE.md, PLAYER_GUARANTEES_RU.md, PROGRESSION_SIMULATOR_README.md |
| **Advanced** | PROJECT_SUMMARY.md, IMPLEMENTATION_GUIDE.md, DATABASE_DOMAIN_VERIFICATION.md, ADRs |

### By File Type

| Type | Files |
|------|-------|
| **User Guides** | USER_GUIDE.md, QUICKSTART_GUI.md, WINDOWS_SETUP.md |
| **Reference** | FAQ.md, GLOSSARY.md, QUICK_REFERENCE.md, VALIDATION_QUICK_REFERENCE.md |
| **Features** | PROGRESSION_SIMULATOR_README.md, MUSIC_SYSTEM.md, MUTATION_TESTING_README.md |
| **Architecture** | PROJECT_SUMMARY.md, IMPLEMENTATION_GUIDE.md, STRUCTURE.md |
| **Validation** | VALIDATION_QUICK_REFERENCE.md, DATABASE_DOMAIN_VERIFICATION.md, DOMAIN_EDGE_CASES_RU.md |

---

## 💡 Documentation Structure

```
docs/
├── README.md (this file) - Main index and navigation
├── USER_GUIDE.md - Complete user guide
├── FAQ.md - Frequently asked questions
├── GLOSSARY.md - Terminology explained
├── QUICK_REFERENCE.md - One-page cheat sheets
│
├── gui/ - GUI documentation
│   ├── QUICKSTART_GUI.md - GUI walkthrough
│   └── GUI_IMPLEMENTATION_SUMMARY.md - Technical details
│
├── features/ - Feature-specific guides
│   ├── PROGRESSION_SIMULATOR_README.md - Progression testing
│   ├── MUSIC_SYSTEM.md - Audio integration
│   └── MUTATION_TESTING_README.md - Lore evolution testing
│
├── validation/ - Domain validation and rules
│   ├── VALIDATION_QUICK_REFERENCE.md - All business rules
│   ├── PLAYER_GUARANTEES_RU.md - Player-facing guarantees
│   ├── DATABASE_DOMAIN_VERIFICATION.md - SQL constraints
│   └── DOMAIN_EDGE_CASES_RU.md - Edge case testing
│
├── design/ - Architecture and design
│   ├── PROJECT_SUMMARY.md - System overview
│   ├── IMPLEMENTATION_GUIDE.md - How to build
│   ├── GAME_DESIGN.md - Game mechanics
│   ├── STRUCTURE.md - Code organization
│   └── adr/ - Architectural Decision Records
│
└── platform/ - Platform-specific setup
    └── WINDOWS_SETUP.md - Windows installation
```

---

## 🤝 Contributing to Documentation

Found a typo? Want to improve an explanation? We welcome documentation contributions!

**How to contribute:**
1. Fork the repository
2. Make your changes
3. Submit a Pull Request with a clear description

**What we're looking for:**
- Fixes to unclear sections
- Additional examples
- Screenshots and diagrams
- Translations to other languages
- Simplified explanations for non-technical users

---

## 📞 Getting Help

### Self-Service

- **Search**: Use Ctrl+F (or Cmd+F) to search within documents
- **FAQ**: Check [FAQ.md](FAQ.md) for common questions
- **Glossary**: Look up terms in [GLOSSARY.md](GLOSSARY.md)

### Community

- **GitHub Issues**: Report bugs and request features
- **Discord**: Join our community for real-time help (link in main project README)
- **Discussions**: Use GitHub Discussions for questions and ideas

### Documentation Issues

If you find documentation issues:
1. Check if there's already a GitHub issue
2. If not, create an issue with:
   - Which document has the issue
   - What's wrong or unclear
   - Suggested improvement (if you have one)

---

## 🔄 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| USER_GUIDE.md | ✅ Updated (v2.0) | 2026-01-29 |
| QUICKSTART_GUI.md | ✅ Current | 2026-01-23 |
| FAQ.md | ✅ New | 2026-01-29 |
| GLOSSARY.md | ✅ New | 2026-01-29 |
| QUICK_REFERENCE.md | ✅ New | 2026-01-29 |
| VALIDATION_QUICK_REFERENCE.md | ✅ Current | 2026-01-18 |
| PROGRESSION_SIMULATOR_README.md | ✅ Current | 2026-01-29 |
| PROJECT_SUMMARY.md | ✅ Current | 2026-01-29 |

---

## 📌 Key Concepts

Before diving in, understand these core concepts:

### Lore Management
MythWeave is designed to **manage game lore** - worlds, characters, events, and the rules that connect them.

### Domain-Driven Design
The system is built around the **domain of game lore**, not around databases or user interfaces. This means the software matches how you think about game design.

### Validation-First
All lore is validated against **business rules** before saving. This prevents broken game mechanics and inconsistent stories.

### Version Control
Track every change with **Git integration**. Revert mistakes, compare versions, and collaborate with your team.

---

**Ready to start?** Jump to [USER_GUIDE.md](USER_GUIDE.md) and begin your lore-building journey! 📚✨

---

*This documentation index last updated: January 29, 2026*
