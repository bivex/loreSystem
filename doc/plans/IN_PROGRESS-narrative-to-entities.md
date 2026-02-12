# PLAN-0001: Narrative Chapter to Entities Generation (3 Test Agents)

Loom-based agent orchestration for converting narrative chapters into loreSystem entities using 30 specialized agent professions.

<!-- loom METADATA -->
```yaml
loom:
  version: 1
  sandbox:
    enabled: true
    auto_allow: true
    excluded_commands: []
    filesystem:
      deny_read:
        - "~/.ssh/**"
        - "~/.aws/**"
        - "~/.gnupg/**"
      deny_write:
        - "agents/skills/**"
        - ".work/stages/**"
        - ".work/sessions/**"
        - ".git/**"
      allow_write:
        - "entities/**"
        - "scripts/**"
        - "doc/plans/**"
        - "src/**"
      allow_read:
        - ".work/config.toml"
        - ".work/signals/**"
        - ".work/handoffs/**"
        - ".claude/CLAUDE.md"
        - "agents/skills/**"
    network:
      allowed_domains: ["github.com", "crates.io", "raw.githubusercontent.com"]
      additional_domains: []
      allow_local_binding: false
      allow_unix_sockets: false
  stages:
    # ===== 3 ACTIVE AGENTS FOR TESTING =====
    - id: narrative-specialist
      name: Narrative Specialist (8 entities)
      description: Create Story, Chapter, Act, Episode, Prologue, Epilogue, PlotBranch, BranchPoint
      working_dir: "."
      stage_type: standard
      dependencies: []
      execution_mode: team
      context_budget: 70
      files:
        - "agents/skills/narrative-specialist.md"
        - "src/domain/story/*.py"
      truths:
        - "jq '.story | length > 0' entities/narrative.json"
        - "jq '.chapter | length > 0' entities/narrative.json"
      artifacts:
        - "entities/narrative.json"
      wiring:
        - source: "entities/narrative.json"
          pattern: "story_id"
          description: Narrative entities linked to chapter

    - id: character-architect
      name: Character Architect (7 entities)
      description: Create Character, CharacterEvolution, CharacterProfileEntry, CharacterRelationship, CharacterVariant, VoiceActor, MotionCapture
      working_dir: "."
      stage_type: standard
      dependencies: []
      execution_mode: team
      context_budget: 70
      files:
        - "agents/skills/character-architect.md"
        - "src/domain/entities/character*.py"
      truths:
        - "jq '.character | length > 0' entities/character.json"
      artifacts:
        - "entities/character.json"
      wiring:
        - source: "entities/character.json"
          pattern: "character_id"
          description: Character entities generated

    - id: quest-designer
      name: Quest Designer (9 entities)
      description: Create Quest, QuestChain, QuestNode, QuestGiver, QuestObjective, QuestPrerequisite, QuestRewardTier, QuestTracker, MoralChoice
      working_dir: "."
      stage_type: standard
      dependencies: []
      execution_mode: team
      context_budget: 70
      files:
        - "agents/skills/quest-designer.md"
        - "src/domain/entities/quest*.py"
      truths:
        - "jq '.quest | length > 0' entities/quest.json"
      artifacts:
        - "entities/quest.json"

    # ===== REMAINING 27 AGENTS (DISABLED FOR TESTING) =====
    # Uncomment when ready for full 30-agent run
    #
    # - id: progression-engineer
    #   name: Progression Engineer (10 entities)
    #   description: Create Skill, Perk, Trait, Attribute, Experience, LevelUp, TalentTree, Mastery, ProgressionEvent, ProgressionState
    #   working_dir: "."
    #   stage_type: standard
    #   dependencies: []
    #   execution_mode: team
    #   files:
    #     - "agents/skills/progression-engineer.md"
    #     - "src/domain/entities/*.py"
    #   truths:
    #     - "jq '.skill | length > 0' entities/progression.json"
    #   artifacts:
    #     - "entities/progression.json"
    #
    # ... (other 26 agents would be commented here)
    #

    # ===== VALIDATION =====
    - id: validate-entities
      name: Validate All Entities
      description: Validate all generated entity JSON files against loreSystem domain model and schema
      working_dir: "."
      stage_type: integration-verify
      dependencies:
        - "narrative-specialist"
        - "character-architect"
        - "quest-designer"
      context_budget: 70
      acceptance:
        - "python scripts/validate_entities.py entities/ --strict"
      truths:
        - "python scripts/validate_schema.py entities/ --all-files"
      artifacts:
        - "validation_report.json"
        - "validation_summary.json"

    # ===== PERSIST =====
    - id: persist-to-sqlite
      name: Persist Entities to SQLite
      description: Insert all validated entities into loreSystem database
      working_dir: "."
      stage_type: standard
      dependencies: ["validate-entities"]
      context_budget: 70
      acceptance:
        - "python scripts/verify_sqlite_inserts.py lore_system.db entities/"
      truths:
        - "sqlite3 lore_system.db 'SELECT COUNT(*) FROM story > 0'"
        - "sqlite3 lore_system.db 'SELECT COUNT(*) FROM character > 0'"
        - "sqlite3 lore_system.db 'SELECT COUNT(*) FROM quest > 0'"
      artifacts:
        - "lore_system.db"
        - "insert_log.json"
        - "insert_summary.json"
```
<!-- END loom METADATA -->

