"""SQLite repositories for miscellaneous game-system entities.

This module is a **backward-compatibility facade**. The monolithic
implementation has been split across several sub-modules in the same
package for better maintainability.
"""

from __future__ import annotations

# Re-export everything from sub-modules
from .misc_a_b import *  # noqa: F401,F403
from .misc_c_1 import *  # noqa: F401,F403
from .misc_c_2 import *  # noqa: F401,F403
from .misc_d_f import *  # noqa: F401,F403
from .misc_g_i import *  # noqa: F401,F403
from .misc_j_l import *  # noqa: F401,F403
from .misc_m_o import *  # noqa: F401,F403
from .misc_p_r import *  # noqa: F401,F403
from .misc_s_1 import *  # noqa: F401,F403
from .misc_s_2 import *  # noqa: F401,F403
from .misc_t_z import *  # noqa: F401,F403
