"""CAMEL-powered rumor → event → relationship bridge."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence

from src.domain.entities.character import Character
from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.event import Event
from src.domain.entities.rumor import Rumor
from src.domain.repositories.rumor_repository import IRumorRepository
from src.domain.value_objects.common import (
    Backstory,
    CharacterName,
    Description,
    EntityId,
    EventOutcome,
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


class RumorBridgeService:
    def __init__(
        self,
        repository: IRumorRepository,
        backend: AgentTextBackend | None = None,
        character_repository: CharacterStore | None = None,
        event_repository: EventStore | None = None,
        relationship_repository: RelationshipStore | None = None,
        allow_fallback: bool = True,
    ):
        self.repository = repository
        self.backend = backend or CamelChatBackend()
        self.character_repository = character_repository
        self.event_repository = event_repository
        self.relationship_repository = relationship_repository
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

    def generate_story_chain(self, request: RumorGenerationRequest) -> RumorChainResult:
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

        return RumorChainResult(rumors=rumors, characters=list(characters_by_name.values()), events=events, relationships=relationships)

    def _build_rumor_prompt(self, request: RumorGenerationRequest, agent_name: str) -> str:
        return (
            f"Theme: {request.theme}\n"
            f"Context: {request.context or 'No extra context provided.'}\n"
            f"Need exactly 1 rumor as JSON with name, description, source_name, truth_level, spread_speed, credibility_score.\n"
            f"Speaker persona: {agent_name}"
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

    def _parse_items(self, raw: str, key: str) -> list[dict]:
        snippet = raw.strip()
        match = re.search(r"(\[.*\]|\{.*\})", snippet, re.S)
        payload = json.loads(match.group(1) if match else snippet)
        items = payload.get(key, [payload]) if isinstance(payload, dict) else payload
        return [item for item in items if isinstance(item, dict)]

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