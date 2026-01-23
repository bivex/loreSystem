# MythWeave Chronicles User Guide

## Front Matter
**Title:** MythWeave Chronicles User Guide  
**Version:** 1.0  
**Date:** January 23, 2026  
**Authors:** MythWeave Development Team  
**Revision History:**  
- v1.0 (January 23, 2026): Initial structure

## Introduction
- **Purpose:** This guide helps users install, configure, use, and troubleshoot MythWeave Chronicles.
- **Scope:** Covers GUI usage, installation, configuration, troubleshooting, and uninstallation.
- **Audience:** Game designers, world-builders, technical writers, QA, project managers.
- **Referenced Documents:** See docs/README.md for full documentation map.

## Concept of Operations
- MythWeave is a lore management platform for games, supporting world-building, progression, and gacha mechanics via a PyQt6 GUI.
- Typical users: lore managers, designers, QA, writers.
- Main scenarios: create/edit worlds, manage characters/events, simulate progression, export/import data.

## Installation and Configuration
- **System Requirements:** Python 3.11+, PostgreSQL 15+, Elasticsearch 8+, PyQt6 6.6.1+, Windows/macOS/Linux.
- **Quick Start:** See docs/gui/QUICKSTART_GUI.md and docs/platform/WINDOWS_SETUP.md for step-by-step instructions.
- **Configuration:** Edit config/config.yaml for database, search, and git settings.

## Procedures
- **Launching GUI:** See docs/gui/QUICKSTART_GUI.md.
- **Creating Worlds/Characters:** Use GUI tabs; see docs/gui/GUI_IMPLEMENTATION_SUMMARY.md for details.
- **Import/Export Lore:** Use File → Load/Save As in GUI.
- **Simulate Progression:** See docs/features/PROGRESSION_SIMULATOR_README.md.

## Troubleshooting
- **Common Issues:** See docs/gui/GUI_IMPLEMENTATION_SUMMARY.md (Troubleshooting section).
- **Error Messages:** Refer to docs/validation/DOMAIN_EDGE_CASES_RU.md and docs/validation/TASK_COMPLETION_REPORT_RU.md.
- **Support:** Contact via GitHub issues or consult docs/README.md.

## Uninstallation
- **When to Uninstall:** Removing or reinstalling the application.
- **Steps:** Remove venv, project directory, database, and Elasticsearch indices. See docs/platform/WINDOWS_SETUP.md for details.
- **Backup:** Export lore data and config before removal.

## Appendices
- **Glossary, Acronyms, Index:** See docs/README.md and docs/design/STRUCTURE.md for navigation and definitions.

---

For advanced topics, architecture, and validation, see docs/design/ and docs/validation/. For feature-specific guides, see docs/features/.