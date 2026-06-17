"""Aggregate PersistenceMixin: composes domain-specific persistence sub-mixins.

Auto-split during the second-pass decomposition. The original monolithic
``PersistenceMixin`` (5,122 lines, 41 methods) is now distributed across
six domain sub-mixins:

* :class:`EnginePersistenceMixin` - transaction scope, persist orchestrators,
  canonical context, registry wiring, row helpers, the two giant
  ``_persist_*_unbatched`` methods that fan out across every domain.
* :class:`NarrativePersistenceMixin` - campaign/story/act/chapter/episode/storyline
  save-or-merge logic.
* :class:`CharacterPersistenceMixin` - character/event/relationship generation
  and persistence, semantic candidate lookup.
* :class:`QuestPersistenceMixin` - quest/chain/tracker save-or-merge.
* :class:`ItemPersistenceMixin` - item/inventory save-or-merge.
* :class:`WorldPersistenceMixin` - seasonal events, wars, artifact sets, relics.

All sub-mixins are composed here so :class:`RumorBridgeService` keeps
working with a single ``PersistenceMixin`` base. Cross-domain ``self.``
calls resolve through MRO.
"""

from __future__ import annotations

from src.application.integration.camel_bridge.mixins.persistence_characters import (
    CharacterPersistenceMixin,
)
from src.application.integration.camel_bridge.mixins.persistence_engine import (
    EnginePersistenceMixin,
)
from src.application.integration.camel_bridge.mixins.persistence_items import (
    ItemPersistenceMixin,
)
from src.application.integration.camel_bridge.mixins.persistence_narrative_structure import (
    NarrativePersistenceMixin,
)
from src.application.integration.camel_bridge.mixins.persistence_quests import (
    QuestPersistenceMixin,
)
from src.application.integration.camel_bridge.mixins.persistence_world import (
    WorldPersistenceMixin,
)


class PersistenceMixin(
    EnginePersistenceMixin,
    NarrativePersistenceMixin,
    CharacterPersistenceMixin,
    QuestPersistenceMixin,
    ItemPersistenceMixin,
    WorldPersistenceMixin,
):
    """Aggregate mixin composing all persistence sub-domains.

    No methods live here directly; see the six sub-mixins listed above.
    """


__all__ = ["PersistenceMixin"]
