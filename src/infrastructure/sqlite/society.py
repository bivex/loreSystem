"""SQLite repositories for society, factions, and politics entities.

This module is a **backward-compatibility facade**. The monolithic
implementation has been split across several sub-modules in the same
package for better maintainability.
"""

from __future__ import annotations

# Re-export everything from sub-modules
from .society_factions import *  # noqa: F401,F403
from .society_politics import *  # noqa: F401,F403
from .society_social import *  # noqa: F401,F403
