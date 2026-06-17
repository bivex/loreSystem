"""Mixin classes composing the ``RumorBridgeService`` behavior.

Extracted from the monolithic ``rumor_agents.py``. The five mixins split
the ~290 private methods of ``RumorBridgeService`` by responsibility:

* :class:`ParsersMixin`      - JSON parsing and payload coercion into Drafts.
* :class:`StabilizerMixin`   - narrative draft stabilization and partial-field merging.
* :class:`FallbacksMixin`    - deterministic fallback drafts for unusable LLM output.
* :class:`PromptsMixin`      - prompt construction, localization, memory context.
* :class:`PersistenceMixin`  - repository persistence with canonical merge.

All methods are kept on the mixins (rather than free functions) so that
the orchestrators in :class:`RumorBridgeService` can call them via
``self.`` after mixin composition - no call-site changes were required.
The mixins have no ``__init__`` of their own; state lives entirely on
``RumorBridgeService.__init__``.
"""

from __future__ import annotations

from src.application.integration.camel_bridge.mixins.fallbacks import FallbacksMixin
from src.application.integration.camel_bridge.mixins.parsers import ParsersMixin
from src.application.integration.camel_bridge.mixins.persistence import PersistenceMixin
from src.application.integration.camel_bridge.mixins.prompts import PromptsMixin
from src.application.integration.camel_bridge.mixins.stabilizer import StabilizerMixin

__all__ = [
    "FallbacksMixin",
    "ParsersMixin",
    "PersistenceMixin",
    "PromptsMixin",
    "StabilizerMixin",
]
