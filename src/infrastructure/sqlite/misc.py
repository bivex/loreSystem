"""SQLite repositories for miscellaneous game-system entities.

This module is a **backward-compatibility facade**. The monolithic
implementation has been split across semantic sub-modules for better
maintainability.
"""

from __future__ import annotations

# Re-export everything from semantic sub-modules
from .misc_science import *  # noqa: F401,F403
from .misc_geography import *  # noqa: F401,F403
from .misc_media import *  # noqa: F401,F403
from .misc_audio_visual import *  # noqa: F401,F403
from .misc_knowledge import *  # noqa: F401,F403
from .misc_faith import *  # noqa: F401,F403
from .misc_biology import *  # noqa: F401,F403
from .misc_travel import *  # noqa: F401,F403
from .misc_gameplay import *  # noqa: F401,F403
from .misc_narrative_extra import *  # noqa: F401,F403
from .misc_warfare import *  # noqa: F401,F403
from .misc_social_extra import *  # noqa: F401,F403
from .misc_economy_extra import *  # noqa: F401,F403
from .misc_technical import *  # noqa: F401,F403
from .misc_other import *  # noqa: F401,F403
