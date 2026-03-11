"""CAMEL-powered rumor → event → relationship bridge."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence

from src.domain.entities.act import Act, ActStructure, ActType
from src.domain.entities.alternate_reality import AlternateReality, RealityAccess, RealityType
from src.domain.entities.branch_point import BranchPoint, BranchPointType
from src.domain.entities.campaign import Campaign, CampaignType
from src.domain.entities.chapter import Chapter, ChapterType
from src.domain.entities.character import Character
from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.choice import Choice
from src.domain.entities.consequence import Consequence, ConsequenceSeverity, ConsequenceType
from src.domain.entities.ending import Ending, EndingRarity, EndingType
from src.domain.entities.episode import Episode, EpisodeType
from src.domain.entities.epilogue import Epilogue, EpilogueCondition, EpilogueType
from src.domain.entities.event import Event
from src.domain.entities.flash_forward import FlashForward
from src.domain.entities.flashback import Flashback
from src.domain.entities.moral_choice import ChoiceUrgency, MoralAlignment, MoralChoice
from src.domain.entities.plot_branch import BranchStatus, BranchType, PlotBranch
from src.domain.entities.prologue import Prologue, PrologueType
from src.domain.entities.rumor import Rumor
from src.domain.entities.story import Story
from src.domain.entities.storyline import Storyline
from src.domain.repositories.rumor_repository import IRumorRepository
from src.domain.value_objects.common import (
    Backstory,
    CharacterName,
    ChoiceType,
    Content,
    Description,
    EntityId,
    EventOutcome,
    StoryName,
    StorylineType,
    StoryType,
    TenantId,
    Timestamp,
    Version,
)


@dataclass(frozen=True)
class RumorDraft:
    name: str
    description: str
    source_name: str | None = None
    truth_level: str = "Unverified"
    spread_speed: str = "Moderate"
    credibility_score: int | None = None


@dataclass(frozen=True)
class EventDraft:
    name: str
    description: str
    participant_names: tuple[str, ...] = ()
    outcome: str = "ongoing"


@dataclass(frozen=True)
class CharacterRelationshipDraft:
    character_from_name: str
    character_to_name: str
    description: str
    relationship_type: str = "complicated"
    relationship_level: int = 15
    is_mutual: bool = False


@dataclass(frozen=True)
class CampaignDraft:
    title: str
    description: str
    campaign_type: str = "main_story"
    recommended_level: int | None = None
    estimated_hours: int | None = None
    is_replayable: bool = False


@dataclass(frozen=True)
class StoryDraft:
    name: str
    description: str
    content: str
    story_type: str = "linear"


@dataclass(frozen=True)
class StorylineDraft:
    name: str
    description: str
    storyline_type: str = "main"
    event_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChoiceDraft:
    prompt: str
    options: tuple[str, ...]
    consequences: tuple[str, ...]
    next_story_titles: tuple[str | None, ...]
    choice_type: str = "decision"
    story_name: str | None = None
    is_mandatory: bool = True


@dataclass(frozen=True)
class ConsequenceDraft:
    description: str
    consequence_type: str = "story"
    severity: str = "minor"
    trigger_choice_prompt: str | None = None
    is_permanent: bool = True
    is_visible_to_player: bool = True
    delay_seconds: int | None = None
    conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class MoralChoiceOptionDraft:
    label: str
    outcome: str = ""
    alignment: str = "neutral"


@dataclass(frozen=True)
class MoralChoiceDraft:
    prompt: str
    options: tuple[MoralChoiceOptionDraft, ...]
    description: str | None = None
    choice_alignment: str = "neutral"
    urgency: str = "low"
    consequence_descriptions: tuple[str, ...] = ()
    is_reversible: bool = False
    time_limit_seconds: int | None = None
    affects_reputation: bool = True
    affects_karma: bool = True


@dataclass(frozen=True)
class EndingDraft:
    title: str
    description: str
    ending_type: str = "neutral"
    rarity: str = "common"
    conditions: tuple[str, ...] = ()
    ending_number: int = 1


@dataclass(frozen=True)
class PlotBranchDraft:
    name: str
    description: str
    story_content: str
    branch_type: str = "minor"
    status: str = "locked"
    consequence_descriptions: tuple[str, ...] = ()
    is_reversible: bool = False
    difficulty_modifier: float | None = None


@dataclass(frozen=True)
class BranchPointDraft:
    description: str
    branch_names: tuple[str, ...]
    branch_point_type: str = "choice"
    choice_prompt: str | None = None
    is_mandatory: bool = True
    is_skippable: bool = False
    condition_expression: str | None = None
    skill_check_difficulty: int | None = None
    location_id: int | None = None
    can_revisit: bool = False


@dataclass(frozen=True)
class AlternateRealityDraft:
    name: str
    description: str
    reality_type: str = "parallel_universe"
    access_method: str | None = None
    divergence_point: str | None = None
    is_canon: bool = False
    stability: float | None = None
    entry_points: tuple[str, ...] = ()
    exit_points: tuple[str, ...] = ()


@dataclass(frozen=True)
class FlashbackDraft:
    name: str
    description: str | None = None
    scene_id: str | None = None
    trigger_event_name: str | None = None
    flashback_time: datetime | None = None
    duration_ms: int | None = None
    character_names: tuple[str, ...] = ()
    is_skippable: bool = True
    filter_effect: str = "grayscale"


@dataclass(frozen=True)
class FlashForwardDraft:
    name: str
    description: str
    hinted_event_name: str | None = None
    clarity_level: str = "symbolic"
    is_prophetic: bool = True


@dataclass(frozen=True)
class PrologueDraft:
    title: str
    description: str
    content: str
    prologue_type: str = "world_building"
    is_skippable: bool = False
    is_required: bool = True
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class ActDraft:
    title: str
    description: str
    act_number: int
    act_type: str = "setup"
    structure: str = "three_act"
    key_events: tuple[str, ...] = ()
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class ChapterDraft:
    title: str
    description: str
    sequence_number: int
    act_numbers: tuple[int, ...] = ()
    chapter_type: str = "rising_action"
    required_level: int | None = None
    estimated_minutes: int | None = None
    unlocks_at_level: int | None = None


@dataclass(frozen=True)
class EpisodeDraft:
    title: str
    description: str
    sequence_number: int
    chapter_number: int
    episode_type: str = "narrative"
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class EpilogueDraft:
    title: str
    description: str
    content: str
    epilogue_type: str = "closing_narrative"
    trigger_condition: str = "always"
    is_skippable: bool = False
    estimated_minutes: int | None = None


@dataclass(frozen=True)
class NarrativeStructureDraft:
    campaign: CampaignDraft
    story: StoryDraft
    acts: tuple[ActDraft, ...]
    chapters: tuple[ChapterDraft, ...]
    episodes: tuple[EpisodeDraft, ...]
    storylines: tuple[StorylineDraft, ...] = field(default_factory=tuple)
    plot_branches: tuple[PlotBranchDraft, ...] = field(default_factory=tuple)
    branch_points: tuple[BranchPointDraft, ...] = field(default_factory=tuple)
    choices: tuple[ChoiceDraft, ...] = field(default_factory=tuple)
    consequences: tuple[ConsequenceDraft, ...] = field(default_factory=tuple)
    moral_choices: tuple[MoralChoiceDraft, ...] = field(default_factory=tuple)
    alternate_realities: tuple[AlternateRealityDraft, ...] = field(default_factory=tuple)
    flashbacks: tuple[FlashbackDraft, ...] = field(default_factory=tuple)
    flash_forwards: tuple[FlashForwardDraft, ...] = field(default_factory=tuple)
    endings: tuple[EndingDraft, ...] = field(default_factory=tuple)
    prologue: PrologueDraft | None = None
    epilogue: EpilogueDraft | None = None


@dataclass(frozen=True)
class RumorGenerationRequest:
    tenant_id: int
    world_id: int
    theme: str
    context: str = ""
    count: int = 2
    location_id: int | None = None
    character_names: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RumorChainResult:
    rumors: list[Rumor]
    characters: list[Character]
    events: list[Event]
    relationships: list[CharacterRelationship]
    campaign: Campaign | None = None
    story: Story | None = None
    acts: list[Act] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)
    episodes: list[Episode] = field(default_factory=list)
    storylines: list[Storyline] = field(default_factory=list)
    plot_branches: list[PlotBranch] = field(default_factory=list)
    branch_points: list[BranchPoint] = field(default_factory=list)
    choices: list[Choice] = field(default_factory=list)
    consequences: list[Consequence] = field(default_factory=list)
    moral_choices: list[MoralChoice] = field(default_factory=list)
    alternate_realities: list[AlternateReality] = field(default_factory=list)
    flashbacks: list[Flashback] = field(default_factory=list)
    flash_forwards: list[FlashForward] = field(default_factory=list)
    endings: list[Ending] = field(default_factory=list)
    prologue: Prologue | None = None
    epilogue: Epilogue | None = None


def load_env_file(env_path: str | None = None, override: bool = False) -> str | None:
    candidates = [Path(env_path)] if env_path else [Path.cwd() / ".env", Path(__file__).resolve().parents[4] / ".env"]
    for candidate in candidates:
        if not candidate.exists() or not candidate.is_file():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and (override or key not in os.environ):
                os.environ[key] = value
        return str(candidate)
    return None


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class AgentTextBackend(Protocol):
    def generate(self, system_message: str, user_message: str) -> str: ...


class CharacterStore(Protocol):
    def find_by_name(self, tenant_id: TenantId, world_id: EntityId, name: str): ...
    def save(self, entity: Character) -> Character: ...


class EventStore(Protocol):
    def save(self, entity: Event) -> Event: ...


class RelationshipStore(Protocol):
    def save(self, entity: CharacterRelationship, world_id: EntityId) -> CharacterRelationship: ...


class CampaignStore(Protocol):
    def save(self, entity: Campaign) -> Campaign: ...


class StoryStore(Protocol):
    def save(self, entity: Story) -> Story: ...


class ActStore(Protocol):
    def save(self, entity: Act) -> Act: ...


class ChapterStore(Protocol):
    def save(self, entity: Chapter) -> Chapter: ...


class EpisodeStore(Protocol):
    def save(self, entity: Episode) -> Episode: ...


class PrologueStore(Protocol):
    def save(self, entity: Prologue) -> Prologue: ...


class EpilogueStore(Protocol):
    def save(self, entity: Epilogue) -> Epilogue: ...


class StorylineStore(Protocol):
    def save(self, entity: Storyline) -> Storyline: ...


class ChoiceStore(Protocol):
    def save(self, entity: Choice) -> Choice: ...


class ConsequenceStore(Protocol):
    def save(self, entity: Consequence) -> Consequence: ...


class MoralChoiceStore(Protocol):
    def save(self, entity: MoralChoice) -> MoralChoice: ...


class EndingStore(Protocol):
    def save(self, entity: Ending) -> Ending: ...


class PlotBranchStore(Protocol):
    def save(self, entity: PlotBranch) -> PlotBranch: ...


class BranchPointStore(Protocol):
    def save(self, entity: BranchPoint) -> BranchPoint: ...


class AlternateRealityStore(Protocol):
    def save(self, entity: AlternateReality) -> AlternateReality: ...


class FlashbackStore(Protocol):
    def save(self, entity: Flashback) -> Flashback: ...


class FlashForwardStore(Protocol):
    def save(self, entity: FlashForward) -> FlashForward: ...


class CamelChatBackend:
    """Lazy CAMEL backend that only imports CAMEL at runtime."""

    def __init__(self, model_platform: str | None = None, model_type: str | None = None, model_config: dict | None = None):
        self.model_platform = (model_platform or os.getenv("CAMEL_MODEL_PLATFORM") or "OPENAI").upper()
        self.model_type = model_type or os.getenv("CAMEL_MODEL_TYPE") or "GPT_4O_MINI"
        self.model_url = os.getenv("CAMEL_MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        self.model_config = model_config or self._build_model_config()

    def generate(self, system_message: str, user_message: str) -> str:
        from camel.agents import ChatAgent
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType

        self._validate_environment()
        model = ModelFactory.create(
            model_platform=getattr(ModelPlatformType, self.model_platform, self.model_platform),
            model_type=getattr(ModelType, self.model_type, self.model_type),
            model_config_dict=self.model_config,
            api_key=self._get_api_key(),
            url=self.model_url,
        )
        agent = ChatAgent(model=model)
        response = agent.step(f"System instruction:\n{system_message}\n\nUser request:\n{user_message}")
        if hasattr(response, "msgs") and response.msgs:
            return response.msgs[-1].content
        return str(response)

    def _build_model_config(self) -> dict:
        config = {"temperature": float(os.getenv("CAMEL_MODEL_TEMPERATURE", "0.8"))}
        if os.getenv("CAMEL_MODEL_MAX_TOKENS"):
            config["max_tokens"] = int(os.getenv("CAMEL_MODEL_MAX_TOKENS", "0"))
        return config

    def _validate_environment(self) -> None:
        required_key = {
            "OPENAI": "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GEMINI": "GOOGLE_API_KEY",
            "GOOGLE": "GOOGLE_API_KEY",
            "GROQ": "GROQ_API_KEY",
            "MISTRAL": "MISTRAL_API_KEY",
            "OPENROUTER": "OPENROUTER_API_KEY",
        }.get(self.model_platform)
        if required_key and not os.getenv(required_key):
            raise RuntimeError(f"Missing required environment variable for CAMEL bridge: {required_key}")

    def _get_api_key(self) -> str | None:
        required_key = {
            "OPENAI": "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GEMINI": "GOOGLE_API_KEY",
            "GOOGLE": "GOOGLE_API_KEY",
            "GROQ": "GROQ_API_KEY",
            "MISTRAL": "MISTRAL_API_KEY",
            "OPENROUTER": "OPENROUTER_API_KEY",
        }.get(self.model_platform)
        return os.getenv(required_key) if required_key else None


class DeterministicRumorBackend:
    """Test/offline backend with queued responses."""

    def __init__(self, responses: Sequence[str] | None = None):
        self._responses = list(responses or [])

    def generate(self, system_message: str, user_message: str) -> str:
        if self._responses:
            return self._responses.pop(0)
        theme = user_message.split("Theme:", 1)[-1].splitlines()[0].strip() or "market unrest"
        if "campaign" in system_message.lower() or "prologue" in system_message.lower():
            return json.dumps({
                "campaign": {
                    "title": f"{theme.title()} Campaign",
                    "description": f"A full campaign spun out of the {theme} unrest.",
                    "campaign_type": "main_story",
                    "recommended_level": 5,
                    "estimated_hours": 8,
                    "is_replayable": False,
                },
                "story": {
                    "name": f"{theme.title()} Chronicle",
                    "description": f"The central story thread behind {theme}.",
                    "content": f"Rumors of {theme} grow into a city-wide reckoning.",
                    "story_type": "linear",
                },
                "storylines": [
                    {
                        "name": "Lantern Line",
                        "description": "Tracks how harbor whispers become public raids.",
                        "storyline_type": "main",
                        "events": ["Blue Lantern Raid"],
                    }
                ],
                "plot_branches": [
                    {
                        "name": "Ledger Rebellion",
                        "description": "The survivors expose the magistrate and spark open revolt.",
                        "story_content": "The harbor crowds seize the evidence and turn whispers into rebellion.",
                        "branch_type": "major",
                        "consequence_descriptions": ["The wardens tighten control over the harbor."],
                    },
                    {
                        "name": "Silent Harbor",
                        "description": "The survivors bury the truth and preserve uneasy order.",
                        "story_content": "The ledger disappears and the city survives under a harsher peace.",
                        "branch_type": "temporary",
                        "consequence_descriptions": ["The wardens tighten control over the harbor."],
                        "is_reversible": True,
                    },
                ],
                "branch_points": [
                    {
                        "description": "The survivors decide whether truth or order matters more.",
                        "branch_point_type": "choice",
                        "choice_prompt": "Who do the survivors trust when the bells ring?",
                        "branch_names": ["Ledger Rebellion", "Silent Harbor"],
                    }
                ],
                "choices": [
                    {
                        "prompt": "Who do the survivors trust when the bells ring?",
                        "choice_type": "decision",
                        "options": [
                            {"label": "Trust Mara", "consequence": "Mara reveals the hidden ledger.", "next_story": "Blue Lantern Chronicle"},
                            {"label": "Trust Iven", "consequence": "Iven opens the armory for a last stand.", "next_story": None},
                        ],
                    }
                ],
                "consequences": [
                    {
                        "description": "The wardens tighten control over the harbor.",
                        "consequence_type": "story",
                        "severity": "major",
                        "trigger_choice_prompt": "Who do the survivors trust when the bells ring?",
                    }
                ],
                "moral_choices": [
                    {
                        "prompt": "Will the survivors expose the magistrate or shield the city from panic?",
                        "description": "Truth may save the harbor or break it.",
                        "choice_alignment": "neutral",
                        "urgency": "high",
                        "options": [
                            {"label": "Expose the magistrate", "outcome": "The public rises immediately.", "alignment": "good"},
                            {"label": "Shield the city", "outcome": "Order holds, but corruption survives.", "alignment": "lawful"},
                        ],
                        "consequence_descriptions": ["The wardens tighten control over the harbor."],
                    }
                ],
                "alternate_realities": [
                    {
                        "name": "Bellglass Reflection",
                        "description": "A fractured mirror-reality where the eclipse never ends.",
                        "reality_type": "alternate_possibility",
                        "access_method": "choice",
                        "divergence_point": "The harbor crowd chooses silence instead of revolt.",
                        "entry_points": ["Broken bell tower"],
                        "exit_points": ["Magistrate archive"],
                    }
                ],
                "flashbacks": [
                    {
                        "name": "Night of the First Bell",
                        "description": "A remembered omen from the night fear first took root.",
                        "scene_id": "prologue_1",
                        "trigger_event": "Blue Lantern Raid",
                        "characters": ["Mara Voss"],
                        "filter_effect": "sepia",
                    }
                ],
                "prologue": {
                    "title": "Before the First Whisper",
                    "description": "A tense introduction to the harbor unrest.",
                    "content": f"Before dawn, the first whispers of {theme} spread through the piers.",
                    "prologue_type": "world_building",
                    "is_skippable": False,
                    "is_required": True,
                    "estimated_minutes": 12,
                },
                "acts": [
                    {"title": "Act I - Gathering Tension", "description": "Rumors gather force.", "act_number": 1, "act_type": "setup", "structure": "three_act", "key_events": ["Dockside whispers"], "estimated_minutes": 30},
                    {"title": "Act II - Harbor Flashpoint", "description": "Conflict reaches the streets.", "act_number": 2, "act_type": "rising_action", "structure": "three_act", "key_events": ["Harbor uprising"], "estimated_minutes": 45},
                    {"title": "Act III - Night of Oaths", "description": "Alliances harden into consequence.", "act_number": 3, "act_type": "resolution", "structure": "three_act", "key_events": ["Oathbound alliance"], "estimated_minutes": 35},
                ],
                "chapters": [
                    {"title": "Chapter 1 - Tideborne Hints", "description": "The first clues appear.", "sequence_number": 1, "act_numbers": [1], "chapter_type": "introduction", "estimated_minutes": 20},
                    {"title": "Chapter 2 - Bells at Noon", "description": "The city hears the warning.", "sequence_number": 2, "act_numbers": [2], "chapter_type": "climax", "estimated_minutes": 25},
                    {"title": "Chapter 3 - Harbor Afterglow", "description": "The fallout reshapes loyalties.", "sequence_number": 3, "act_numbers": [3], "chapter_type": "resolution", "estimated_minutes": 20},
                ],
                "episodes": [
                    {"title": "Episode 1 - Hidden Ledger", "description": "A clue surfaces in the market.", "sequence_number": 1, "chapter_number": 1, "episode_type": "narrative", "estimated_minutes": 12},
                    {"title": "Episode 2 - Lantern Riot", "description": "Crowds surge along the quay.", "sequence_number": 2, "chapter_number": 2, "episode_type": "narrative", "estimated_minutes": 15},
                    {"title": "Episode 3 - Oath in the Rain", "description": "Two survivors bind their fates.", "sequence_number": 3, "chapter_number": 3, "episode_type": "narrative", "estimated_minutes": 12},
                ],
                "epilogue": {
                    "title": "After the Rebellion",
                    "description": "The harbor remembers.",
                    "content": f"In the wake of {theme}, the city records new loyalties and old scars.",
                    "epilogue_type": "aftermath",
                    "trigger_condition": "always",
                    "is_skippable": False,
                    "estimated_minutes": 10,
                },
                "flash_forwards": [
                    {
                        "name": "Harbor in Ashes",
                        "description": "A prophetic glimpse of what the bells may yet destroy.",
                        "hinted_event": "Blue Lantern Raid",
                        "clarity_level": "vivid",
                        "is_prophetic": True,
                    }
                ],
                "endings": [
                    {
                        "title": "Lanterns at Dawn",
                        "description": "The city accepts the cost of truth.",
                        "ending_type": "good",
                        "rarity": "uncommon",
                        "conditions": ["Expose the magistrate"],
                        "ending_number": 1,
                    }
                ],
            })
        if "relationship" in system_message.lower():
            return json.dumps([{
                "character_from_name": "Mara Voss",
                "character_to_name": "Iven Hale",
                "description": f"{theme.title()} forces them into a wary alliance.",
                "relationship_type": "ally",
                "relationship_level": 25,
                "is_mutual": True,
            }])
        if "event" in system_message.lower():
            return json.dumps([{
                "name": f"{theme.title()} Flashpoint",
                "description": f"An escalating incident tied to {theme} sweeps through the district.",
                "participant_names": ["Mara Voss", "Iven Hale"],
                "outcome": "ongoing",
            }])
        return json.dumps([{
            "name": f"{theme.title()} Whisper",
            "description": f"A street rumor links {theme} to a hidden patron.",
            "source_name": "Whisper Broker",
            "truth_level": "Unverified",
            "spread_speed": "Rapid",
            "credibility_score": 5,
        }])


DEFAULT_RUMOR_AGENT_PROMPTS = (
    ("Whisper Broker", "Invent one street-level rumor as compact JSON. Keep it flavorful, uncertain, and socially contagious."),
    ("Town Crier", "Invent one public-square rumor as compact JSON. Keep it vivid, dramatic, and suitable for codex seeding."),
)
DEFAULT_EVENT_AGENT_PROMPT = (
    "Chronicle Weaver",
    "Convert the rumors into one consequential event as compact JSON with name, description, participant_names, and outcome.",
)
DEFAULT_RELATIONSHIP_AGENT_PROMPT = (
    "Bond Archivist",
    "Infer one character relationship from the rumors and event as compact JSON with character_from_name, character_to_name, description, relationship_type, relationship_level, is_mutual.",
)
DEFAULT_NARRATIVE_AGENT_PROMPT = (
    "Saga Architect",
    "Convert the rumor/event/relationship chain into one compact JSON object with keys campaign, story, storylines, plot_branches, branch_points, choices, consequences, moral_choices, alternate_realities, flashbacks, prologue, acts, chapters, episodes, flash_forwards, epilogue, endings.",
)


class RumorBridgeService:
    def __init__(
        self,
        repository: IRumorRepository,
        backend: AgentTextBackend | None = None,
        character_repository: CharacterStore | None = None,
        event_repository: EventStore | None = None,
        relationship_repository: RelationshipStore | None = None,
        campaign_repository: CampaignStore | None = None,
        story_repository: StoryStore | None = None,
        act_repository: ActStore | None = None,
        chapter_repository: ChapterStore | None = None,
        episode_repository: EpisodeStore | None = None,
        prologue_repository: PrologueStore | None = None,
        epilogue_repository: EpilogueStore | None = None,
        storyline_repository: StorylineStore | None = None,
        plot_branch_repository: PlotBranchStore | None = None,
        branch_point_repository: BranchPointStore | None = None,
        choice_repository: ChoiceStore | None = None,
        consequence_repository: ConsequenceStore | None = None,
        moral_choice_repository: MoralChoiceStore | None = None,
        alternate_reality_repository: AlternateRealityStore | None = None,
        flashback_repository: FlashbackStore | None = None,
        flash_forward_repository: FlashForwardStore | None = None,
        ending_repository: EndingStore | None = None,
        allow_fallback: bool = True,
    ):
        self.repository = repository
        self.backend = backend or CamelChatBackend()
        self.character_repository = character_repository
        self.event_repository = event_repository
        self.relationship_repository = relationship_repository
        self.campaign_repository = campaign_repository
        self.story_repository = story_repository
        self.act_repository = act_repository
        self.chapter_repository = chapter_repository
        self.episode_repository = episode_repository
        self.prologue_repository = prologue_repository
        self.epilogue_repository = epilogue_repository
        self.storyline_repository = storyline_repository
        self.plot_branch_repository = plot_branch_repository
        self.branch_point_repository = branch_point_repository
        self.choice_repository = choice_repository
        self.consequence_repository = consequence_repository
        self.moral_choice_repository = moral_choice_repository
        self.alternate_reality_repository = alternate_reality_repository
        self.flashback_repository = flashback_repository
        self.flash_forward_repository = flash_forward_repository
        self.ending_repository = ending_repository
        self.allow_fallback = allow_fallback

    def generate_and_persist(self, request: RumorGenerationRequest) -> list[Rumor]:
        drafts: list[RumorDraft] = []
        for index, (agent_name, system_message) in enumerate(DEFAULT_RUMOR_AGENT_PROMPTS, start=1):
            try:
                raw = self.backend.generate(system_message, self._build_rumor_prompt(request, agent_name))
                drafts.extend(self._parse_rumor_drafts(raw))
            except Exception:
                if not self.allow_fallback:
                    raise
                drafts.append(self._fallback_rumor_draft(request, index, agent_name))
        if not drafts and not self.allow_fallback:
            raise RuntimeError("CAMEL bridge did not produce any rumor drafts")
        return [self.repository.save(self._rumor_to_entity(request, draft)) for draft in self._dedupe_rumors(request, drafts, request.count)]

    def generate_story_chain(self, request: RumorGenerationRequest, include_narrative_structure: bool = False) -> RumorChainResult:
        if not (self.character_repository and self.event_repository and self.relationship_repository):
            raise ValueError("Character, event, and relationship repositories are required for story chain generation")

        rumors = self.generate_and_persist(request)
        characters_by_name = self._ensure_seed_characters(request)
        event_drafts = self._generate_event_drafts(request, rumors)
        events: list[Event] = []
        for draft in event_drafts:
            participants = self._ensure_participants(request, draft.participant_names, characters_by_name)
            event = self.event_repository.save(self._event_to_entity(request, draft, participants))
            events.append(event)

        relationship_drafts = self._generate_relationship_drafts(request, rumors, events, tuple(characters_by_name))
        relationships: list[CharacterRelationship] = []
        for draft in relationship_drafts:
            left = self._ensure_character(request, draft.character_from_name, characters_by_name)
            right = self._ensure_character(request, draft.character_to_name, characters_by_name)
            if left.id == right.id:
                continue
            relation = self._relationship_to_entity(request, draft, left.id, right.id, events[0].id if events else None)
            relationships.append(self.relationship_repository.save(relation, EntityId(request.world_id)))

        result = RumorChainResult(rumors=rumors, characters=list(characters_by_name.values()), events=events, relationships=relationships)
        if include_narrative_structure:
            narrative = self.generate_narrative_structure(request, result)
            result = RumorChainResult(
                rumors=result.rumors,
                characters=result.characters,
                events=result.events,
                relationships=result.relationships,
                campaign=narrative.campaign,
                story=narrative.story,
                acts=narrative.acts,
                chapters=narrative.chapters,
                episodes=narrative.episodes,
                storylines=narrative.storylines,
                plot_branches=narrative.plot_branches,
                branch_points=narrative.branch_points,
                choices=narrative.choices,
                consequences=narrative.consequences,
                moral_choices=narrative.moral_choices,
                alternate_realities=narrative.alternate_realities,
                flashbacks=narrative.flashbacks,
                flash_forwards=narrative.flash_forwards,
                endings=narrative.endings,
                prologue=narrative.prologue,
                epilogue=narrative.epilogue,
            )
        return result

    def generate_narrative_structure(self, request: RumorGenerationRequest, chain_result: RumorChainResult) -> RumorChainResult:
        if not all([
            self.campaign_repository,
            self.story_repository,
            self.act_repository,
            self.chapter_repository,
            self.episode_repository,
            self.prologue_repository,
            self.epilogue_repository,
        ]):
            raise ValueError("Campaign/story repositories are required for narrative structure generation")
        try:
            agent_name, system_message = DEFAULT_NARRATIVE_AGENT_PROMPT
            raw = self.backend.generate(system_message, self._build_narrative_prompt(request, chain_result, agent_name))
            draft = self._parse_narrative_structure(raw)
        except Exception:
            if not self.allow_fallback:
                raise
            draft = self._fallback_narrative_structure_draft(request, chain_result)
        return self._persist_narrative_structure(request, chain_result, draft)

    def _build_rumor_prompt(self, request: RumorGenerationRequest, agent_name: str) -> str:
        return (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Need exactly 1 rumor as JSON with name, description, source_name, truth_level, spread_speed, credibility_score.\n"
            f"Speaker persona: {agent_name}"
        )

    def _build_narrative_prompt(self, request: RumorGenerationRequest, chain_result: RumorChainResult, agent_name: str) -> str:
        return (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Speaker persona: {agent_name}\n"
            f"Rumors: {'; '.join(str(r.name) for r in chain_result.rumors)}\n"
            f"Events: {'; '.join(str(e.name) for e in chain_result.events)}\n"
            f"Relationships: {'; '.join(str(r.description) for r in chain_result.relationships) or 'None'}\n"
            "Return one JSON object with campaign, story, storylines, plot_branches, branch_points, choices, consequences, moral_choices, alternate_realities, flashbacks, prologue, acts, chapters, episodes, flash_forwards, epilogue, endings. "
            "For storylines include events/event_names. For plot_branches include name, description, story_content, branch_type, and optional consequence_descriptions. "
            "For branch_points include description, branch_names, and optional choice_prompt. For choices include options with label, consequence, and optional next_story. "
            "For alternate_realities include name, description, reality_type, and optional access_method. For flashbacks include name, description, trigger_event, optional scene_id, and optional characters. "
            "For flash_forwards include name, description, hinted_event, and clarity_level. For chapters include act_numbers. For episodes include chapter_number."
        )

    def _build_event_prompt(self, request: RumorGenerationRequest, rumors: list[Rumor]) -> str:
        rumor_lines = "\n".join(f"- {rumor.name}: {rumor.description}" for rumor in rumors)
        seed = ", ".join(request.character_names) or "Invent participants if needed"
        return f"Theme: {request.theme}\nContext: {request.context}\nRumors:\n{rumor_lines}\nPreferred characters: {seed}"

    def _build_relationship_prompt(self, request: RumorGenerationRequest, rumors: list[Rumor], events: list[Event], character_names: tuple[str, ...]) -> str:
        event_lines = "\n".join(f"- {event.name}: {event.description}" for event in events)
        cast = ", ".join(character_names) or "Invent two names"
        return f"Theme: {request.theme}\nRumors: {', '.join(r.name for r in rumors)}\nEvents:\n{event_lines}\nCast: {cast}"

    def _parse_rumor_drafts(self, raw: str) -> list[RumorDraft]:
        drafts = []
        for item in self._parse_items(raw, "rumors"):
            drafts.append(RumorDraft(
                name=str(item.get("name") or "Unnamed Rumor")[:255],
                description=str(item.get("description") or "An unverified tale is moving through the crowd."),
                source_name=item.get("source_name"),
                truth_level=self._coerce_truth_level(item.get("truth_level")),
                spread_speed=self._coerce_spread_speed(item.get("spread_speed")),
                credibility_score=self._coerce_credibility_score(item.get("credibility_score")),
            ))
        return drafts

    def _parse_event_drafts(self, raw: str) -> list[EventDraft]:
        drafts = []
        for item in self._parse_items(raw, "events"):
            participants = tuple(str(name).strip() for name in item.get("participant_names", []) if str(name).strip())
            drafts.append(EventDraft(
                name=str(item.get("name") or "Unnamed Event")[:255],
                description=str(item.get("description") or "A sudden incident changes local expectations."),
                participant_names=participants,
                outcome=str(item.get("outcome") or "ongoing").lower(),
            ))
        return drafts

    def _parse_relationship_drafts(self, raw: str) -> list[CharacterRelationshipDraft]:
        drafts = []
        for item in self._parse_items(raw, "relationships"):
            drafts.append(CharacterRelationshipDraft(
                character_from_name=str(item.get("character_from_name") or "Witness One"),
                character_to_name=str(item.get("character_to_name") or "Witness Two"),
                description=str(item.get("description") or "Their shared secrets bind them uneasily."),
                relationship_type=str(item.get("relationship_type") or "complicated").lower(),
                relationship_level=self._coerce_relationship_level(item.get("relationship_level")),
                is_mutual=self._coerce_bool(item.get("is_mutual", False)),
            ))
        return drafts

    def _parse_narrative_structure(self, raw: str) -> NarrativeStructureDraft:
        payload = self._parse_object(raw)
        campaign_payload = payload.get("campaign") if isinstance(payload.get("campaign"), dict) else {}
        story_payload = payload.get("story") if isinstance(payload.get("story"), dict) else {}
        prologue_payload = payload.get("prologue") if isinstance(payload.get("prologue"), dict) else {}
        epilogue_payload = payload.get("epilogue") if isinstance(payload.get("epilogue"), dict) else {}
        campaign_text = self._coerce_optional_text(payload.get("campaign"))
        story_text = self._coerce_optional_text(payload.get("story"))
        prologue_text = self._coerce_optional_text(payload.get("prologue"))
        epilogue_text = self._coerce_optional_text(payload.get("epilogue"))
        acts_payload = self._coerce_narrative_items(payload.get("acts"))
        chapters_payload = self._coerce_narrative_items(payload.get("chapters"))
        episodes_payload = self._coerce_narrative_items(payload.get("episodes"))
        storylines_payload = self._coerce_narrative_items(payload.get("storylines"))
        plot_branches_payload = self._coerce_narrative_items(payload.get("plot_branches") or payload.get("branches"))
        branch_points_payload = self._coerce_narrative_items(payload.get("branch_points"))
        choices_payload = self._coerce_narrative_items(payload.get("choices"))
        consequences_payload = self._coerce_narrative_items(payload.get("consequences"))
        moral_choices_payload = self._coerce_narrative_items(payload.get("moral_choices"))
        alternate_realities_payload = self._coerce_narrative_items(payload.get("alternate_realities") or payload.get("alternate_worlds"))
        flashbacks_payload = self._coerce_narrative_items(payload.get("flashbacks"))
        flash_forwards_payload = self._coerce_narrative_items(payload.get("flash_forwards") or payload.get("foreshadowing"))
        endings_payload = self._coerce_narrative_items(payload.get("endings"))

        campaign_title = self._compact_title(
            campaign_payload.get("title") or campaign_text,
            fallback="Harbor Campaign",
        )
        story_name = self._compact_title(
            story_payload.get("name") or campaign_title,
            fallback="Harbor Chronicle",
        )
        return NarrativeStructureDraft(
            campaign=CampaignDraft(
                title=campaign_title,
                description=self._first_non_empty_text(
                    campaign_payload.get("description"),
                    story_text,
                    "A campaign born from mounting unrest.",
                ),
                campaign_type=str(campaign_payload.get("campaign_type") or "main_story"),
                recommended_level=self._coerce_optional_int(campaign_payload.get("recommended_level")),
                estimated_hours=self._coerce_optional_int(campaign_payload.get("estimated_hours")),
                is_replayable=self._coerce_bool(campaign_payload.get("is_replayable", False)),
            ),
            story=StoryDraft(
                name=story_name,
                description=self._first_non_empty_text(
                    story_payload.get("description"),
                    story_text,
                    campaign_payload.get("description"),
                    "A central tale rising from the rumors.",
                ),
                content=self._first_non_empty_text(
                    story_payload.get("content"),
                    story_payload.get("summary"),
                    story_text,
                    "Rumors transform into a structured narrative arc.",
                ),
                story_type=str(story_payload.get("story_type") or "linear"),
            ),
            prologue=self._build_prologue_draft(prologue_payload, prologue_text),
            acts=tuple(
                self._build_act_draft(item, index)
                for index, item in enumerate(acts_payload, start=1)
            ),
            chapters=tuple(
                self._build_chapter_draft(item, index)
                for index, item in enumerate(chapters_payload, start=1)
            ),
            episodes=tuple(
                self._build_episode_draft(item, index)
                for index, item in enumerate(episodes_payload, start=1)
            ),
            storylines=tuple(
                self._build_storyline_draft(item, index)
                for index, item in enumerate(storylines_payload, start=1)
            ),
            plot_branches=tuple(
                self._build_plot_branch_draft(item, index)
                for index, item in enumerate(plot_branches_payload, start=1)
            ),
            branch_points=tuple(
                self._build_branch_point_draft(item, index)
                for index, item in enumerate(branch_points_payload, start=1)
            ),
            choices=tuple(
                self._build_choice_draft(item, index, story_name=story_name)
                for index, item in enumerate(choices_payload, start=1)
            ),
            consequences=tuple(
                self._build_consequence_draft(item, index)
                for index, item in enumerate(consequences_payload, start=1)
            ),
            moral_choices=tuple(
                self._build_moral_choice_draft(item, index)
                for index, item in enumerate(moral_choices_payload, start=1)
            ),
            alternate_realities=tuple(
                self._build_alternate_reality_draft(item, index)
                for index, item in enumerate(alternate_realities_payload, start=1)
            ),
            flashbacks=tuple(
                self._build_flashback_draft(item, index)
                for index, item in enumerate(flashbacks_payload, start=1)
            ),
            flash_forwards=tuple(
                self._build_flash_forward_draft(item, index)
                for index, item in enumerate(flash_forwards_payload, start=1)
            ),
            endings=tuple(
                self._build_ending_draft(item, index)
                for index, item in enumerate(endings_payload, start=1)
            ),
            epilogue=self._build_epilogue_draft(epilogue_payload, epilogue_text),
        )

    def _parse_object(self, raw: str) -> dict:
        snippet = raw.strip()
        match = re.search(r"(\{.*\})", snippet, re.S)
        payload = json.loads(match.group(1) if match else snippet)
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object")
        return payload

    def _parse_items(self, raw: str, key: str) -> list[dict]:
        snippet = raw.strip()
        match = re.search(r"(\[.*\]|\{.*\})", snippet, re.S)
        payload = json.loads(match.group(1) if match else snippet)
        items = payload.get(key, [payload]) if isinstance(payload, dict) else payload
        return [item for item in items if isinstance(item, dict)]

    def _build_prologue_draft(self, payload: dict[str, object], scalar_text: str | None) -> PrologueDraft | None:
        if not payload and not scalar_text:
            return None
        return PrologueDraft(
            title=self._compact_title(payload.get("title"), fallback="Before the First Whisper"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "The opening conditions of the unrest.",
            ),
            content=self._first_non_empty_text(
                payload.get("content"),
                scalar_text,
                "Before the first public confrontation, the city learns to fear silence.",
            ),
            prologue_type=str(payload.get("prologue_type") or "world_building"),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            is_required=self._coerce_bool(payload.get("is_required", True)),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_epilogue_draft(self, payload: dict[str, object], scalar_text: str | None) -> EpilogueDraft | None:
        if not payload and not scalar_text:
            return None
        return EpilogueDraft(
            title=self._compact_title(payload.get("title"), fallback="After the Uprising"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "The consequences that remain after the story closes.",
            ),
            content=self._first_non_empty_text(
                payload.get("content"),
                scalar_text,
                "The final echoes of the campaign settle over the city.",
            ),
            epilogue_type=str(payload.get("epilogue_type") or "aftermath"),
            trigger_condition=str(payload.get("trigger_condition") or "always"),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_act_draft(self, item: object, index: int) -> ActDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ActDraft(
            title=self._compact_title(payload.get("title") or scalar_text, fallback=f"Act {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A major dramatic phase in the campaign.",
            ),
            act_number=self._coerce_positive_int(payload.get("act_number"), index),
            act_type=str(payload.get("act_type") or "setup"),
            structure=str(payload.get("structure") or "three_act"),
            key_events=self._coerce_text_tuple(payload.get("key_events")),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_chapter_draft(self, item: object, index: int) -> ChapterDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ChapterDraft(
            title=self._compact_title(payload.get("title") or scalar_text, fallback=f"Chapter {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A chapter that escalates the campaign story.",
            ),
            sequence_number=self._coerce_positive_int(payload.get("sequence_number") or payload.get("chapter_number"), index),
            act_numbers=self._coerce_positive_int_tuple(payload.get("act_numbers") or payload.get("act_number")),
            chapter_type=str(payload.get("chapter_type") or "rising_action"),
            required_level=self._coerce_optional_int(payload.get("required_level")),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
            unlocks_at_level=self._coerce_optional_int(payload.get("unlocks_at_level")),
        )

    def _build_episode_draft(self, item: object, index: int) -> EpisodeDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return EpisodeDraft(
            title=self._compact_title(payload.get("title") or scalar_text, fallback=f"Episode {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A playable story beat inside the chapter.",
            ),
            sequence_number=self._coerce_positive_int(payload.get("sequence_number") or payload.get("episode_number"), index),
            chapter_number=self._coerce_positive_int(payload.get("chapter_number") or payload.get("chapter"), 1),
            episode_type=str(payload.get("episode_type") or "story"),
            estimated_minutes=self._coerce_optional_int(payload.get("estimated_minutes")),
        )

    def _build_storyline_draft(self, item: object, index: int) -> StorylineDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return StorylineDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Storyline {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A storyline that threads rumors into a larger arc.",
            ),
            storyline_type=str(payload.get("storyline_type") or "main"),
            event_names=self._coerce_text_tuple(payload.get("event_names") or payload.get("events")),
        )

    def _build_plot_branch_draft(self, item: object, index: int) -> PlotBranchDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        consequence_descriptions = self._coerce_text_tuple(payload.get("consequence_descriptions"))
        if not consequence_descriptions and isinstance(payload.get("consequences"), list):
            consequence_descriptions = tuple(
                self._first_non_empty_text(
                    consequence_item.get("description") if isinstance(consequence_item, dict) else consequence_item,
                    f"Branch consequence {offset}",
                )
                for offset, consequence_item in enumerate(payload.get("consequences"), start=1)
            )
        return PlotBranchDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Plot Branch {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "An alternate path through the rumor-born campaign.",
            ),
            story_content=self._first_non_empty_text(
                payload.get("story_content"),
                payload.get("content"),
                payload.get("summary"),
                payload.get("description"),
                scalar_text,
                "The campaign bends into a new consequence-laden path.",
            ),
            branch_type=str(payload.get("branch_type") or "minor"),
            status=str(payload.get("status") or "locked"),
            consequence_descriptions=consequence_descriptions,
            is_reversible=self._coerce_bool(payload.get("is_reversible", False)),
            difficulty_modifier=self._coerce_optional_float(payload.get("difficulty_modifier")),
        )

    def _build_branch_point_draft(self, item: object, index: int) -> BranchPointDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        if isinstance(payload.get("branches"), list):
            branch_names = tuple(
                self._first_non_empty_text(
                    branch_item.get("name") if isinstance(branch_item, dict) else branch_item,
                    f"Plot Branch {offset}",
                )
                for offset, branch_item in enumerate(payload.get("branches"), start=1)
            )
        else:
            branch_names = self._coerce_text_tuple(payload.get("branch_names") or payload.get("branches"))
        return BranchPointDraft(
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Branch point {index} splits the campaign.",
            ),
            branch_names=branch_names,
            branch_point_type=str(payload.get("branch_point_type") or "choice"),
            choice_prompt=self._coerce_optional_text(payload.get("choice_prompt") or payload.get("choice") or payload.get("question")),
            is_mandatory=self._coerce_bool(payload.get("is_mandatory", True)),
            is_skippable=self._coerce_bool(payload.get("is_skippable", False)),
            condition_expression=self._coerce_optional_text(payload.get("condition_expression") or payload.get("condition")),
            skill_check_difficulty=self._coerce_optional_int(payload.get("skill_check_difficulty")),
            location_id=self._coerce_optional_int(payload.get("location_id")),
            can_revisit=self._coerce_bool(payload.get("can_revisit", False)),
        )

    def _build_choice_draft(self, item: object, index: int, story_name: str) -> ChoiceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        option_payloads = payload.get("options") if isinstance(payload.get("options"), list) else []
        options: list[str] = []
        consequences: list[str] = []
        next_story_titles: list[str | None] = []
        for option_index, option_item in enumerate(option_payloads, start=1):
            if isinstance(option_item, dict):
                label = self._first_non_empty_text(
                    option_item.get("label"),
                    option_item.get("option"),
                    option_item.get("text"),
                    option_item.get("title"),
                    f"Option {option_index}",
                )
                consequence = self._first_non_empty_text(
                    option_item.get("consequence"),
                    option_item.get("outcome"),
                    option_item.get("result"),
                    f"{label} shifts the balance of power.",
                )
                next_story = self._coerce_optional_text(option_item.get("next_story") or option_item.get("next_story_title"))
            else:
                label = self._coerce_optional_text(option_item) or f"Option {option_index}"
                consequence = f"{label} shifts the balance of power."
                next_story = None
            options.append(label)
            consequences.append(consequence)
            next_story_titles.append(next_story)
        if len(options) < 2:
            options = ["Support the whisper network", "Report to the wardens"]
            consequences = [
                "The rumor reaches the streets before dawn.",
                "Authority clamps down before the crowd can organize.",
            ]
            next_story_titles = [story_name, None]
        return ChoiceDraft(
            prompt=self._first_non_empty_text(
                payload.get("prompt"),
                payload.get("question"),
                scalar_text,
                f"What should happen at choice point {index}?",
            ),
            options=tuple(options),
            consequences=tuple(consequences),
            next_story_titles=tuple(next_story_titles),
            choice_type=str(payload.get("choice_type") or "decision"),
            story_name=self._coerce_optional_text(payload.get("story_name") or payload.get("story")) or story_name,
            is_mandatory=self._coerce_bool(payload.get("is_mandatory", True)),
        )

    def _build_consequence_draft(self, item: object, index: int) -> ConsequenceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return ConsequenceDraft(
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                f"Consequence {index} reshapes the city.",
            ),
            consequence_type=str(payload.get("consequence_type") or "story"),
            severity=str(payload.get("severity") or "minor"),
            trigger_choice_prompt=self._coerce_optional_text(
                payload.get("trigger_choice_prompt") or payload.get("choice_prompt") or payload.get("choice")
            ),
            is_permanent=self._coerce_bool(payload.get("is_permanent", True)),
            is_visible_to_player=self._coerce_bool(payload.get("is_visible_to_player", True)),
            delay_seconds=self._coerce_optional_int(payload.get("delay_seconds")),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
        )

    def _build_moral_choice_draft(self, item: object, index: int) -> MoralChoiceDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        option_payloads = payload.get("options") if isinstance(payload.get("options"), list) else []
        options = tuple(self._build_moral_choice_option_draft(option, option_index) for option_index, option in enumerate(option_payloads, start=1))
        if len(options) < 2:
            options = (
                MoralChoiceOptionDraft(label="Tell the truth", outcome="The public rallies.", alignment="good"),
                MoralChoiceOptionDraft(label="Preserve order", outcome="Panic stays buried for now.", alignment="lawful"),
            )
        consequence_descriptions = self._coerce_text_tuple(payload.get("consequence_descriptions"))
        if not consequence_descriptions and isinstance(payload.get("consequences"), list):
            consequence_descriptions = tuple(
                self._first_non_empty_text(
                    consequence_item.get("description") if isinstance(consequence_item, dict) else consequence_item,
                    f"Moral consequence {offset}",
                )
                for offset, consequence_item in enumerate(payload.get("consequences"), start=1)
            )
        return MoralChoiceDraft(
            prompt=self._first_non_empty_text(
                payload.get("prompt"),
                payload.get("question"),
                scalar_text,
                f"What moral line must be crossed at decision {index}?",
            ),
            options=options,
            description=self._coerce_optional_text(payload.get("description")),
            choice_alignment=str(payload.get("choice_alignment") or payload.get("alignment") or "neutral"),
            urgency=str(payload.get("urgency") or "low"),
            consequence_descriptions=consequence_descriptions,
            is_reversible=self._coerce_bool(payload.get("is_reversible", False)),
            time_limit_seconds=self._coerce_optional_int(payload.get("time_limit_seconds")),
            affects_reputation=self._coerce_bool(payload.get("affects_reputation", True)),
            affects_karma=self._coerce_bool(payload.get("affects_karma", True)),
        )

    def _build_moral_choice_option_draft(self, item: object, index: int) -> MoralChoiceOptionDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return MoralChoiceOptionDraft(
            label=self._first_non_empty_text(
                payload.get("label"),
                payload.get("option"),
                payload.get("text"),
                scalar_text,
                f"Option {index}",
            ),
            outcome=self._first_non_empty_text(payload.get("outcome"), payload.get("consequence"), ""),
            alignment=str(payload.get("alignment") or "neutral"),
        )

    def _build_ending_draft(self, item: object, index: int) -> EndingDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return EndingDraft(
            title=self._compact_title(payload.get("title") or payload.get("name") or scalar_text, fallback=f"Ending {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A campaign ending that closes the rumor arc.",
            ),
            ending_type=str(payload.get("ending_type") or "neutral"),
            rarity=str(payload.get("rarity") or "common"),
            conditions=self._coerce_text_tuple(payload.get("conditions")),
            ending_number=self._coerce_positive_int(payload.get("ending_number"), index),
        )

    def _build_alternate_reality_draft(self, item: object, index: int) -> AlternateRealityDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return AlternateRealityDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Alternate Reality {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A fractured reality revealed by the campaign's branching choices.",
            ),
            reality_type=str(payload.get("reality_type") or "parallel_universe"),
            access_method=self._coerce_optional_text(payload.get("access_method") or payload.get("access")),
            divergence_point=self._coerce_optional_text(payload.get("divergence_point")),
            is_canon=self._coerce_bool(payload.get("is_canon", False)),
            stability=self._coerce_optional_float(payload.get("stability")),
            entry_points=self._coerce_text_tuple(payload.get("entry_points") or payload.get("entry")),
            exit_points=self._coerce_text_tuple(payload.get("exit_points") or payload.get("exit")),
        )

    def _build_flashback_draft(self, item: object, index: int) -> FlashbackDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return FlashbackDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Flashback {index}"),
            description=self._coerce_optional_text(payload.get("description") or scalar_text),
            scene_id=self._coerce_optional_text(payload.get("scene_id") or payload.get("scene")),
            trigger_event_name=self._coerce_optional_text(payload.get("trigger_event") or payload.get("event")),
            flashback_time=self._coerce_optional_datetime(payload.get("flashback_time") or payload.get("timestamp")),
            duration_ms=self._coerce_optional_int(payload.get("duration_ms")),
            character_names=self._coerce_text_tuple(payload.get("character_names") or payload.get("characters")),
            is_skippable=self._coerce_bool(payload.get("is_skippable", True)),
            filter_effect=self._coerce_flashback_filter(payload.get("filter_effect")),
        )

    def _build_flash_forward_draft(self, item: object, index: int) -> FlashForwardDraft:
        payload = item if isinstance(item, dict) else {}
        scalar_text = self._coerce_optional_text(item)
        return FlashForwardDraft(
            name=self._compact_title(payload.get("name") or payload.get("title") or scalar_text, fallback=f"Flash Forward {index}"),
            description=self._first_non_empty_text(
                payload.get("description"),
                scalar_text,
                "A glimpse of a future consequence still struggling to arrive.",
            ),
            hinted_event_name=self._coerce_optional_text(payload.get("hinted_event_name") or payload.get("hinted_event") or payload.get("event")),
            clarity_level=self._first_non_empty_text(payload.get("clarity_level"), payload.get("clarity"), "symbolic"),
            is_prophetic=self._coerce_bool(payload.get("is_prophetic", True)),
        )

    def _coerce_narrative_items(self, value: object) -> list[object]:
        if isinstance(value, list):
            return [item for item in value if isinstance(item, (dict, str))]
        if isinstance(value, (dict, str)):
            return [value]
        return []

    def _coerce_text_tuple(self, value: object) -> tuple[str, ...]:
        if isinstance(value, list):
            return tuple(str(item).strip() for item in value if self._coerce_optional_text(item))
        scalar_text = self._coerce_optional_text(value)
        return (scalar_text,) if scalar_text else ()

    def _coerce_positive_int_tuple(self, value: object) -> tuple[int, ...]:
        if isinstance(value, list):
            return tuple(
                self._coerce_positive_int(item, index)
                for index, item in enumerate(value, start=1)
                if self._coerce_optional_int(item) is not None
            )
        parsed = self._coerce_optional_int(value)
        return (parsed,) if parsed and parsed > 0 else ()

    def _first_non_empty_text(self, *values: object) -> str:
        for value in values:
            text = self._coerce_optional_text(value)
            if text:
                return text
        return ""

    def _coerce_optional_text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _normalize_lookup_key(self, value: object) -> str:
        return (self._coerce_optional_text(value) or "").lower()

    def _compact_title(self, value: object, fallback: str) -> str:
        text = self._coerce_optional_text(value)
        if not text:
            return fallback
        normalized = re.sub(r"\s+", " ", text).strip().strip('"\'')
        head = re.split(r"[.!?\n]", normalized, maxsplit=1)[0].strip()
        candidate = head or normalized
        if len(candidate) > 120:
            candidate = candidate[:117].rstrip() + "..."
        return candidate or fallback

    def _persist_narrative_structure(self, request: RumorGenerationRequest, chain_result: RumorChainResult, draft: NarrativeStructureDraft) -> RumorChainResult:
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        connected_ids = [character.id for character in chain_result.characters if character.id is not None]

        campaign = self.campaign_repository.save(Campaign.create(
            tenant_id=tenant_id,
            world_id=world_id,
            title=draft.campaign.title,
            description=Description(draft.campaign.description),
            campaign_type=self._coerce_campaign_type(draft.campaign.campaign_type),
            recommended_level=draft.campaign.recommended_level,
            estimated_hours=draft.campaign.estimated_hours,
            is_replayable=draft.campaign.is_replayable,
        ))
        story = self.story_repository.save(Story.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=StoryName(draft.story.name),
            description=draft.story.description,
            story_type=self._coerce_story_type(draft.story.story_type),
            content=Content(draft.story.content),
            connected_world_ids=connected_ids,
        ))

        prologue = None
        if draft.prologue:
            prologue = self.prologue_repository.save(Prologue.create(
                tenant_id=tenant_id,
                campaign_id=campaign.id,
                world_id=world_id,
                title=draft.prologue.title,
                description=Description(draft.prologue.description),
                prologue_type=self._coerce_prologue_type(draft.prologue.prologue_type),
                is_skippable=draft.prologue.is_skippable,
                is_required=draft.prologue.is_required,
                content=draft.prologue.content,
                character_ids=connected_ids,
                estimated_minutes=draft.prologue.estimated_minutes,
            ))

        acts_by_number: dict[int, Act] = {}
        for act_draft in sorted(draft.acts, key=lambda item: item.act_number):
            act = self.act_repository.save(Act.create(
                tenant_id=tenant_id,
                campaign_id=campaign.id,
                world_id=world_id,
                title=act_draft.title,
                description=Description(act_draft.description),
                act_type=self._coerce_act_type(act_draft.act_type),
                act_number=act_draft.act_number,
                structure=self._coerce_act_structure(act_draft.structure),
                key_events=list(act_draft.key_events),
                estimated_minutes=act_draft.estimated_minutes,
            ))
            acts_by_number[act_draft.act_number] = act

        chapters_by_number: dict[int, Chapter] = {}
        for chapter_draft in sorted(draft.chapters, key=lambda item: item.sequence_number):
            act_ids = [acts_by_number[number].id for number in chapter_draft.act_numbers if number in acts_by_number]
            chapter = self.chapter_repository.save(Chapter.create(
                tenant_id=tenant_id,
                campaign_id=campaign.id,
                world_id=world_id,
                title=chapter_draft.title,
                description=Description(chapter_draft.description),
                chapter_type=self._coerce_chapter_type(chapter_draft.chapter_type),
                sequence_number=chapter_draft.sequence_number,
                act_ids=act_ids,
                required_level=chapter_draft.required_level,
                estimated_minutes=chapter_draft.estimated_minutes,
                unlocks_at_level=chapter_draft.unlocks_at_level,
            ))
            chapters_by_number[chapter.sequence_number] = chapter
            campaign.add_chapter(chapter.id)
            self.campaign_repository.save(campaign)
            for number in chapter_draft.act_numbers:
                if number in acts_by_number:
                    acts_by_number[number].add_chapter(chapter.id)
                    self.act_repository.save(acts_by_number[number])

        episodes: list[Episode] = []
        previous_episode_ids: dict[int, EntityId] = {}
        for episode_draft in sorted(draft.episodes, key=lambda item: item.sequence_number):
            chapter = chapters_by_number.get(episode_draft.chapter_number) or next(iter(chapters_by_number.values()), None)
            if chapter is None:
                continue
            required_previous = [previous_episode_ids[chapter.sequence_number]] if chapter.sequence_number in previous_episode_ids else []
            episode = self.episode_repository.save(Episode.create(
                tenant_id=tenant_id,
                chapter_id=chapter.id,
                world_id=world_id,
                title=episode_draft.title,
                description=Description(episode_draft.description),
                episode_type=self._coerce_episode_type(episode_draft.episode_type),
                sequence_number=episode_draft.sequence_number,
                estimated_minutes=episode_draft.estimated_minutes,
                required_previous_episodes=required_previous,
            ))
            chapter.add_episode(episode.id)
            self.chapter_repository.save(chapter)
            previous_episode_ids[chapter.sequence_number] = episode.id
            episodes.append(episode)

        epilogue = None
        if draft.epilogue:
            epilogue = self.epilogue_repository.save(Epilogue.create(
                tenant_id=tenant_id,
                campaign_id=campaign.id,
                world_id=world_id,
                title=draft.epilogue.title,
                description=Description(draft.epilogue.description),
                epilogue_type=self._coerce_epilogue_type(draft.epilogue.epilogue_type),
                trigger_condition=self._coerce_epilogue_condition(draft.epilogue.trigger_condition),
                is_skippable=draft.epilogue.is_skippable,
                content=draft.epilogue.content,
                character_ids=connected_ids,
                estimated_minutes=draft.epilogue.estimated_minutes,
            ))

        storylines: list[Storyline] = []
        if self.storyline_repository:
            event_lookup = {
                self._normalize_lookup_key(event.name): event.id
                for event in chain_result.events
                if event.id is not None
            }
            fallback_event_ids = [event.id for event in chain_result.events if event.id is not None]
            for storyline_draft in draft.storylines:
                event_ids = [
                    event_lookup[key]
                    for key in (self._normalize_lookup_key(name) for name in storyline_draft.event_names)
                    if key in event_lookup
                ]
                if not event_ids:
                    event_ids = list(fallback_event_ids)
                if not event_ids:
                    continue
                now = Timestamp.now()
                storylines.append(self.storyline_repository.save(Storyline(
                    id=None,
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=storyline_draft.name,
                    description=Description(storyline_draft.description),
                    storyline_type=self._coerce_storyline_type(storyline_draft.storyline_type),
                    event_ids=event_ids,
                    quest_ids=[],
                    created_at=now,
                    updated_at=now,
                    version=Version(1),
                )))

        choices: list[Choice] = []
        choices_by_prompt: dict[str, Choice] = {}
        if self.choice_repository:
            story_lookup = {self._normalize_lookup_key(str(story.name)): story.id}
            for choice_draft in draft.choices:
                next_story_ids = [
                    story_lookup.get(self._normalize_lookup_key(title)) if title else None
                    for title in choice_draft.next_story_titles
                ]
                choice = self.choice_repository.save(Choice.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    story_id=story.id,
                    prompt=choice_draft.prompt,
                    choice_type=self._coerce_choice_type(choice_draft.choice_type),
                    options=list(choice_draft.options),
                    consequences=list(choice_draft.consequences),
                    next_story_ids=next_story_ids,
                    is_mandatory=choice_draft.is_mandatory,
                ))
                choices.append(choice)
                choices_by_prompt[self._normalize_lookup_key(choice.prompt)] = choice

        consequences: list[Consequence] = []
        consequences_by_description: dict[str, Consequence] = {}
        if self.consequence_repository:
            fallback_action_id = next((event.id for event in chain_result.events if event.id is not None), None)
            for consequence_draft in draft.consequences:
                trigger_choice = choices_by_prompt.get(self._normalize_lookup_key(consequence_draft.trigger_choice_prompt or ""))
                trigger_choice_id = trigger_choice.id if trigger_choice else (choices[0].id if choices else None)
                trigger_action_id = None if trigger_choice_id else fallback_action_id
                if trigger_choice_id is None and trigger_action_id is None:
                    continue
                consequence = self.consequence_repository.save(Consequence.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    description=Description(consequence_draft.description),
                    consequence_type=self._coerce_consequence_type(consequence_draft.consequence_type),
                    severity=self._coerce_consequence_severity(consequence_draft.severity),
                    is_permanent=consequence_draft.is_permanent,
                    is_visible_to_player=consequence_draft.is_visible_to_player,
                    trigger_choice_id=trigger_choice_id,
                    trigger_action_id=trigger_action_id,
                    delay_seconds=consequence_draft.delay_seconds,
                    conditions=list(consequence_draft.conditions),
                ))
                consequences.append(consequence)
                consequences_by_description[self._normalize_lookup_key(str(consequence.description))] = consequence

        moral_choices: list[MoralChoice] = []
        if self.moral_choice_repository:
            for moral_choice_draft in draft.moral_choices:
                consequence_ids = [
                    consequence.id
                    for description in moral_choice_draft.consequence_descriptions
                    if (consequence := consequences_by_description.get(self._normalize_lookup_key(description))) is not None and consequence.id is not None
                ]
                moral_choices.append(self.moral_choice_repository.save(MoralChoice.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    prompt=moral_choice_draft.prompt,
                    options=[
                        {"label": option.label, "outcome": option.outcome, "alignment": option.alignment}
                        for option in moral_choice_draft.options
                    ],
                    choice_alignment=self._coerce_moral_alignment(moral_choice_draft.choice_alignment),
                    urgency=self._coerce_choice_urgency(moral_choice_draft.urgency),
                    campaign_id=campaign.id,
                    description=Description(moral_choice_draft.description) if moral_choice_draft.description else None,
                    consequence_ids=consequence_ids,
                    is_reversible=moral_choice_draft.is_reversible,
                    time_limit_seconds=moral_choice_draft.time_limit_seconds,
                    affects_reputation=moral_choice_draft.affects_reputation,
                    affects_karma=moral_choice_draft.affects_karma,
                    character_ids=connected_ids,
                )))

        plot_branches: list[PlotBranch] = []
        plot_branches_by_name: dict[str, PlotBranch] = {}
        if self.plot_branch_repository and campaign.id is not None:
            placeholder_origin_branch_point_id = campaign.id
            for plot_branch_draft in draft.plot_branches:
                consequence_ids = [
                    consequence.id
                    for description in plot_branch_draft.consequence_descriptions
                    if (consequence := consequences_by_description.get(self._normalize_lookup_key(description))) is not None and consequence.id is not None
                ]
                plot_branch = PlotBranch.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    campaign_id=campaign.id,
                    name=plot_branch_draft.name,
                    story_content=plot_branch_draft.story_content,
                    origin_branch_point_id=placeholder_origin_branch_point_id,
                    branch_type=self._coerce_branch_type(plot_branch_draft.branch_type),
                    description=Description(plot_branch_draft.description),
                    consequence_ids=consequence_ids,
                    is_reversible=plot_branch_draft.is_reversible,
                    difficulty_modifier=plot_branch_draft.difficulty_modifier,
                )
                object.__setattr__(plot_branch, "status", self._coerce_branch_status(plot_branch_draft.status))
                plot_branch = self.plot_branch_repository.save(plot_branch)
                plot_branches.append(plot_branch)
                plot_branches_by_name[self._normalize_lookup_key(plot_branch.name)] = plot_branch

        branch_points: list[BranchPoint] = []
        branch_point_ids_by_branch_name: dict[str, EntityId] = {}
        if self.branch_point_repository and campaign.id is not None:
            branch_ids_fallback = [branch.id for branch in plot_branches if branch.id is not None]
            choice_ids_by_prompt = {
                self._normalize_lookup_key(choice.prompt): choice.id
                for choice in choices
                if choice.id is not None
            }
            for branch_point_draft in draft.branch_points:
                branch_ids = [
                    branch.id
                    for branch_name in branch_point_draft.branch_names
                    if (branch := plot_branches_by_name.get(self._normalize_lookup_key(branch_name))) is not None and branch.id is not None
                ]
                if len(branch_ids) < 2:
                    branch_ids = branch_ids_fallback[:2]
                if len(branch_ids) < 2:
                    continue
                branch_point_type = self._coerce_branch_point_type(branch_point_draft.branch_point_type)
                choice_id = choice_ids_by_prompt.get(self._normalize_lookup_key(branch_point_draft.choice_prompt or ""))
                if branch_point_type == BranchPointType.CHOICE and choice_id is None:
                    choice_id = next(iter(choice_ids_by_prompt.values()), None)
                if branch_point_type == BranchPointType.CHOICE and choice_id is None:
                    branch_point_type = BranchPointType.TRIGGER
                if branch_point_type == BranchPointType.CONDITION and not branch_point_draft.condition_expression:
                    branch_point_type = BranchPointType.TRIGGER
                if branch_point_type == BranchPointType.SKILL_CHECK and branch_point_draft.skill_check_difficulty is None:
                    branch_point_type = BranchPointType.TRIGGER
                location_id = branch_point_draft.location_id or request.location_id
                branch_point = self.branch_point_repository.save(BranchPoint.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    campaign_id=campaign.id,
                    description=Description(branch_point_draft.description),
                    branch_ids=branch_ids,
                    branch_point_type=branch_point_type,
                    is_mandatory=branch_point_draft.is_mandatory,
                    is_skippable=branch_point_draft.is_skippable,
                    condition_expression=branch_point_draft.condition_expression,
                    skill_check_difficulty=branch_point_draft.skill_check_difficulty,
                    choice_id=choice_id,
                    location_id=EntityId(location_id) if location_id else None,
                    can_revisit=branch_point_draft.can_revisit,
                ))
                branch_points.append(branch_point)
                if branch_point.id is not None:
                    for branch_name in branch_point_draft.branch_names:
                        branch_point_ids_by_branch_name[self._normalize_lookup_key(branch_name)] = branch_point.id
            if branch_point_ids_by_branch_name:
                for plot_branch in plot_branches:
                    branch_point_id = branch_point_ids_by_branch_name.get(self._normalize_lookup_key(plot_branch.name))
                    if branch_point_id is None or plot_branch.origin_branch_point_id == branch_point_id:
                        continue
                    object.__setattr__(plot_branch, "origin_branch_point_id", branch_point_id)
                    object.__setattr__(plot_branch, "updated_at", Timestamp.now())
                    object.__setattr__(plot_branch, "version", plot_branch.version.increment())
                    self.plot_branch_repository.save(plot_branch)

        alternate_realities: list[AlternateReality] = []
        if self.alternate_reality_repository:
            for alternate_reality_draft in draft.alternate_realities:
                now = Timestamp.now()
                alternate_realities.append(self.alternate_reality_repository.save(AlternateReality(
                    tenant_id=tenant_id,
                    name=alternate_reality_draft.name,
                    description=Description(alternate_reality_draft.description),
                    reality_type=self._coerce_reality_type(alternate_reality_draft.reality_type),
                    created_at=now,
                    updated_at=now,
                    id=None,
                    access_method=self._coerce_reality_access(alternate_reality_draft.access_method),
                    parent_world_id=world_id,
                    divergence_point=alternate_reality_draft.divergence_point,
                    is_canon=alternate_reality_draft.is_canon,
                    stability=alternate_reality_draft.stability or 1.0,
                    entry_points=list(alternate_reality_draft.entry_points),
                    exit_points=list(alternate_reality_draft.exit_points),
                    version=Version(1),
                )))

        flashbacks: list[Flashback] = []
        if self.flashback_repository:
            character_ids_by_name = {
                self._normalize_lookup_key(character.name.value): str(character.id.value)
                for character in chain_result.characters
                if character.id is not None
            }
            default_scene_id = next((f"episode-{episode.id.value}" for episode in episodes if episode.id is not None), None) or f"story-{story.id.value}"
            for flashback_draft in draft.flashbacks:
                now_dt = datetime.now(timezone.utc)
                flashbacks.append(self.flashback_repository.save(Flashback(
                    id=None,
                    tenant_id=str(request.tenant_id),
                    name=flashback_draft.name,
                    scene_id=flashback_draft.scene_id or default_scene_id,
                    created_at=now_dt,
                    updated_at=now_dt,
                    description=flashback_draft.description,
                    trigger_event=flashback_draft.trigger_event_name,
                    flashback_time=flashback_draft.flashback_time,
                    duration_ms=flashback_draft.duration_ms,
                    characters=[
                        character_ids_by_name[key]
                        for key in (self._normalize_lookup_key(name) for name in flashback_draft.character_names)
                        if key in character_ids_by_name
                    ],
                    is_skippable=flashback_draft.is_skippable,
                    filter_effect=flashback_draft.filter_effect,
                    metadata={"world_id": request.world_id},
                )))

        flash_forwards: list[FlashForward] = []
        if self.flash_forward_repository:
            event_ids_by_name = {
                self._normalize_lookup_key(event.name): event.id
                for event in chain_result.events
                if event.id is not None
            }
            for flash_forward_draft in draft.flash_forwards:
                flash_forwards.append(self.flash_forward_repository.save(FlashForward.create(
                    tenant_id=tenant_id,
                    world_id=world_id,
                    name=flash_forward_draft.name,
                    description=Description(flash_forward_draft.description),
                    hinted_event_id=event_ids_by_name.get(self._normalize_lookup_key(flash_forward_draft.hinted_event_name or "")),
                    clarity_level=flash_forward_draft.clarity_level,
                    is_prophetic=flash_forward_draft.is_prophetic,
                )))

        endings: list[Ending] = []
        if self.ending_repository:
            for ending_draft in draft.endings:
                endings.append(self.ending_repository.save(Ending.create(
                    tenant_id=tenant_id,
                    campaign_id=campaign.id,
                    world_id=world_id,
                    title=ending_draft.title,
                    description=Description(ending_draft.description),
                    ending_type=self._coerce_ending_type(ending_draft.ending_type),
                    rarity=self._coerce_ending_rarity(ending_draft.rarity),
                    conditions=list(ending_draft.conditions),
                    epilogue_id=epilogue.id if epilogue and epilogue.id else None,
                    ending_number=ending_draft.ending_number,
                )))

        return RumorChainResult(
            rumors=chain_result.rumors,
            characters=chain_result.characters,
            events=chain_result.events,
            relationships=chain_result.relationships,
            campaign=campaign,
            story=story,
            acts=list(acts_by_number.values()),
            chapters=list(chapters_by_number.values()),
            episodes=episodes,
            storylines=storylines,
            plot_branches=plot_branches,
            branch_points=branch_points,
            choices=choices,
            consequences=consequences,
            moral_choices=moral_choices,
            alternate_realities=alternate_realities,
            flashbacks=flashbacks,
            flash_forwards=flash_forwards,
            endings=endings,
            prologue=prologue,
            epilogue=epilogue,
        )

    def _fallback_narrative_structure_draft(self, request: RumorGenerationRequest, chain_result: RumorChainResult) -> NarrativeStructureDraft:
        theme = request.theme.strip().title() or "Harbor"
        return NarrativeStructureDraft(
            campaign=CampaignDraft(title=f"{theme} Campaign", description=f"A campaign shaped by {request.theme}.", campaign_type="main_story", recommended_level=5, estimated_hours=8),
            story=StoryDraft(name=f"{theme} Chronicle", description=f"The main story behind {request.theme}.", content=f"{request.context or request.theme} evolves from whispered danger into public consequence.", story_type="linear"),
            prologue=PrologueDraft(title="Before the First Whisper", description="The opening setup.", content=f"Before the first clash, {request.theme} already haunts the city.", prologue_type="world_building", estimated_minutes=10),
            acts=(
                ActDraft(title="Act I - Setup", description="Tension gathers.", act_number=1, act_type="setup", structure="three_act", key_events=tuple(r.name for r in chain_result.rumors[:1]), estimated_minutes=30),
                ActDraft(title="Act II - Confrontation", description="Conflict erupts.", act_number=2, act_type="rising_action", structure="three_act", key_events=tuple(e.name for e in chain_result.events[:1]), estimated_minutes=40),
                ActDraft(title="Act III - Resolution", description="Consequences settle.", act_number=3, act_type="resolution", structure="three_act", key_events=tuple(r.description for r in chain_result.relationships[:1]), estimated_minutes=25),
            ),
            chapters=(
                ChapterDraft(title="Chapter 1", description="The first omen.", sequence_number=1, act_numbers=(1,), chapter_type="introduction", estimated_minutes=20),
                ChapterDraft(title="Chapter 2", description="The harbor ignites.", sequence_number=2, act_numbers=(2,), chapter_type="climax", estimated_minutes=25),
                ChapterDraft(title="Chapter 3", description="Oaths remain.", sequence_number=3, act_numbers=(3,), chapter_type="resolution", estimated_minutes=20),
            ),
            episodes=(
                EpisodeDraft(title="Episode 1", description="A clue surfaces.", sequence_number=1, chapter_number=1, episode_type="narrative", estimated_minutes=12),
                EpisodeDraft(title="Episode 2", description="Crowds surge.", sequence_number=2, chapter_number=2, episode_type="narrative", estimated_minutes=15),
                EpisodeDraft(title="Episode 3", description="Alliances harden.", sequence_number=3, chapter_number=3, episode_type="narrative", estimated_minutes=12),
            ),
            storylines=(
                StorylineDraft(name=f"{theme} Main Line", description=f"A storyline following how {request.theme} reshapes public order.", storyline_type="main"),
            ),
            plot_branches=(
                PlotBranchDraft(
                    name="Open Revolt",
                    description="The harbor chooses open resistance.",
                    story_content="The whisper network becomes a public uprising.",
                    branch_type="major",
                    consequence_descriptions=("The harbor guard imposes a citywide curfew.",),
                ),
                PlotBranchDraft(
                    name="Silent Compliance",
                    description="The city buries the truth to preserve peace.",
                    story_content="Fear sinks beneath the surface while authority grows harsher.",
                    branch_type="temporary",
                    consequence_descriptions=("The harbor guard imposes a citywide curfew.",),
                    is_reversible=True,
                ),
            ),
            branch_points=(
                BranchPointDraft(
                    description="The final warning forces the harbor to choose between truth and order.",
                    branch_names=("Open Revolt", "Silent Compliance"),
                    branch_point_type="choice",
                    choice_prompt="Who should carry the final warning?",
                ),
            ),
            choices=(
                ChoiceDraft(
                    prompt="Who should carry the final warning?",
                    options=("Trust the dockworkers", "Trust the magistrate"),
                    consequences=("The crowd prepares itself.", "Authority seizes the message."),
                    next_story_titles=(f"{theme} Chronicle", None),
                    choice_type="decision",
                    story_name=f"{theme} Chronicle",
                ),
            ),
            consequences=(
                ConsequenceDraft(
                    description="The harbor guard imposes a citywide curfew.",
                    consequence_type="story",
                    severity="major",
                    trigger_choice_prompt="Who should carry the final warning?",
                ),
            ),
            moral_choices=(
                MoralChoiceDraft(
                    prompt="Will the survivors reveal the truth or preserve calm?",
                    options=(
                        MoralChoiceOptionDraft(label="Reveal the truth", outcome="The city prepares for the cost.", alignment="good"),
                        MoralChoiceOptionDraft(label="Preserve calm", outcome="Fear stays buried for another night.", alignment="lawful"),
                    ),
                    description="A final moral reckoning closes the campaign.",
                    choice_alignment="neutral",
                    urgency="high",
                    consequence_descriptions=("The harbor guard imposes a citywide curfew.",),
                ),
            ),
            alternate_realities=(
                AlternateRealityDraft(
                    name="Ashen Harbor",
                    description="A reality where the bells never stop tolling.",
                    reality_type="alternate_possibility",
                    access_method="choice",
                    divergence_point="The crowd chooses silence instead of revolt.",
                    entry_points=("Bell tower",),
                    exit_points=("Archivist's vault",),
                ),
            ),
            flashbacks=(
                FlashbackDraft(
                    name="First Bell at Dusk",
                    description="Mara remembers the first night the harbor learned fear.",
                    scene_id="prologue_1",
                    trigger_event_name=chain_result.events[0].name if chain_result.events else None,
                    character_names=tuple(character.name.value for character in chain_result.characters[:1]),
                    filter_effect="sepia",
                ),
            ),
            epilogue=EpilogueDraft(title="After the Rebellion", description="The closing aftermath.", content="The city records the cost of the unrest.", epilogue_type="aftermath", trigger_condition="always", estimated_minutes=10),
            flash_forwards=(
                FlashForwardDraft(
                    name="Harbor Under Ash",
                    description="A prophetic glimpse of what the bells may still destroy.",
                    hinted_event_name=chain_result.events[0].name if chain_result.events else None,
                    clarity_level="vivid",
                    is_prophetic=True,
                ),
            ),
            endings=(
                EndingDraft(
                    title="Truth at First Light",
                    description="The harbor accepts the cost of speaking openly.",
                    ending_type="good",
                    rarity="uncommon",
                    conditions=("Reveal the truth",),
                    ending_number=1,
                ),
            ),
        )

    def _generate_event_drafts(self, request: RumorGenerationRequest, rumors: list[Rumor]) -> list[EventDraft]:
        try:
            raw = self.backend.generate(DEFAULT_EVENT_AGENT_PROMPT[1], self._build_event_prompt(request, rumors))
            drafts = self._parse_event_drafts(raw)
        except Exception:
            if not self.allow_fallback:
                raise
            drafts = []
        if drafts:
            return drafts[: max(1, min(request.count, len(drafts)))]
        if not self.allow_fallback:
            raise RuntimeError("CAMEL bridge did not produce any event drafts")
        participants = request.character_names or ("Mara Voss", "Iven Hale")
        return [EventDraft(
            name=f"{request.theme.strip().title() or 'Rumor'} Flashpoint",
            description=f"Whispered tensions around {request.theme.lower()} burst into a visible public incident.",
            participant_names=tuple(participants[:2]),
            outcome="ongoing",
        )]

    def _generate_relationship_drafts(self, request: RumorGenerationRequest, rumors: list[Rumor], events: list[Event], character_names: tuple[str, ...]) -> list[CharacterRelationshipDraft]:
        try:
            raw = self.backend.generate(DEFAULT_RELATIONSHIP_AGENT_PROMPT[1], self._build_relationship_prompt(request, rumors, events, character_names))
            drafts = self._parse_relationship_drafts(raw)
        except Exception:
            if not self.allow_fallback:
                raise
            drafts = []
        if drafts:
            return drafts[:1]
        if not self.allow_fallback:
            raise RuntimeError("CAMEL bridge did not produce any relationship drafts")
        left, right = (character_names + ("Mara Voss", "Iven Hale"))[:2]
        return [CharacterRelationshipDraft(
            character_from_name=left,
            character_to_name=right,
            description=f"The fallout from {request.theme.lower()} forces them into a complicated alliance.",
            relationship_type="ally",
            relationship_level=25,
            is_mutual=True,
        )]

    def _ensure_seed_characters(self, request: RumorGenerationRequest) -> dict[str, Character]:
        characters: dict[str, Character] = {}
        for name in request.character_names:
            self._ensure_character(request, name, characters)
        return characters

    def _ensure_participants(self, request: RumorGenerationRequest, names: tuple[str, ...], characters: dict[str, Character]) -> list[Character]:
        participant_names = tuple(name for name in names if name) or request.character_names or ("Mara Voss", "Iven Hale")
        participants = [self._ensure_character(request, name, characters) for name in participant_names[:3]]
        if not participants:
            participants.append(self._ensure_character(request, "Mara Voss", characters))
        return participants

    def _ensure_character(self, request: RumorGenerationRequest, name: str, characters: dict[str, Character]) -> Character:
        key = name.strip().lower()
        if key in characters:
            return characters[key]
        tenant_id = TenantId(request.tenant_id)
        world_id = EntityId(request.world_id)
        existing = self.character_repository.find_by_name(tenant_id, world_id, name) if self.character_repository else None
        if existing:
            characters[key] = existing
            return existing
        backstory = Backstory((
            f"{name} grew up in the shadow of {request.theme}, learning to read every whisper in the market. "
            f"Now they navigate the unrest around {request.theme.lower()} with equal parts fear, ambition, and survival instinct."
        )[:220])
        created = Character.create(
            tenant_id=tenant_id,
            world_id=world_id,
            name=CharacterName(name),
            backstory=backstory,
            base_hp=100,
            base_atk=50,
            base_def=50,
            base_speed=50,
            energy_cost=0,
        )
        saved = self.character_repository.save(created)
        characters[key] = saved
        return saved

    def _dedupe_rumors(self, request: RumorGenerationRequest, drafts: list[RumorDraft], limit: int) -> list[RumorDraft]:
        unique: list[RumorDraft] = []
        seen = set()
        for draft in drafts:
            key = draft.name.strip().lower()
            if key and key not in seen:
                unique.append(draft)
                seen.add(key)
            if len(unique) >= limit:
                break
        while len(unique) < limit:
            unique.append(self._fallback_rumor_draft(request, len(unique) + 1, "Bridge Fallback"))
        return unique[:limit]

    def _fallback_rumor_draft(self, request: RumorGenerationRequest, index: int, agent_name: str) -> RumorDraft:
        theme = request.theme.strip().title() or "Rumor"
        return RumorDraft(
            name=f"{theme} Rumor {index}",
            description=f"{agent_name} reports whispered talk that {request.theme.lower()} is changing the balance of power.",
            source_name=agent_name,
            truth_level="Unverified",
            spread_speed="Moderate",
            credibility_score=4 + min(index, 4),
        )

    def _rumor_to_entity(self, request: RumorGenerationRequest, draft: RumorDraft) -> Rumor:
        now = Timestamp.now()
        return Rumor(
            id=None,
            tenant_id=TenantId(request.tenant_id),
            name=draft.name,
            description=Description(draft.description),
            world_id=EntityId(request.world_id),
            location_id=EntityId(request.location_id) if request.location_id else None,
            source_name=draft.source_name,
            origin_date=now,
            truth_level=draft.truth_level,
            spread_speed=draft.spread_speed,
            credibility_score=draft.credibility_score,
            is_active=True,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def _event_to_entity(self, request: RumorGenerationRequest, draft: EventDraft, participants: list[Character]) -> Event:
        outcome = self._coerce_event_outcome(draft.outcome)
        return Event.create(
            tenant_id=TenantId(request.tenant_id),
            world_id=EntityId(request.world_id),
            name=draft.name,
            description=Description(draft.description),
            start_date=Timestamp.now(),
            participant_ids=[character.id for character in participants if character.id],
            outcome=outcome,
            location_id=EntityId(request.location_id) if request.location_id else None,
        )

    def _relationship_to_entity(self, request: RumorGenerationRequest, draft: CharacterRelationshipDraft, from_id: EntityId, to_id: EntityId, first_event_id: EntityId | None) -> CharacterRelationship:
        return CharacterRelationship.create(
            tenant_id=TenantId(request.tenant_id),
            character_from_id=from_id,
            character_to_id=to_id,
            relationship_type=self._coerce_relationship_type(draft.relationship_type),
            description=Description(draft.description),
            relationship_level=max(-100, min(100, draft.relationship_level)),
            is_mutual=draft.is_mutual,
            first_met_event_id=first_event_id,
        )

    def _coerce_event_outcome(self, value: str) -> EventOutcome:
        try:
            return EventOutcome(value.lower())
        except Exception:
            return EventOutcome.ONGOING

    def _coerce_relationship_type(self, value: str) -> RelationshipType:
        try:
            return RelationshipType(value.lower())
        except Exception:
            return RelationshipType.COMPLICATED

    def _coerce_campaign_type(self, value: str) -> CampaignType:
        return self._coerce_enum(value, CampaignType, CampaignType.MAIN_STORY)

    def _coerce_story_type(self, value: str) -> StoryType:
        return self._coerce_enum(value, StoryType, StoryType.LINEAR)

    def _coerce_storyline_type(self, value: str) -> StorylineType:
        return self._coerce_enum(value, StorylineType, StorylineType.MAIN)

    def _coerce_choice_type(self, value: str) -> ChoiceType:
        return self._coerce_enum(value, ChoiceType, ChoiceType.DECISION)

    def _coerce_consequence_type(self, value: str) -> ConsequenceType:
        return self._coerce_enum(value, ConsequenceType, ConsequenceType.STORY)

    def _coerce_consequence_severity(self, value: str) -> ConsequenceSeverity:
        return self._coerce_enum(value, ConsequenceSeverity, ConsequenceSeverity.MINOR)

    def _coerce_moral_alignment(self, value: str) -> MoralAlignment:
        return self._coerce_enum(value, MoralAlignment, MoralAlignment.NEUTRAL)

    def _coerce_choice_urgency(self, value: str) -> ChoiceUrgency:
        return self._coerce_enum(value, ChoiceUrgency, ChoiceUrgency.LOW)

    def _coerce_branch_type(self, value: str) -> BranchType:
        return self._coerce_enum(value, BranchType, BranchType.MINOR)

    def _coerce_branch_status(self, value: str) -> BranchStatus:
        return self._coerce_enum(value, BranchStatus, BranchStatus.LOCKED)

    def _coerce_branch_point_type(self, value: str) -> BranchPointType:
        aliases = {"decision": "choice", "event": "trigger"}
        return self._coerce_enum(value, BranchPointType, BranchPointType.CHOICE, aliases)

    def _coerce_reality_type(self, value: str) -> RealityType:
        aliases = {"parallel": "parallel_universe", "timeline": "time_divergence"}
        return self._coerce_enum(value, RealityType, RealityType.PARALLEL_UNIVERSE, aliases)

    def _coerce_reality_access(self, value: str | None) -> RealityAccess | None:
        if not value:
            return None
        aliases = {"story": "story_event"}
        return self._coerce_enum(value, RealityAccess, RealityAccess.STORY_EVENT, aliases)

    def _coerce_act_type(self, value: str) -> ActType:
        return self._coerce_enum(value, ActType, ActType.SETUP)

    def _coerce_act_structure(self, value: str) -> ActStructure:
        return self._coerce_enum(value, ActStructure, ActStructure.THREE_ACT)

    def _coerce_chapter_type(self, value: str) -> ChapterType:
        aliases = {"opening": "introduction", "story": "rising_action"}
        return self._coerce_enum(value, ChapterType, ChapterType.RISING_ACTION, aliases)

    def _coerce_episode_type(self, value: str) -> EpisodeType:
        aliases = {"story": "narrative", "story_beat": "narrative"}
        return self._coerce_enum(value, EpisodeType, EpisodeType.NARRATIVE, aliases)

    def _coerce_prologue_type(self, value: str) -> PrologueType:
        aliases = {"world_building": "backstory", "setup": "backstory"}
        return self._coerce_enum(value, PrologueType, PrologueType.BACKSTORY, aliases)

    def _coerce_epilogue_type(self, value: str) -> EpilogueType:
        aliases = {"closing_narrative": "outcome", "ending": "outcome"}
        return self._coerce_enum(value, EpilogueType, EpilogueType.AFTERMATH, aliases)

    def _coerce_epilogue_condition(self, value: str) -> EpilogueCondition:
        aliases = {"any_ending": "always", "default": "always"}
        return self._coerce_enum(value, EpilogueCondition, EpilogueCondition.ALWAYS, aliases)

    def _coerce_ending_type(self, value: str) -> EndingType:
        return self._coerce_enum(value, EndingType, EndingType.NEUTRAL)

    def _coerce_ending_rarity(self, value: str) -> EndingRarity:
        return self._coerce_enum(value, EndingRarity, EndingRarity.COMMON)

    def _coerce_enum(self, value: str, enum_cls, default, aliases: dict[str, str] | None = None):
        normalized = str(value or default.value).strip().lower().replace("-", "_").replace(" ", "_")
        if aliases and normalized in aliases:
            normalized = aliases[normalized]
        try:
            return enum_cls(normalized)
        except Exception:
            return default

    def _coerce_positive_int(self, value: object, default: int) -> int:
        parsed = self._coerce_optional_int(value)
        if parsed is None or parsed < 1:
            return default
        return parsed

    def _coerce_optional_int(self, value: object) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _coerce_optional_float(self, value: object) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _coerce_optional_datetime(self, value: object) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        except Exception:
            return None

    def _coerce_truth_level(self, value: object) -> str:
        if value is None or value == "":
            return "Unverified"
        normalized = str(value).strip().lower()
        aliases = {
            "false": "False",
            "fake": "False",
            "debunked": "False",
            "unverified": "Unverified",
            "unknown": "Unverified",
            "rumor": "Unverified",
            "partially true": "Partially True",
            "partial": "Partially True",
            "mixed": "Partially True",
            "mostly true": "Partially True",
            "true": "True",
            "confirmed": "True",
            "verified": "True",
        }
        if normalized in aliases:
            return aliases[normalized]
        numeric = self._coerce_optional_float(value)
        if numeric is None:
            return "Unverified"
        score = numeric / 10 if numeric > 1 else numeric
        if score <= 0.15:
            return "False"
        if score <= 0.6:
            return "Unverified"
        if score <= 0.85:
            return "Partially True"
        return "True"

    def _coerce_spread_speed(self, value: object) -> str:
        if value is None or value == "":
            return "Moderate"
        normalized = str(value).strip().lower()
        aliases = {
            "slow": "Slow",
            "low": "Slow",
            "moderate": "Moderate",
            "medium": "Moderate",
            "steady": "Moderate",
            "rapid": "Rapid",
            "fast": "Rapid",
            "high": "Rapid",
            "viral": "Explosive",
            "explosive": "Explosive",
        }
        if normalized in aliases:
            return aliases[normalized]
        numeric = self._coerce_optional_float(value)
        if numeric is None:
            return "Moderate"
        score = numeric / 10 if numeric > 1 else numeric
        if score <= 0.2:
            return "Slow"
        if score <= 0.55:
            return "Moderate"
        if score <= 0.8:
            return "Rapid"
        return "Explosive"

    def _coerce_credibility_score(self, value: object) -> int | None:
        parsed = self._coerce_optional_int(value)
        if parsed is None:
            return None
        return max(1, min(10, parsed))

    def _coerce_relationship_level(self, value: object) -> int:
        if value is None or value == "":
            return 10
        try:
            return int(value)
        except Exception:
            pass
        normalized = str(value).strip().lower()
        mapping = {
            "hostile": -40,
            "enemy": -35,
            "rival": -20,
            "strained": -10,
            "neutral": 0,
            "tentative": 10,
            "ally": 20,
            "friendly": 25,
            "strong": 35,
            "close": 40,
            "devoted": 50,
        }
        return mapping.get(normalized, 10)

    def _coerce_bool(self, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        normalized = str(value).strip().lower()
        return normalized in {"true", "1", "yes", "y", "on", "mutual"}

    def _coerce_flashback_filter(self, value: object) -> str:
        normalized = str(value or "grayscale").strip().lower().replace(" ", "_")
        valid = {"none", "grayscale", "sepia", "desaturated", "vignette", "blur", "dream", "nightmare"}
        return normalized if normalized in valid else "grayscale"