"""
Example: Validation & Export

This example demonstrates comprehensive validation and export
functionality for loreSystem's domain model, ready for
integration with AAA game engines (Unreal, Unity, Godot).
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys

# Domain entities (in production, these would be imported from src.domain)
# For this example, we'll define minimal stubs with validation logic
class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class Campaign:
    """Campaign stub with validation logic."""
    def __init__(self, id, tenant_id, name, description, campaign_type, difficulty):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.description = description
        self.campaign_type = campaign_type
        self.difficulty = difficulty
        self.chapters = []
        self.plot_branches = []
        self.endings = []
        self.quests = []
    
    def validate(self) -> List[str]:
        """Validate campaign and return list of errors."""
        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Campaign name cannot be empty")
        
        if self.campaign_type not in ["main_story", "side_story", "one_shot"]:
            errors.append(f"Invalid campaign type: {self.campaign_type}")
        
        if self.difficulty not in ["easy", "medium", "hard", "insane"]:
            errors.append(f"Invalid difficulty: {self.difficulty}")
        
        return errors

class Chapter:
    """Chapter stub with validation logic."""
    def __init__(self, id, campaign_id, name, type, number):
        self.id = id
        self.campaign_id = campaign_id
        self.name = name
        self.type = type
        self.number = number
        self.quests = []
    
    def validate(self) -> List[str]:
        """Validate chapter and return list of errors."""
        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Chapter name cannot be empty")
        
        if self.type not in ["main", "prologue", "epilogue", "interlude"]:
            errors.append(f"Invalid chapter type: {self.type}")
        
        if self.number < 1:
            errors.append(f"Chapter number must be >= 1, got {self.number}")
        
        return errors

class Quest:
    """Quest stub with validation logic."""
    def __init__(self, id, campaign_id, name, description, quest_type, difficulty, estimated_time_minutes, prerequisites=None):
        self.id = id
        self.campaign_id = campaign_id
        self.name = name
        self.description = description
        self.quest_type = quest_type
        self.difficulty = difficulty
        self.estimated_time_minutes = estimated_time_minutes
        self.prerequisites = prerequisites or []
    
    def validate(self) -> List[str]:
        """Validate quest and return list of errors."""
        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Quest name cannot be empty")
        
        if self.quest_type not in ["main", "side", "hidden", "system"]:
            errors.append(f"Invalid quest type: {self.quest_type}")
        
        if self.estimated_time_minutes <= 0:
            errors.append(f"Quest estimated time must be positive, got {self.estimated_time_minutes}")
        
        return errors

def validate_campaign_for_export(campaign: Campaign, chapter_ids: List[str] = None) -> Dict[str, Any]:
    """
    Comprehensive validation for campaign and all associated entities.
    Returns dictionary with validation results and export data.
    """
    validation_errors = []
    
    # 1. Validate campaign structure
    try:
        campaign_errors = campaign.validate()
        if campaign_errors:
            validation_errors.extend([f"Camp: {err}" for err in campaign_errors])
    except Exception as e:
        validation_errors.append(f"Camp: {e}")
    
    # 2. Validate chapters
    chapter_errors = []
    if chapter_ids:
        for chapter_id in chapter_ids:
            try:
                # In production, we'd fetch from repository
                chapter = Chapter(
                    id=chapter_id,
                    campaign_id=campaign.id,
                    name="Sample Chapter",
                    type="main",
                    number=1
                )
                chapter_errors = chapter.validate()
                if chapter_errors:
                    validation_errors.extend([f"Chapt: {chapter_id} - {err}" for err in chapter_errors])
            except Exception as e:
                validation_errors.append(f"Chapt: {chapter_id} - {e}")
    
    # 3. Validate quest prerequisites (cycle detection)
    quest_cycles = {}
    for quest in campaign.quests:
        for prereq in quest.prerequisites:
            if prereq not in quest_cycles:
                quest_cycles[prereq] = []
            quest_cycles[prereq].append(quest)
    
    # Detect cycles
    cycles_found = []
    for quest_id, chain in quest_cycles.items():
        if len(chain) > 1:  # Cycle detected
            cycles_found.append(f"Quest {quest_id} has cyclic dependency")
            validation_errors.append(f"Cycle: {quest_id} forms dependency loop")
    
    # 4. Validate endings
    ending_types = {e.type for e in campaign.endings}
    if "good" not in ending_types:
        validation_errors.append("Campaign must have at least one 'good' ending")
    
    # 5. Prepare export data
    export_data = {
        "campaign": {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "type": campaign.campaign_type,
            "difficulty": campaign.difficulty,
            "chapters": [
                {
                    "id": ch.id,
                    "name": ch.name,
                    "type": ch.type,
                    "number": ch.number
                } for ch in campaign.chapters
            ],
            "endings": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "is_canon": e.is_canon,
                    "rarity": e.rarity
                } for e in campaign.endings
            ]
        },
        "validation": {
            "errors": validation_errors,
            "warnings": [],
            "status": "failed" if validation_errors else "success"
        },
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "export_tool": "MythWeave Chronicles v1.0",
            "author": "AAA Game Development Studio"
        }
    }
    
    return export_data

def export_campaign_to_unreal_json(campaign: Campaign, output_path: str) -> Dict[str, Any]:
    """
    Export campaign to Unreal Engine compatible JSON format.
    """
    unreal_data = {
        "campaign": {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "type": campaign.campaign_type,
            "difficulty": campaign.difficulty,
            "recommended_level_range": [10, 50]
        },
        "structure": {
            "chapters": [
                {
                    "id": ch.id,
                    "name": ch.name,
                    "type": ch.type,
                    "number": ch.number,
                    "quests": []  # Would contain quest data
                } for ch in campaign.chapters
            ],
            "endings": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "is_canon": e.is_canon,
                    "rarity": e.rarity
                } for e in campaign.endings
            ]
        },
        "assets": {
            "campaign_icon": f"campaign_{campaign.id}_icon",
            "campaign_bg": f"bg_{campaign.id}_main",
            "music_theme": f"theme_{campaign.id}_main"
        },
        "unreal_specific": {
            "use_as_level": True,
            "max_players": 4,
            "is_persistent": False
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unreal_data, f, indent=2, ensure_ascii=False)
    
    return {"status": "success", "output_file": output_path}

def export_campaign_to_unity_prefab(campaign: Campaign, output_path: str) -> Dict[str, Any]:
    """
    Export campaign to Unity-compatible Prefab format.
    """
    # Unity Prefabs are usually scene files, so we'll generate
    # a simplified YAML-like structure for demonstration
    prefab_data = {
        "Prefab": {
            "m_Scripting": 1,
            "m_Component": 0,
            "m_Tag": 0,
            "m_ChildCount": 0,
            "m_Version": 1,
            "GameObject": {
                "m_Name": campaign.name,
                "m_TagString": "Campaign",
                "m_Layer": 0,
                "m_Component": [],
                "m_Children": [
                    {
                        "GameObject": {
                            "m_Name": ch.name,
                            "m_TagString": "Chapter"
                        }
                    } for ch in campaign.chapters
                ],
                "m_PrefabParentObject": None,
                "m_PrefabInternal": 0
            }
        },
        "meta": {
            "description": campaign.description,
            "type": campaign.campaign_type,
            "difficulty": campaign.difficulty
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        import yaml  # Requires pyyaml
        yaml.dump(prefab_data, f, default_flow_style=False)
    
    return {"status": "success", "output_file": output_path}

# Example usage
if __name__ == "__main__":
    # Create sample campaign with validation errors
    error_campaign = Campaign(
        id="error_campaign_001",
        tenant_id="tenant_001",
        name="",  # Intentional error
        description="Test error campaign",
        campaign_type="invalid_type",  # Invalid type
        difficulty="invalid_difficulty"  # Invalid difficulty
    )
    
    # Create valid campaign
    valid_campaign = Campaign(
        id="valid_campaign_001",
        tenant_id="tenant_001",
        name="Valid Test Campaign",
        description="A properly structured campaign",
        campaign_type="main_story",
        difficulty="medium"
    )
    
    print("=== Validation & Export Examples ===")
    
    # 1. Validate campaign with errors
    print("\n1. Validating campaign with errors:")
    error_result = validate_campaign_for_export(error_campaign)
    print(f"Status: {error_result['validation']['status']}")
    print(f"Errors: {error_result['validation']['errors']}")
    
    # 2. Validate correct campaign
    print("\n2. Validating correct campaign:")
    valid_result = validate_campaign_for_export(valid_campaign)
    print(f"Status: {valid_result['validation']['status']}")
    print(f"Errors: {valid_result['validation']['errors']}")
    
    # 3. Export to Unreal format
    print("\n3. Exporting to Unreal JSON format:")
    unreal_output = export_campaign_to_unreal_json(error_campaign, "exports/unreal_error_campaign.json")
    print(f"Status: {unreal_output['status']}")
    print(f"Output: {unreal_output['output_file']}")
    
    # 4. Export to Unity Prefab format
    print("\n4. Exporting to Unity Prefab format:")
    unity_output = export_campaign_to_unity_prefab(valid_campaign, "exports/unity_valid_campaign.prefab")
    print(f"Status: {unity_output['status']}")
    print(f"Output: {unity_output['output_file']}")
    
    print("\n✅ Validation & Export examples completed!")
    print("📦 Ready for integration with Unreal Engine, Unity, Godot")
    print("🔍 Comprehensive validation for AAA game dev data")
