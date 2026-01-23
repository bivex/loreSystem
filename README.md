# MythWeave Chronicles - Git-Based Lore Management System

## Front Matter

**Title:** MythWeave Chronicles User Guide  
**Version:** 1.0  
**Date:** January 23, 2026  
**Authors:** MythWeave Development Team  
**Revision History:**  
- v1.0 (January 23, 2026): Initial release with comprehensive GUI features and domain modeling.

## Introduction

### Purpose
This document provides user guidance for MythWeave Chronicles, a domain-driven, event-sourced lore management system designed for game developers and world-builders. It enables the creation, management, and evolution of complex game lore using Git version control, SQL databases, and Elasticsearch for search capabilities.

### Scope
This guide covers:
- System overview and capabilities
- Installation and configuration procedures
- Basic usage procedures for the GUI editor
- Troubleshooting common issues
- Uninstallation steps

This guide does not cover:
- Internal architecture details (see IMPLEMENTATION_SUMMARY.md)
- API development (future feature)
- Advanced customization or extension development

### Target Audience
- **Primary:** Game developers, world-builders, and lore managers who need to create and maintain complex game narratives
- **Secondary:** Technical writers, QA testers, and project managers involved in lore management workflows
- **Prerequisites:** Basic familiarity with Python, Git, and database concepts; no advanced programming knowledge required for GUI usage

