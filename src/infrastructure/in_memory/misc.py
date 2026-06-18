"""In-memory repositories for miscellaneous game-system entities.

This module is a **backward-compatibility facade**. The monolithic
implementation has been split across several sub-modules in the same
package for better maintainability.
"""

from __future__ import annotations

# Re-export everything from sub-modules
from .misc_a_g import *  # noqa: F401,F403
from .misc_h_p import *  # noqa: F401,F403
from .misc_q_z import *  # noqa: F401,F403
