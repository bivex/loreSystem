"""
GUI Tab Modules

Separate tab classes for better organization and maintainability.
"""

from .pages_tab import PagesTab
from .templates_tab import TemplatesTab
from .stories_tab import StoriesTab
from .tags_tab import TagsTab
from .images_tab import ImagesTab
from .choice_tab import ChoiceTab
from .flowchart_tab import FlowchartTab
from .handout_tab import HandoutTab
from .inspiration_tab import InspirationTab
from .map_tab import MapTab
from .note_tab import NoteTab
from .requirement_tab import RequirementTab
from .session_tab import SessionTab
from .tokenboard_tab import TokenboardTab

__all__ = [
    'PagesTab',
    'TemplatesTab',
    'StoriesTab',
    'TagsTab',
    'ImagesTab',
    'ChoiceTab',
    'FlowchartTab',
    'HandoutTab',
    'InspirationTab',
    'MapTab',
    'NoteTab',
    'RequirementTab',
    'SessionTab',
    'TokenboardTab',
]