### Referenced Documents
- [GUI Quick Start Guide](QUICKSTART_GUI.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- [Project Structure](STRUCTURE.md)
- [Domain Analysis](LORE_ANALYSIS_AND_TODO.md)

## Concept of Operations

### System Overview
MythWeave Chronicles operates as a comprehensive lore management platform that integrates:
- **Domain-Driven Design:** Structured entities (Worlds, Characters, Events) with business rules
- **Version Control:** Git-based tracking of all lore changes
- **Search & Persistence:** SQL for transactional data, Elasticsearch for full-text search
- **GUI Editor:** PyQt6-based interface for intuitive lore creation and management

### Typical Usage Scenarios
1. **World-Building:** Create game universes with interconnected characters, events, and locations
2. **Lore Evolution:** Propose and validate improvements to maintain story consistency
3. **Gacha Game Management:** Design banner systems, pity mechanics, and character collections
4. **Progression Simulation:** Test player advancement paths and milestone events
5. **Content Organization:** Manage multimedia assets, templates, and tagged content

### Operating Environment
- **Platforms:** macOS, Windows, Linux
- **Dependencies:** Python 3.11+, PostgreSQL 15+, Elasticsearch 8+
- **Hardware Requirements:** Standard desktop/laptop with 4GB+ RAM
- **Network:** Local operation; optional Git remote for collaboration

## Installation and Configuration

### System Requirements
- **Operating System:** macOS 12+, Windows 10+, Ubuntu 20.04+
- **Python:** Version 3.11 or higher
- **Database:** PostgreSQL 15+ (with JSON support)
- **Search Engine:** Elasticsearch 8+
- **Git:** Version 2.30+ for version control
- **GUI Framework:** PyQt6 6.6.1+

### Installation Steps

#### Quick Setup (Recommended)
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd loreSystem
   ```

2. Run the launcher script:
   ```bash
   ./launch_gui.sh  # macOS/Linux
   # OR
   launch_gui.bat   # Windows
   ```
   The script automatically creates a virtual environment and installs dependencies.

#### Manual Installation
1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # OR
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up PostgreSQL database:
   - Install PostgreSQL 15+
   - Create a database named `mythweave`
   - Run migrations: `alembic upgrade head`

4. Configure Elasticsearch:
   - Install Elasticsearch 8+
   - Initialize indices: `python -m src.infrastructure.persistence.elasticsearch.init_indices`

### Configuration
Create `config/config.yaml` with:
```yaml
database:
  url: postgresql://user:password@localhost/mythweave
elasticsearch:
  url: http://localhost:9200
git:
  repository_path: /path/to/lore/repo
```

### Verification
After installation:
1. Run tests: `pytest tests/`
2. Launch GUI: `python3 run_gui.py`
3. Load sample data from `examples/sample_lore.json`

## Procedures

### Procedure: Launch the GUI Editor
**Purpose:** Start the main application interface.

**Preconditions:**
- Installation completed successfully
- Virtual environment activated (if using manual setup)

**Steps:**
1. Navigate to the project directory
2. Run: `./launch_gui.sh` (macOS/Linux) or `launch_gui.bat` (Windows)
3. Wait for the PyQt6 window to appear

**Result:** MythWeave GUI opens with tabbed interface.

### Procedure: Create a New World
**Purpose:** Set up a new game universe.

**Preconditions:**
- GUI is running
- User has appropriate permissions

**Steps:**
1. Click the "Worlds" tab
2. Click "Add World" button
3. Enter world name and description
4. Click "Save"

**Result:** New world appears in the worlds list.

### Procedure: Load Existing Lore
**Purpose:** Import previously saved lore data.

**Preconditions:**
- JSON lore file exists
- GUI is running

**Steps:**
1. Click "File" → "Load"
2. Navigate to the JSON file (e.g., `examples/sample_lore.json`)
3. Click "Open"

**Result:** Lore data loads into the interface.

### Procedure: Save Current Lore
**Purpose:** Export current lore state to file.

**Preconditions:**
- Lore data exists in the application

**Steps:**
1. Click "File" → "Save As"
2. Choose save location and filename
3. Click "Save"

**Result:** Lore saved as JSON file.

## Troubleshooting

### Common Issues

**Issue:** GUI fails to launch  
**Symptoms:** Error messages about missing PyQt6 or Python version  
**Resolution:**
1. Verify Python version: `python3 --version` (must be 3.11+)
2. Reinstall PyQt6: `pip install "PyQt6>=6.6.1"`
3. Check virtual environment activation

**Issue:** Database connection fails  
**Symptoms:** Errors about PostgreSQL connection  
**Resolution:**
1. Verify PostgreSQL is running
2. Check connection string in `config/config.yaml`
3. Ensure database exists: `createdb mythweave`

**Issue:** Elasticsearch search not working  
**Symptoms:** Search features unavailable  
**Resolution:**
1. Verify Elasticsearch is running on port 9200
2. Reinitialize indices: `python -m src.infrastructure.persistence.elasticsearch.init_indices`

**Issue:** Memory corruption in GUI tests  
**Symptoms:** PyQt6 crashes during testing  
**Resolution:**
1. Run tests in isolated environment
2. Update PyQt6: `pip install --upgrade PyQt6`
3. Use `pytest --tb=short` for better error reporting

### Error Messages
- **"LoreData.from_dict() KeyError"**: Missing required fields in JSON. Validate JSON structure against schema.
- **"PyQt6 memory corruption"**: GUI threading issue. Restart application and avoid concurrent operations.

### Support
For additional help:
- Check [GUI Implementation Summary](docs/GUI_IMPLEMENTATION_SUMMARY.md)
- Review [Mutation Testing Readme](MUTATION_TESTING_README.md)
- Contact development team via GitHub issues

## Information for Uninstallation

### When to Uninstall
Uninstall MythWeave when:
- Removing the application permanently
- Performing clean reinstall
- Freeing up system resources

### Uninstallation Steps
1. Close all running instances of the GUI
2. Remove the virtual environment: `rm -rf venv`
3. Delete the project directory: `rm -rf loreSystem`
4. Drop the database (optional): `dropdb mythweave`
5. Remove Elasticsearch indices (optional): Use Elasticsearch API to delete indices

### Data Backup
Before uninstallation:
1. Export all lore data: Use "Save As" in GUI
2. Backup configuration: Copy `config/config.yaml`
3. Backup database: `pg_dump mythweave > backup.sql`

## Appendices

### Glossary
- **Aggregate:** A consistency boundary for related domain entities
- **Domain-Driven Design:** An approach to software development focused on business domain
- **Event Sourcing:** Storing state changes as a sequence of events
- **Lore:** The collective narrative and world-building elements of a game
- **Tenant:** An isolated instance for different games or campaigns

### Acronyms
- GUI: Graphical User Interface
- SQL: Structured Query Language
- JSON: JavaScript Object Notation
- UTC: Coordinated Universal Time

### Index
- Configuration: See Installation and Configuration
- Database setup: See Installation and Configuration
- GUI launch: See Procedures
- Troubleshooting: See Troubleshooting
- Uninstallation: See Information for Uninstallation
- World creation: See Procedures
