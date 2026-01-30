"""
CraftingRecipe Entity

A CraftingRecipe defines how to create items from other items.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)


class RecipeDifficulty(str, Enum):
    """Difficulty level for crafting recipes."""
    TRIVIAL = "trivial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class RecipeIngredient:
    """An ingredient required for crafting."""
    item_id: EntityId
    quantity: int
    is_consumed: bool  # True if item is consumed during crafting
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")


@dataclass
class CraftingRecipe:
    """
    CraftingRecipe entity for item crafting.
    
    Invariants:
    - Must have at least one ingredient
    - Must produce at least one item
    - Crafting time must be non-negative
    - Success rate must be between 0-100 (None for guaranteed)
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: str
    ingredients: List[RecipeIngredient]  # Items required for crafting
    result_item_id: EntityId  # Item produced by this recipe
    result_quantity: int  # Quantity produced
    crafting_time_seconds: int  # Time required to craft
    success_rate: Optional[int]  # Success rate percentage (None = 100%)
    difficulty: RecipeDifficulty
    skill_requirement: Optional[EntityId]  # Required skill entity
    skill_level_requirement: Optional[int]  # Minimum skill level
    required_workstation_id: Optional[EntityId]  # Required workstation/location
    is_discoverable: bool  # Can be discovered by players
    is_locked: bool  # Requires unlocking
    
    # Economic factors
    gold_cost: int  # Gold required for crafting
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Recipe name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Recipe name must be <= 255 characters")
        
        if not self.ingredients or len(self.ingredients) == 0:
            raise ValueError("Recipe must have at least one ingredient")
        
        if self.result_quantity <= 0:
            raise ValueError("Result quantity must be positive")
        
        if self.crafting_time_seconds < 0:
            raise ValueError("Crafting time cannot be negative")
        
        if self.success_rate is not None and (self.success_rate < 0 or self.success_rate > 100):
            raise ValueError("Success rate must be between 0-100")
        
        if self.skill_level_requirement is not None and self.skill_level_requirement <= 0:
            raise ValueError("Skill level requirement must be positive")
        
        if self.gold_cost < 0:
            raise ValueError("Gold cost cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: str,
        ingredients: List[RecipeIngredient],
        result_item_id: EntityId,
        result_quantity: int = 1,
        crafting_time_seconds: int = 0,
        success_rate: Optional[int] = None,
        difficulty: RecipeDifficulty = RecipeDifficulty.NORMAL,
        skill_requirement: Optional[EntityId] = None,
        skill_level_requirement: Optional[int] = None,
        required_workstation_id: Optional[EntityId] = None,
        is_discoverable: bool = True,
        is_locked: bool = False,
        gold_cost: int = 0,
    ) -> 'CraftingRecipe':
        """
        Factory method for creating a new CraftingRecipe.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            ingredients=ingredients,
            result_item_id=result_item_id,
            result_quantity=result_quantity,
            crafting_time_seconds=crafting_time_seconds,
            success_rate=success_rate,
            difficulty=difficulty,
            skill_requirement=skill_requirement,
            skill_level_requirement=skill_level_requirement,
            required_workstation_id=required_workstation_id,
            is_discoverable=is_discoverable,
            is_locked=is_locked,
            gold_cost=gold_cost,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def can_craft(self, inventory_items: Dict[EntityId, int], gold: int, skill_level: Optional[int] = None) -> bool:
        """
        Check if crafting is possible with given resources.
        
        Args:
            inventory_items: Mapping of item_id -> quantity in inventory
            gold: Available gold
            skill_level: Current skill level (if skill requirement exists)
        
        Returns:
            True if crafting is possible.
        """
        # Check gold cost
        if gold < self.gold_cost:
            return False
        
        # Check skill requirement
        if self.skill_level_requirement is not None:
            if skill_level is None or skill_level < self.skill_level_requirement:
                return False
        
        # Check ingredients
        for ingredient in self.ingredients:
            if ingredient.item_id not in inventory_items:
                return False
            if inventory_items[ingredient.item_id] < ingredient.quantity:
                return False
        
        return True
    
    def calculate_success_chance(self, skill_level: Optional[int] = None) -> float:
        """
        Calculate actual success chance based on skill level.
        
        Higher skill levels can increase success chance for difficult recipes.
        """
        base_chance = self.success_rate if self.success_rate is not None else 100.0
        
        if self.skill_level_requirement is None or skill_level is None:
            return base_chance
        
        # Bonus for exceeding skill requirement
        if skill_level > self.skill_level_requirement:
            level_diff = skill_level - self.skill_level_requirement
            bonus = min(level_diff * 2, 10)  # Max 10% bonus
            return min(base_chance + bonus, 100.0)
        
        # Penalty for being below requirement
        if skill_level < self.skill_level_requirement:
            penalty = (self.skill_level_requirement - skill_level) * 5
            return max(base_chance - penalty, 0.0)
        
        return base_chance
    
    def add_ingredient(self, ingredient: RecipeIngredient) -> None:
        """Add an ingredient to the recipe."""
        # Check if ingredient already exists (merge quantities)
        for existing in self.ingredients:
            if existing.item_id == ingredient.item_id:
                object.__setattr__(existing, 'quantity', existing.quantity + ingredient.quantity)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return
        
        # Add new ingredient
        self.ingredients.append(ingredient)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_ingredient(self, item_id: EntityId) -> bool:
        """
        Remove an ingredient from the recipe.
        
        Returns:
            True if ingredient was removed, False if not found.
        """
        for i, ingredient in enumerate(self.ingredients):
            if ingredient.item_id == item_id:
                self.ingredients.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def update_ingredient_quantity(self, item_id: EntityId, new_quantity: int) -> bool:
        """
        Update the quantity of an ingredient.
        
        Returns:
            True if ingredient was updated, False if not found.
        """
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        for ingredient in self.ingredients:
            if ingredient.item_id == item_id:
                object.__setattr__(ingredient, 'quantity', new_quantity)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def set_result_item(self, item_id: EntityId, quantity: int = 1) -> None:
        """Change the result item and quantity."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        object.__setattr__(self, 'result_item_id', item_id)
        object.__setattr__(self, 'result_quantity', quantity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_crafting_time(self, seconds: int) -> None:
        """Set the crafting time."""
        if seconds < 0:
            raise ValueError("Crafting time cannot be negative")
        
        object.__setattr__(self, 'crafting_time_seconds', seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_success_rate(self, rate: Optional[int]) -> None:
        """Set the success rate (None for guaranteed)."""
        if rate is not None and (rate < 0 or rate > 100):
            raise ValueError("Success rate must be between 0-100")
        
        object.__setattr__(self, 'success_rate', rate)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_gold_cost(self, cost: int) -> None:
        """Set the gold cost."""
        if cost < 0:
            raise ValueError("Gold cost cannot be negative")
        
        object.__setattr__(self, 'gold_cost', cost)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unlock(self) -> None:
        """Unlock the recipe."""
        if not self.is_locked:
            return
        
        object.__setattr__(self, 'is_locked', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def lock(self) -> None:
        """Lock the recipe."""
        if self.is_locked:
            return
        
        object.__setattr__(self, 'is_locked', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        success_str = f" ({self.success_rate}%)" if self.success_rate else ""
        return f"CraftingRecipe({self.name}, {len(self.ingredients)} ingredients{success_str})"
    
    def __repr__(self) -> str:
        return (
            f"CraftingRecipe(id={self.id}, name='{self.name}', "
            f"result_item_id={self.result_item_id}, difficulty={self.difficulty})"
        )
