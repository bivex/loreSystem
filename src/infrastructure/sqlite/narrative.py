"""SQLite repositories for narrative/story/world/character entities.

This module is a **backward-compatibility facade**. The monolithic
implementation has been split across several sub-modules in the same
package for better maintainability.
"""

from __future__ import annotations

# Re-export everything from sub-modules
from .narrative_core import *  # noqa: F401,F403
from .narrative_characters import *  # noqa: F401,F403
from .narrative_events import *  # noqa: F401,F403
from .narrative_meta import *  # noqa: F401,F403
