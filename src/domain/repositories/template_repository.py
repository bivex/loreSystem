"""
Template Repository Interface

Port for persisting and retrieving Template entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.template import Template
from ..value_objects.common import TenantId, EntityId, TemplateName, TemplateType


class ITemplateRepository(ABC):
    """
    Repository interface for Template entity.
    
    Templates belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, template: Template) -> Template:
        """
        Save a template (insert or update).
        
        Args:
            template: Template to save
        
        Returns:
            Saved template with ID populated
        
        Raises:
            DuplicateEntity: If template name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world/parent doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        template_id: EntityId,
    ) -> Optional[Template]:
        """Find template by ID."""
        pass
    
    @abstractmethod
    def find_by_name(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: TemplateName,
    ) -> Optional[Template]:
        """
        Find template by name within a specific world.
        
        Template names are unique per world, not globally.
        """
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Template]:
        """List all templates in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_type(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        template_type: TemplateType,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Template]:
        """List templates by type within a world."""
        pass
    
    @abstractmethod
    def list_runes(
        self,
        tenant_id: TenantId,
        parent_template_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Template]:
        """List all runes (sub-templates) for a parent template."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        template_id: EntityId,
    ) -> bool:
        """
        Delete a template.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: TemplateName,
    ) -> bool:
        """Check if template with name exists in world."""
        pass