## Entity Coverage

| Agent Profession | Entities Covered | Count |
|------------------|------------------|-------|
| Narrative Specialist | story, chapter, act, episode, prologue, epilogue, plot_branch, branch_point | 8 |
| Character Architect | character, character_evolution, character_profile_entry, character_relationship, character_variant, voice_actor, motion_capture | 7 |
| Quest Designer | quest, quest_chain, quest_node, quest_giver, quest_objective, quest_prerequisite, quest_reward_tier, quest_tracker, moral_choice | 9 |
| **ACTIVE (3)** | **Test agents** | **24** |
| Progression Engineer | skill, perk, trait, attribute, experience, level_up, talent_tree, mastery, progression_event, progression_state | 10 |
| ... | ... | ... |
| **DISABLED (27)** | **Remaining agents** | **271** |
| **TOTAL** | **All loreSystem entities** | **295** |

## Usage

### macOS (Current System)
```bash
cd /Volumes/External/Code/loreSystem
rm -rf .work && loom init doc/plans/IN_PROGRESS-narrative-to-entities.md
loom run --max-parallel 3
```

### Linux (with X11)
```bash
cd /root/clawd
rm -rf .work && loom init doc/plans/narrative-to-entities.md
export TERMINAL=xterm
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99
loom run --max-parallel 3
```

## macOS Worktree Path Resolution

**CRITICAL for macOS loom worktrees:**

When working in a loom git worktree, agents are in an isolated environment at `.worktrees/<stage-id>/`.

**Path Resolution Rules:**
1. **Always use absolute paths** when referencing main repo: `/Volumes/External/Code/loreSystem/`
2. **`.work/` is a SYMLINK** to shared state - use it for accessing shared resources
3. **Never use `../`** - use absolute paths instead
4. **`working_dir`** is relative to worktree root, not main repo

**Correct path patterns:**
- Main repo files: `/Volumes/External/Code/loreSystem/agents/skills/...`
- Shared state: `.work/config.toml`, `.work/signals/...`
- Worktree files: Use paths relative to `working_dir`

**Example:**
- If `working_dir: "."`, you're at `.worktrees/<stage-id>/`
- To read skill files: use absolute path `/Volumes/External/Code/loreSystem/agents/skills/...`
- To access shared state: `.work/config.toml` (symlink works from worktree)

## Output Structure

```
entities/
├── narrative.json          # 8 entities
├── character.json          # 7 entities
├── quest.json              # 9 entities
└── validation_summary.json # Combined validation
```

## Next Steps

To enable all 30 agents, uncomment the remaining agent stages in the YAML metadata.
