"""
GUI Tab Modules

Separate tab classes for better organization and maintainability.
"""

from .pages_tab import PagesTab
from .templates_tab import TemplatesTab
from .stories_tab import StoriesTab
from .tags_tab import TagsTab
from .images_tab import ImagesTab

__all__ = [
    'PagesTab',
    'TemplatesTab',
    'StoriesTab',
    'TagsTab',
    'ImagesTab',
]
