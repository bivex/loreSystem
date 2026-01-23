"""
Lore Axioms Entity

Defines the immutable logical axioms that govern the world.
These are static rules that cannot be changed during simulation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Timestamp,
    Version,
)
from ..value_objects.progression import (
    CharacterClass,
    StatType,
    CharacterLevel,
    StatValue,
    ExperiencePoints,
)
from ..exceptions import InvariantViolation


class AxiomType(str, Enum):
    """Types of lore axioms."""
    CLASS_DEFINITION = "class_definition"
    STAT_DEFINITION = "stat_definition"
    MAX_STAT_BOUND = "max_stat_bound"
    CLASS_STAT_RELATION = "class_stat_relation"
    FORBIDDEN_COMBINATION = "forbidden_combination"
    REQUIRED_EXPERIENCE = "required_experience"
    LEVEL_UP_RULE = "level_up_rule"


@dataclass
class LoreAxiom:
    """
    Individual lore axiom.
    
    Represents a single immutable rule of the world.
    """
    axiom_type: AxiomType
    predicate: str  # FOL predicate
    parameters: Dict[str, str]  # Parameter mappings
    description: str

    def to_fol(self) -> str:
        """Convert axiom to First-Order Logic format."""
        if self.axiom_type == AxiomType.CLASS_DEFINITION:
            return f"class({self.parameters['class']})."
        elif self.axiom_type == AxiomType.STAT_DEFINITION:
            return f"stat({self.parameters['stat']})."
        elif self.axiom_type == AxiomType.MAX_STAT_BOUND:
            return f"max_stat({self.parameters['stat']}, {self.parameters['max_value']})."
        elif self.axiom_type == AxiomType.CLASS_STAT_RELATION:
            return f"uses_stat({self.parameters['class']}, {self.parameters['stat']})."
        elif self.axiom_type == AxiomType.FORBIDDEN_COMBINATION:
            return f"false :- {self.predicate}."
        elif self.axiom_type == AxiomType.REQUIRED_EXPERIENCE:
            return f"required_xp({self.parameters['level']}, {self.parameters['xp']})."
        elif self.axiom_type == AxiomType.LEVEL_UP_RULE:
            return f"can_level_up(C, T) :- level(C, L, T), experience(C, XP, T), required_xp(L, R), XP >= R."
        else:
            return f"% {self.description}"


@dataclass
class LoreAxioms:
    """
    Complete set of lore axioms for a world.
    
    This is the static, immutable foundation that governs all progression.
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    axioms: List[LoreAxiom]
    
    # Derived data for efficient access
    classes: Set[CharacterClass] = field(init=False)
    stats: Set[StatType] = field(init=False)
    max_stat_bounds: Dict[StatType, int] = field(init=False)
    class_stat_relations: Dict[CharacterClass, Set[StatType]] = field(init=False)
    required_experience: Dict[int, int] = field(init=False)
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate and derive axiom data."""
        self._validate_invariants()
        self._derive_data()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        
        # Check for duplicate axioms (same predicate)
        predicates = [axiom.predicate for axiom in self.axioms]
        if len(predicates) != len(set(predicates)):
            raise InvariantViolation("Duplicate axioms not allowed")
    
    def _derive_data(self):
        """Derive efficient lookup structures from axioms."""
        self.classes = set()
        self.stats = set()
        self.max_stat_bounds = {}
        self.class_stat_relations = {}
        self.required_experience = {}
        
        for axiom in self.axioms:
            if axiom.axiom_type == AxiomType.CLASS_DEFINITION:
                self.classes.add(CharacterClass(axiom.parameters['class']))
            elif axiom.axiom_type == AxiomType.STAT_DEFINITION:
                self.stats.add(StatType(axiom.parameters['stat']))
            elif axiom.axiom_type == AxiomType.MAX_STAT_BOUND:
                stat = StatType(axiom.parameters['stat'])
                max_val = int(axiom.parameters['max_value'])
                self.max_stat_bounds[stat] = max_val
            elif axiom.axiom_type == AxiomType.CLASS_STAT_RELATION:
                cls = CharacterClass(axiom.parameters['class'])
                stat = StatType(axiom.parameters['stat'])
                if cls not in self.class_stat_relations:
                    self.class_stat_relations[cls] = set()
                self.class_stat_relations[cls].add(stat)
            elif axiom.axiom_type == AxiomType.REQUIRED_EXPERIENCE:
                level = int(axiom.parameters['level'])
                xp = int(axiom.parameters['xp'])
                self.required_experience[level] = xp
    
    def get_max_stat(self, stat: StatType) -> Optional[int]:
        """Get maximum bound for a stat."""
        return self.max_stat_bounds.get(stat)
    
    def get_required_xp(self, level: int) -> Optional[int]:
        """Get experience required for a level."""
        return self.required_experience.get(level)
    
    def can_use_stat(self, cls: CharacterClass, stat: StatType) -> bool:
        """Check if a class can use a stat."""
        return stat in self.class_stat_relations.get(cls, set())
    
    def to_fol_file(self) -> str:
        """Export all axioms as FOL for Prover9/Mace4."""
        lines = [
            "% Lore Axioms - Generated from LoreAxioms entity",
            "% World ID: " + str(self.world_id),
            "",
        ]
        
        for axiom in self.axioms:
            lines.append(axiom.to_fol())
        
        return "\n".join(lines)
    
    @classmethod
    def create_default(cls, tenant_id: TenantId, world_id: EntityId) -> 'LoreAxioms':
        """Create default lore axioms for a fantasy RPG."""
        axioms = [
            # Class definitions
            LoreAxiom(
                axiom_type=AxiomType.CLASS_DEFINITION,
                predicate="class(warrior)",
                parameters={"class": "warrior"},
                description="Warrior class definition"
            ),
            LoreAxiom(
                axiom_type=AxiomType.CLASS_DEFINITION,
                predicate="class(mage)",
                parameters={"class": "mage"},
                description="Mage class definition"
            ),
            LoreAxiom(
                axiom_type=AxiomType.CLASS_DEFINITION,
                predicate="class(rogue)",
                parameters={"class": "rogue"},
                description="Rogue class definition"
            ),
            
            # Stat definitions
            LoreAxiom(
                axiom_type=AxiomType.STAT_DEFINITION,
                predicate="stat(strength)",
                parameters={"stat": "strength"},
                description="Strength stat definition"
            ),
            LoreAxiom(
                axiom_type=AxiomType.STAT_DEFINITION,
                predicate="stat(intellect)",
                parameters={"stat": "intellect"},
                description="Intellect stat definition"
            ),
            LoreAxiom(
                axiom_type=AxiomType.STAT_DEFINITION,
                predicate="stat(agility)",
                parameters={"stat": "agility"},
                description="Agility stat definition"
            ),
            
            # Max stat bounds
            LoreAxiom(
                axiom_type=AxiomType.MAX_STAT_BOUND,
                predicate="max_stat(strength, 100)",
                parameters={"stat": "strength", "max_value": "100"},
                description="Strength maximum bound"
            ),
            LoreAxiom(
                axiom_type=AxiomType.MAX_STAT_BOUND,
                predicate="max_stat(intellect, 120)",
                parameters={"stat": "intellect", "max_value": "120"},
                description="Intellect maximum bound"
            ),
            LoreAxiom(
                axiom_type=AxiomType.MAX_STAT_BOUND,
                predicate="max_stat(agility, 90)",
                parameters={"stat": "agility", "max_value": "90"},
                description="Agility maximum bound"
            ),
            
            # Class-stat relations
            LoreAxiom(
                axiom_type=AxiomType.CLASS_STAT_RELATION,
                predicate="uses_stat(warrior, strength)",
                parameters={"class": "warrior", "stat": "strength"},
                description="Warriors use strength"
            ),
            LoreAxiom(
                axiom_type=AxiomType.CLASS_STAT_RELATION,
                predicate="uses_stat(mage, intellect)",
                parameters={"class": "mage", "stat": "intellect"},
                description="Mages use intellect"
            ),
            LoreAxiom(
                axiom_type=AxiomType.CLASS_STAT_RELATION,
                predicate="uses_stat(rogue, agility)",
                parameters={"class": "rogue", "stat": "agility"},
                description="Rogues use agility"
            ),
            
            # Forbidden combinations
            LoreAxiom(
                axiom_type=AxiomType.FORBIDDEN_COMBINATION,
                predicate="has_class(C, mage), equip(C, heavy_armor, T)",
                parameters={},
                description="Mages cannot equip heavy armor"
            ),
            
            # Experience requirements
            LoreAxiom(
                axiom_type=AxiomType.REQUIRED_EXPERIENCE,
                predicate="required_xp(1, 0)",
                parameters={"level": "1", "xp": "0"},
                description="Level 1 requires 0 XP"
            ),
            LoreAxiom(
                axiom_type=AxiomType.REQUIRED_EXPERIENCE,
                predicate="required_xp(2, 100)",
                parameters={"level": "2", "xp": "100"},
                description="Level 2 requires 100 XP"
            ),
            LoreAxiom(
                axiom_type=AxiomType.REQUIRED_EXPERIENCE,
                predicate="required_xp(3, 250)",
                parameters={"level": "3", "xp": "250"},
                description="Level 3 requires 250 XP"
            ),
            
            # Level up rule
            LoreAxiom(
                axiom_type=AxiomType.LEVEL_UP_RULE,
                predicate="can_level_up(C, T)",
                parameters={},
                description="Level up condition"
            ),
        ]
        
        from ..value_objects.common import Timestamp, Version
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            axioms=axioms,
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
            version=Version(1),
        )
