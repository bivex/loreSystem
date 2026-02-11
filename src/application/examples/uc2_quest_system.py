"""
Example: Quest System

This example demonstrates how AAA game dev studios can use
MythWeave's domain model to create and manage complex quest chains
with rewards, prerequisites and progress tracking.
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# Domain entities (in production, these would be imported from src.domain)
# For this example, we'll define minimal stubs
class QuestGiver:
    """Quest giver stub for example."""
    def __init__(self, tenant_id, name, location_id, dialogue):
        self.tenant_id = tenant_id
        self.name = name
        self.location_id = location_id
        self.dialogue = dialogue
        self.id = None

class QuestObjective:
    """Quest objective stub for example."""
    def __init__(self, tenant_id, quest_node_id, description, objective_type, target_entity_id, is_required):
        self.tenant_id = tenant_id
        self.quest_node_id = quest_node_id
        self.description = description
        self.objective_type = objective_type
        self.target_entity_id = target_entity_id
        self.is_required = is_required
        self.id = None

class QuestNode:
    """Quest node stub for example."""
    def __init__(self, tenant_id, parent_chain_id, name, description, quest_type, difficulty, quest_giver_id, is_repeatable, is_hidden, estimated_time_minutes):
        self.tenant_id = tenant_id
        self.parent_chain_id = parent_chain_id
        self.name = name
        self.description = description
        self.quest_type = quest_type
        self.difficulty = difficulty
        self.quest_giver_id = quest_giver_id
        self.is_repeatable = is_repeatable
        self.is_hidden = is_hidden
        self.estimated_time_minutes = estimated_time_minutes
        self.objectives = []
        self.prerequisites = []
        self.id = None

class QuestRewardTier:
    """Quest reward tier stub for example."""
    def __init__(self, tenant_id, name, tier, reward_ids):
        self.tenant_id = tenant_id
        self.name = name
        self.tier = tier
        self.reward_ids = reward_ids
        self.id = None

class QuestChain:
    """Quest chain stub for example."""
    def __init__(self, tenant_id, name, campaign_id, difficulty, estimated_playtime_hours, quest_giver_id, quests):
        self.tenant_id = tenant_id
        self.name = name
        self.campaign_id = campaign_id
        self.difficulty = difficulty
        self.estimated_playtime_hours = estimated_playtime_hours
        self.quest_giver_id = quest_giver_id
        self.quests = quests
        self.id = None
        self.epilogue_id = None

def create_ancient_artifact_quest_chain(tenant_id: str, world_id: str, campaign_id: str) -> QuestChain:
    """
    Create complex quest chain "Ancient Artifact Recovery" with multiple stages.
    This is a realistic example for AAA RPG games like Witcher, Mass Effect.
    """
    
    # 1. Create quest giver (archaeologist)
    quest_giver = QuestGiver(
        tenant_id=tenant_id,
        name="Dr. Elena Vance",
        location_id=f"{world_id}:location_ruins",
        dialogue="Магистр! Я нашла древний свиток..."
    )
    quest_giver.id = f"{world_id}:npc_dr_vance"  # Assign ID
    
    # 2. Create main quest (find artifact)
    main_quest = QuestNode(
        tenant_id=tenant_id,
        parent_chain_id=None,
        name="Find the Ancient Artifact",
        description="Dr. Vance discovered an artifact in the Ruins. Retrieve it.",
        quest_type="main",
        difficulty="hard",
        quest_giver_id=quest_giver.id,
        is_repeatable=False,
        is_hidden=False,
        estimated_time_minutes=60
    )
    
    # 3. Create quest objectives
    objective_1 = QuestObjective(
        tenant_id=tenant_id,
        quest_node_id=main_quest.id,
        description="Find the artifact in the Ruins",
        objective_type="interaction",
        target_entity_id=f"{world_id}:location_ruins",
        is_required=True
    )
    
    objective_2 = QuestObjective(
        tenant_id=tenant_id,
        quest_node_id=main_quest.id,
        description="Bring the artifact to Dr. Vance",
        objective_type="item_delivery",
        target_entity_id=quest_giver.id,
        is_required=True
    )
    
    main_quest.objectives = [objective_1, objective_2]
    
    # 4. Create reward tier (rare items + XP)
    reward_tier = QuestRewardTier(
        tenant_id=tenant_id,
        name="Ancient Artifact Rewards",
        tier=2,
        reward_ids=[
            f"{world_id}:item_ancient_artifact",
            f"{world_id}:xp_1000",
            f"{world_id}:item_scarab_amulet"
        ]
    )
    
    # 5. Create prerequisites (level requirement)
    # In production, this would be QuestPrerequisite entity
    main_quest.prerequisites = [
        {
            "type": "level",
            "value": 30,
            "description": "Requires level 30 to access Ruins"
        }
    ]
    
    # 6. Setup reward
    main_quest.experience_reward = 1000
    
    # 7. Create side quest (translate artifact text)
    translation_quest = QuestNode(
        tenant_id=tenant_id,
        parent_chain_id=None,
        name="Translate Artifact Text",
        description="Dr. Vance needs help translating ancient text on the artifact.",
        quest_type="side",
        difficulty="easy",
        quest_giver_id=quest_giver.id,
        is_repeatable=False,
        is_hidden=False,
        estimated_time_minutes=30
    )
    
    translation_quest.objectives = [
        QuestObjective(
            tenant_id=tenant_id,
            quest_node_id=translation_quest.id,
            description="Translate all text from the artifact",
            objective_type="interaction",
            target_entity_id=f"{world_id}:item_ancient_artifact",
            is_required=True
        )
    ]
    
    # 8. Create secret quest (hidden passage behind artifact)
    secret_quest = QuestNode(
        tenant_id=tenant_id,
        parent_chain_id=None,
        name="Discover Hidden Passage",
        description="Behind the artifact lies a secret passage to ancient ruins.",
        quest_type="hidden",
        difficulty="medium",
        quest_giver_id=quest_giver.id,
        is_repeatable=False,
        is_hidden=True,  # Players must discover this
        estimated_time_minutes=45
    )
    
    secret_quest.objectives = [
        QuestObjective(
            tenant_id=tenant_id,
            quest_node_id=secret_quest.id,
            description="Find the hidden passage behind the artifact",
            objective_type="interaction",
            target_entity_id=f"{world_id}:location_secret_passage",
            is_required=True
        )
    ]
    
    # 9. Create quest chain
    quest_chain = QuestChain(
        tenant_id=tenant_id,
        name="Ancient Artifact Recovery",
        campaign_id=campaign_id,
        difficulty="hard",
        estimated_playtime_hours=4,
        quest_giver_id=quest_giver.id,
        quests=[main_quest, translation_quest, secret_quest]
    )
    
    return quest_chain

def validate_quest_chain(quest_chain: QuestChain) -> list[str]:
    """
    Validate quest chain and return list of errors.
    """
    errors = []
    
    # Validate structure
    if not quest_chain.quests:
        errors.append("Quest chain must have at least 1 quest")
    
    if not quest_chain.quest_giver_id:
        errors.append("Quest chain must have a quest giver")
    
    # Validate quests
    for quest in quest_chain.quests:
        if not quest.name:
            errors.append(f"Quest {quest.id} has no name")
        
        if not quest.objectives:
            errors.append(f"Quest {quest.name} has no objectives")
        
        if quest.estimated_time_minutes <= 0:
            errors.append(f"Quest {quest.name} must have positive time")
    
    # Validate objectives
    for quest in quest_chain.quests:
        for obj in quest.objectives:
            if not obj.is_required and obj.objective_type in ["item_delivery", "item_use"]:
                errors.append(f"Objective '{obj.description}' must be required for item quests")
    
    return errors

def export_quest_chain_to_json(quest_chain: QuestChain, output_path: str) -> None:
    """
    Export quest chain to JSON format for game engines (Unreal, Unity).
    """
    # Create JSON structure compatible with Unreal Engine
    json_data = {
        "quest_chain": {
            "id": str(quest_chain.id),
            "name": quest_chain.name,
            "campaign_id": quest_chain.campaign_id,
            "difficulty": quest_chain.difficulty,
            "estimated_playtime_hours": quest_chain.estimated_playtime_hours,
            "quest_giver_id": quest_chain.quest_giver_id,
            "quests": [
                {
                    "id": str(quest.id),
                    "name": quest.name,
                    "description": quest.description,
                    "type": quest.quest_type,
                    "difficulty": quest.difficulty,
                    "is_repeatable": quest.is_repeatable,
                    "is_hidden": quest.is_hidden,
                    "estimated_time_minutes": quest.estimated_time_minutes,
                    "objectives": [
                        {
                            "id": str(obj.id),
                            "description": obj.description,
                            "type": obj.objective_type,
                            "target_entity_id": obj.target_entity_id if obj.target_entity_id else None,
                            "is_required": obj.is_required
                        } for obj in quest.objectives
                    ],
                    "prerequisites": [
                        {
                            "type": p.get("type"),
                            "value": p.get("value"),
                            "description": p.get("description")
                        } for p in quest.prerequisites
                    ] if quest.prerequisites else []
                } for quest in quest_chain.quests
            ]
        },
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "export_tool": "MythWeave v1.0",
            "author": "MythWeave Chronicles"
        }
    }
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    # Example tenant and world IDs
    tenant_id = "tenant_001"
    world_id = "world_001"
    campaign_id = "campaign_001"
    
    # Create quest chain
    quest_chain = create_ancient_artifact_quest_chain(tenant_id, world_id, campaign_id)
    
    # Validate quest chain
    errors = validate_quest_chain(quest_chain)
    if errors:
        print(f"❌ Quest chain validation failed with {len(errors)} errors:")
        for error in errors[:10]:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ Quest chain created and validated successfully!")
        print(f"📚 Quest chain: {quest_chain.name}")
        print(f"📚 Number of quests: {len(quest_chain.quests)}")
        print(f"📚 Estimated playtime: {quest_chain.estimated_playtime_hours} hours")
        print(f"📚 Objectives: {sum(len(q.objectives) for q in quest_chain.quests)}")
        
        # Export to JSON
        output_path = "examples/quest_ancient_artifact_recovery.json"
        export_quest_chain_to_json(quest_chain, output_path)
        print(f"✅ Quest chain exported to {output_path}")
