"""Aggregate ParsersMixin: composes domain-specific parser sub-mixins.

Auto-split during the second-pass decomposition. The original monolithic
``ParsersMixin`` (5,380 lines, 202 methods) is now distributed across
eight domain sub-mixins, each holding the parsing/coercion logic for one
entity family:

* :class:`NarrativeParserMixin` - narrative structure, rumors, events, relationships.
* :class:`CharacterParserMixin` - characters, evolution, variants, voice/mocap, affinity.
* :class:`QuestParserMixin` - quests, chains, nodes, objectives, prerequisites.
* :class:`ItemParserMixin` - items, components, sockets, inventory, materials, recipes.
* :class:`ProgressionParserMixin` - skills, perks, traits, talent trees, achievements.
* :class:`WorldParserMixin` - dungeons, raids, arenas, instances, world events.
* :class:`ChoiceParserMixin` - plot branches, choices, consequences, moral choices.
* :class:`CoerceParserMixin` - low-level payload/enum coercion utilities.

All sub-mixins are composed here so :class:`RumorBridgeService` keeps
working with a single ``ParsersMixin`` base. Cross-domain ``self.``
calls (e.g. a quest builder calling ``self._coerce_text_tuple`` from the
coerce utils) resolve through MRO.
"""

from __future__ import annotations

from src.application.integration.camel_bridge.mixins.parsers_characters import (
    CharacterParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_choices_branches import (
    ChoiceParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_coerce_utils import (
    CoerceParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_items import (
    ItemParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_narrative_structure import (
    NarrativeParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_progression import (
    ProgressionParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_quests import (
    QuestParserMixin,
)
from src.application.integration.camel_bridge.mixins.parsers_world import (
    WorldParserMixin,
)


class ParsersMixin(
    NarrativeParserMixin,
    CharacterParserMixin,
    QuestParserMixin,
    ItemParserMixin,
    ProgressionParserMixin,
    WorldParserMixin,
    ChoiceParserMixin,
    CoerceParserMixin,
):
    """Aggregate mixin composing all parser sub-domains.

    No methods live here directly; see the eight sub-mixins listed above.
    """


__all__ = ["ParsersMixin"]
