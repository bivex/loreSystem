"""
Example: Campaign Management

This example demonstrates how AAA game dev studios can use
MythWeave's domain model to create, validate and manage
branching story campaigns with multiple endings.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Domain entities (in production, these would be imported from src.domain)
# For this example, we'll define minimal stubs
class Campaign:
    """Campaign entity stub for example."""
    def __init__(self, tenant_id, id, name, description, campaign_type, difficulty, recommended_level_range):
        self.tenant_id = tenant_id
        self.id = id
        self.name = name
        self.description = description
        self.campaign_type = campaign_type
        self.difficulty = difficulty
        self.recommended_level_range = recommended_level_range
        self.chapters = []
        self.plot_branches = []
        self.endings = []
        self.metadata = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class Chapter:
    """Chapter entity stub for example."""
    def __init__(self, tenant_id, id, name, type, number, campaign_id):
        self.tenant_id = tenant_id
        self.id = id
        self.name = name
        self.type = type
        self.number = number
        self.campaign_id = campaign_id

class PlotBranch:
    """Plot branch stub for example."""
    def __init__(self, tenant_id, id, branch_point_id, branch_type, description, condition_id, consequences):
        self.tenant_id = tenant_id
        self.id = id
        self.branch_point_id = branch_point_id
        self.branch_type = branch_type
        self.description = description
        self.condition_id = condition_id
        self.consequences = consequences or []

class Ending:
    """Ending entity stub for example."""
    def __init__(self, tenant_id, id, name, ending_type, description, is_canon, rarity, campaign_id):
        self.tenant_id = tenant_id
        self.id = id
        self.name = name
        self.ending_type = ending_type
        self.description = description
        self.is_canon = is_canon
        self.rarity = rarity
        self.campaign_id = campaign_id

class MoralChoice:
    """Moral choice stub for example."""
    def __init__(self, tenant_id, id, prompt, description, options, choice_alignment, urgency, consequence_ids):
        self.tenant_id = tenant_id
        self.id = id
        self.prompt = prompt
        self.description = description
        self.options = options
        self.choice_alignment = choice_alignment
        self.urgency = urgency
        self.consequence_ids = consequence_ids or []

def create_war_of_three_kingdoms_campaign(tenant_id: str, world_id: str) -> Campaign:
    """
    Create "War of Three Kingdoms" campaign with branching narrative.
    This is a realistic example for AAA RPG games like Witcher, Mass Effect.
    """
    
    # 1. Create prologue
    prologue = Chapter(
        tenant_id=tenant_id,
        id=None,
        name="Prologue: Three Kingdoms United",
        type="prologue",
        number=0
        campaign_id=None
    )
    prologue.description = "Long ago, three kingdoms - Solaris, Lunaris, and Terratia - lived in harmony beneath the Three Moons. Peace and prosperity reigned throughout the realm..."
    prologue.created_at = datetime.now()
    prologue.updated_at = datetime.now()
    
    # 2. Create main chapters (one for each kingdom)
    chapter_1 = Chapter(
        tenant_id=tenant_id,
        id=None,
        name="Chapter 1: The Invasion Begins",
        type="main",
        number=1,
        campaign_id=None
    )
    chapter_1.description = "Without warning, shadows moved across the realm. The Dark Lord Malachar's forces invaded Solaris Kingdom first, sweeping through northern territories..."
    chapter_1.created_at = datetime.now()
    chapter_1.updated_at = datetime.now()
    
    chapter_2 = Chapter(
        tenant_id=tenant_id,
        id=None,
        name="Chapter 2: Shadow War",
        type="main",
        number=2,
        campaign_id=None
    )
    chapter_2.description = "As Solaris fell, Lunaris and Terratia forged an alliance. Together they pushed back the darkness, but at great cost. Ancient ruins were desecrated, and thousands of innocent lives were lost..."
    chapter_2.created_at = datetime.now()
    chapter_2.updated_at = datetime.now()
    
    chapter_3 = Chapter(
        tenant_id=tenant_id,
        id=None,
        name="Chapter 3: Final Confrontation",
        type="main",
        number=3,
        campaign_id=None
    )
    chapter_3.description = "The combined armies of the three kingdoms marched on Malachar's fortress at Mount Vespera. In the final battle, the Dark Lord was defeated, but not before his final curse bound the souls of the fallen..."
    chapter_3.created_at = datetime.now()
    chapter_3.updated_at = datetime.now()
    
    # 3. Create final act (branch point for ending choice)
    final_act = PlotBranch(
        tenant_id=tenant_id,
        id=None,
        branch_point_id=None,
        branch_type="choice",
        description="Player chooses the fate of the three kingdoms - unite them, conquer them, or remain neutral",
        condition_id=None,
        consequences=[]
    )
    final_act.created_at = datetime.now()
    final_act.updated_at = datetime.now()
    
    # 4. Create three endings with different rarities
    good_ending = Ending(
        tenant_id=tenant_id,
        id=None,
        name="Good Ending: Three Kingdoms United",
        ending_type="good",
        description="Through diplomacy and mutual understanding, the three kingdoms unite to form a powerful alliance. Peace and prosperity return to the realm for generations to come.",
        is_canon=False,
        rarity="common",
        campaign_id=None
    )
    good_ending.created_at = datetime.now()
    good_ending.updated_at = datetime.now()
    
    evil_ending = Ending(
        tenant_id=tenant_id,
        id=None,
        name="Evil Ending: Eternal Tyrant",
        ending_type="evil",
        description="You exploit the chaos and destruction to become the supreme ruler of all three kingdoms. Eternal darkness and tyranny cover the realm, but at what cost to your soul?",
        is_canon=False,
        rarity="rare",
        campaign_id=None
    )
    evil_ending.created_at = datetime.now()
    evil_ending.updated_at = datetime.now()
    
    neutral_ending = Ending(
        tenant_id=tenant_id,
        id=None,
        name="Neutral Ending: Silent Observer",
        ending_type="neutral",
        description="You choose not to interfere, becoming a silent observer of the conflict. The three kingdoms destroy each other, and darkness eventually consumes everything. You watch from the shadows, powerless but alive.",
        is_canon=False,
        rarity="uncommon",
        campaign_id=None
    )
    neutral_ending.created_at = datetime.now()
    neutral_ending.updated_at = datetime.now()
    
    # 5. Create moral choice prompt
    moral_choice = MoralChoice(
        tenant_id=tenant_id,
        id=None,
        prompt="How do you resolve the conflict between the three kingdoms?",
        description="The fate of the realm hangs in the balance. Your decision will shape the future of all three kingdoms.",
        options=[
            {"id": "good", "text": "Unite the kingdoms diplomatically", "alignment": "good"},
            {"id": "evil", "text": "Conquer all kingdoms by force", "alignment": "evil"},
            {"id": "neutral", "text": "Remain neutral observer", "alignment": "neutral"}
        ],
        choice_alignment="neutral",
        urgency="high",
        consequence_ids=[good_ending.id, evil_ending.id, neutral_ending.id]
    )
    moral_choice.created_at = datetime.now()
    moral_choice.updated_at = datetime.now()
    
    # 6. Create campaign entity
    campaign = Campaign(
        tenant_id=tenant_id,
        id=None,
        name="War of Three Kingdoms",
        description="An epic RPG campaign with branching narrative, moral choices, and multiple endings set in a fantasy world with three warring kingdoms.",
        campaign_type="main_story",
        difficulty="medium",
        recommended_level_range=[10, 50]
    )
    campaign.created_at = datetime.now()
    campaign.updated_at = datetime.now()
    
    # 7. Link everything together
    prologue.campaign_id = campaign.id
    chapter_1.campaign_id = campaign.id
    chapter_2.campaign_id = campaign.id
    chapter_3.campaign_id = campaign.id
    final_act.campaign_id = chapter_3.id
    
    good_ending.campaign_id = campaign.id
    evil_ending.campaign_id = campaign.id
    neutral_ending.campaign_id = campaign.id
    
    moral_choice.campaign_id = final_act.id
    
    campaign.chapters = [prologue.id, chapter_1.id, chapter_2.id, chapter_3.id]
    campaign.plot_branches = [final_act.id]
    campaign.endings = [good_ending.id, evil_ending.id, neutral_ending.id]
    
    # 8. Add metadata
    campaign.metadata = {
        "estimated_playtime_hours": 60,  # Estimated 60 hours to complete
        "total_endings": 3,
        "canonical_ending": None,  # Player chooses
        "moral_alignment_system": "good/evil/neutral",
        "replay_value": "high",  # Multiple endings encourage replay
    }
    
    return campaign

def validate_campaign(campaign: Campaign) -> List[str]:
    """Validate campaign and return list of errors."""
    errors = []
    
    # Validate structure
    if not campaign.chapters:
        errors.append("Campaign must have at least 1 chapter")
    
    if not campaign.plot_branches:
        errors.append("Campaign must have at least 1 plot branch")
    
    if not campaign.endings:
        errors.append("Campaign must have at least 1 ending")
    
    # Validate content
    for i, chapter in enumerate(campaign.chapters, 1):
        if not chapter.name:
            errors.append(f"Chapter {i} has no name")
    
    # Validate endings
    ending_types = [e.ending_type for e in campaign.endings]
    if "good" not in ending_types:
        errors.append("Campaign must have a 'good' ending")
    
    # Validate moral choice
    if "good" in [opt["alignment"] for opt in campaign.plot_branches[0].consequences[0].options if "moral_choice" in str(campaign.plot_branches[0].consequences[0]).lower()]:
        pass  # This is a very basic check
    
    return errors

def export_campaign_to_json(campaign: Campaign, output_path: str) -> None:
    """Export campaign to JSON format for game engines."""
    export_data = {
        "campaign": {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "type": campaign.campaign_type,
            "difficulty": campaign.difficulty,
            "recommended_level_range": campaign.recommended_level_range
        },
        "structure": {
            "prologue": {
                "name": campaign.chapters[0].name,
                "description": campaign.chapters[0].description
            },
            "chapters": [
                {
                    "id": chapter.id,
                    "name": chapter.name,
                    "type": chapter.type,
                    "number": chapter.number,
                    "description": chapter.description
                } for chapter in campaign.chapters[1:]
            ],
            "plot_branches": [
                {
                    "id": branch.id,
                    "type": branch.branch_type,
                    "description": branch.description,
                    "moral_choice": campaign.plot_branches[0].consequences[0].prompt if branch.branch_type == "choice"
                } for branch in campaign.plot_branches
            ],
            "endings": [
                {
                    "id": ending.id,
                    "name": ending.name,
                    "type": ending.ending_type,
                    "description": ending.description,
                    "is_canon": ending.is_canon,
                    "rarity": ending.rarity
                } for ending in campaign.endings
            ]
        },
        "metadata": campaign.metadata,
        "export_info": {
            "export_date": datetime.now().isoformat(),
            "export_tool": "MythWeave Chronicles v1.0",
            "author": "AAA Game Development Studio"
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Campaign exported to {output_path}")

# Example usage
if __name__ == "__main__":
    # Create campaign
    campaign = create_war_of_three_kingdoms_campaign("tenant_001", "world_001")
    
    # Validate campaign
    errors = validate_campaign(campaign)
    if errors:
        print(f"❌ Campaign validation failed with {len(errors)} errors:")
        for error in errors[:10]:
            print(f"  {error}")
    else:
        print("✅ Campaign created and validated successfully")
        print(f"📚 Name: {campaign.name}")
        print(f"📚 Type: {campaign.campaign_type}")
        print(f"📚 Difficulty: {campaign.difficulty}")
        print(f"📚 Chapters: {len(campaign.chapters)}")
        print(f"📚 Plot Branches: {len(campaign.plot_branches)}")
        print(f"📚 Endings: {len(campaign.endings)}")
        print(f"🎬 Est. Playtime: {campaign.metadata.get('estimated_playtime_hours', 0)} hours")
        
        # Export to JSON
        output_path = "examples/campaign_war_of_three_kingdoms.json"
        export_campaign_to_json(campaign, output_path)
