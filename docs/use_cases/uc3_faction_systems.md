# Use Case 3: Создание и управление системами фракций и репутации

## Описание
Создание и управление сложными фракциями, их иерархией, идеологиями и системами репутации, влияющими на игроков и мир в целом.

## Акёры
- **Narrative Designer**: Создаёт сюжетные линии для фракционных конфликтов
- **Quest Designer**: Интегрирует фракции в квесты и миссии
- **Game Designer**: Балансирует фракционные бонусы и штрафы

## Сценарий
Нарративный дизайнер хочет создать фракционную систему "Order vs Chaos" для RPG-игры:
1. Две основные фракции: Order (законность) и Chaos (анархия)
2. Каждая фракция имеет иерархию лидеров (FactionLeader)
3. Система идеологий и рейтингов влияния (FactionIdeology)
4. Система репутации и кармы (Reputation, Karma)
5. Договоры и союзы между фракциями (Treaty, Alliance)

## Предусловия
- Наличие мира (World entity)
- Наличие персонажей (Character entities)
- Наличие квестов (Quest entities)

## Постусловия
- Фракции должны влиять на репутацию игроков
- Лидеры фракций должны иметь диалоги (VoiceLine)
- Фракции должны иметь территории (FactionTerritory)

## Пример кода

```python
from src.domain import (
    Faction, FactionHierarchy, FactionIdeology, FactionLeader,
    Reputation, Karma, Honor, Treaty, Alliance,
    Character, Location
)
from src.domain.value_objects import TenantId, EntityId, Version, Timestamp

def create_order_vs_chaos_factions(tenant_id: TenantId, world_id: EntityId) -> tuple[Faction, Faction]:
    """
    Создаёт две противостоящие фракции "Order vs Chaos" для RPG-игры.
    
    Parameters:
        tenant_id: ID тенанта
        world_id: ID мира
    
    Returns:
        Кортеж из двух фракций (order_faction, chaos_faction)
    """
    
    # 1. Создаём фракцию Order (законность)
    order_ideology = FactionIdeology.create(
        tenant_id=tenant_id,
        name="Lawful Order",
        description="Фракция, верящая в законы и порядок",
        ideology_type="lawful_good",
        core_values=["порядок", "закон", "справедливость"],
        is_player_joinable=True
    )
    
    order_faction = Faction.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Order of the Silver Hand",
        description="Древний орден, посвящённый поддержанию закона и порядка",
        ideology_id=order_ideology.id,
        alignment="lawful_good",
        is_player_joinable=True,
        territories=[],
        relations={
            "chaos": "hostile",
            "neutral": "neutral"
        }
    )
    
    # 2. Создаём иерархию лидеров для Order
    order_leader = FactionLeader.create(
        tenant_id=tenant_id,
        faction_id=order_faction.id,
        name="Grand Commander Aethelgard",
        description="Мудрый стратег, правивший орденом 500 лет",
        title="Grand Commander",
        is_active=True
    )
    
    order_hierarchy = FactionHierarchy.create(
        tenant_id=tenant_id,
        faction_id=order_faction.id,
        name="Order Hierarchy",
        hierarchy_type="military",
        levels=[
            {"level": 1, "title": "Recruit", "count": 10000},
            {"level": 2, "title": "Soldier", "count": 5000},
            {"level": 3, "title": "Captain", "count": 500},
            {"level": 4, "title": "Commander", "count": 50}
        ]
    )
    
    # 3. Создаём фракцию Chaos (анархия)
    chaos_ideology = FactionIdeology.create(
        tenant_id=tenant_id,
        name="Chaotic Liberation",
        description="Фракция, стремящаяся к свободе через разрушение порядка",
        ideology_type="chaotic_neutral",
        core_values=["свобода", "анархия", "личная свобода"],
        is_player_joinable=True
    )
    
    chaos_faction = Faction.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Chaos of the Broken Chain",
        description="Повстанцы и анархисты, разрушающие старый порядок",
        ideology_id=chaos_ideology.id,
        alignment="chaotic_neutral",
        is_player_joinable=True,
        territories=[],
        relations={
            "order": "hostile",
            "neutral": "neutral"
        }
    )
    
    # 4. Создаём иерархию для Chaos
    chaos_leader = FactionLeader.create(
        tenant_id=tenant_id,
        faction_id=chaos_faction.id,
        name="Warlord Vex",
        description="Безжалостный полководец, ведущий разрушительные рейды",
        title="Warlord",
        is_active=True
    )
    
    chaos_hierarchy = FactionHierarchy.create(
        tenant_id=tenant_id,
        faction_id=chaos_faction.id,
        name="Chaos Hierarchy",
        hierarchy_type="tribal",
        levels=[
            {"level": 1, "title": "Outlaw", "count": 5000},
            {"level": 2, "title": "Bandit", "count": 2000},
            {"level": 3, "title": "Warlord", "count": 200}
        ]
    )
    
    # 5. Настраиваем иерархии для фракций
    order_faction.set_leader_id(order_leader.id)
    order_faction.set_hierarchy_id(order_hierarchy.id)
    order_faction.set_faction_resource_id(None)  # Ресурсы у фракции
    
    chaos_faction.set_leader_id(chaos_leader.id)
    chaos_faction.set_hierarchy_id(chaos_hierarchy.id)
    chaos_faction.set_faction_resource_id(None)
    
    # 6. Создаём территории для фракций
    order_territory = Location.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Capital of Order",
        description="Главный город Ордена Серебряной Руки",
        location_type="city",
        is_faction_hq=True,
        faction_id=order_faction.id
    )
    
    chaos_territory = Location.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Chaos Camp",
        description="База повстанцев в тёмном лесу",
        location_type="camp",
        is_faction_hq=True,
        faction_id=chaos_faction.id
    )
    
    # 7. Связываем территории с фракциями
    order_faction.add_territory(order_territory.id)
    chaos_faction.add_territory(chaos_territory.id)
    
    # 8. Создаём систему репутации
    reputation = Reputation.create(
        tenant_id=tenant_id,
        player_id=EntityId("player_hero"),
        faction_id=order_faction.id,
        score=100,
        tier="revered"
    )
    
    # 9. Создаём договор между фракциями
    treaty = Treaty.create(
        tenant_id=tenant_id,
        name="Temporary Truce",
        description="Временное перемирие между Орденом и Повстанцами",
        faction_a_id=order_faction.id,
        faction_b_id=chaos_faction.id,
        treaty_type="peace",
        duration_days=30,
        is_active=True
    )
    
    # 10. Создаём союз (альянс) для Order
    alliance = Alliance.create(
        tenant_id=tenant_id,
        name="Silver League",
        description="Союз королевств и фракций, поддерживающих Орден",
        leader_faction_id=order_faction.id,
        type="military"
    )
    
    # 11. Настраиваем отношения фракций
    order_faction.add_alliance_id(alliance.id)
    order_faction.add_treaty_id(treaty.id)
    order_faction.update_relations("chaos", "hostile")
    
    chaos_faction.add_relation("order", "hostile")
    
    # 12. Создаём квест для фракционной войны
    from src.domain import QuestChain, QuestNode, QuestObjective
    
    faction_quest_chain = QuestChain.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Faction War: Order vs Chaos",
        campaign_type="faction_conflict",
        difficulty="hard",
        estimated_playtime_hours=20
    )
    
    main_quest = QuestNode.create(
        tenant_id=tenant_id,
        parent_chain_id=faction_quest_chain.id,
        name="Choose Your Side",
        quest_type="choice",
        difficulty="medium",
        quest_giver_id=order_faction.id,
        is_repeatable=False,
        description="Вступай в Орден или Повстанцы"
    )
    
    order_quest = QuestNode.create(
        tenant_id=tenant_id,
        parent_chain_id=faction_quest_chain.id,
        name="Defend Order Stronghold",
        quest_type="main",
        difficulty="hard",
        quest_giver_id=order_faction.id,
        is_repeatable=False,
        description="Защити цитадель Ордена от повстанцев"
    )
    
    chaos_quest = QuestNode.create(
        tenant_id=tenant_id,
        parent_chain_id=faction_quest_chain.id,
        name="Raid Order Supply Lines",
        quest_type="main",
        difficulty="medium",
        quest_giver_id=chaos_faction.id,
        is_repeatable=True,
        description="Нападь на транспортные линии Ордена"
    )
    
    # 13. Создаём систему чести для репутации
    honor = Honor.create(
        tenant_id=tenant_id,
        player_id=EntityId("player_hero"),
        faction_id=order_faction.id,
        title="Knight of the Order",
        description="Получил звание Рыцаря за защиту Ордена"
        points=100
    )
    
    # 14. Создаём систему кармы
    karma = Karma.create(
        tenant_id=tenant_id,
        player_id=EntityId("player_hero"),
        score=100,  # Нейтральное на старте
        total_karma=1000
    )
    
    # 15. Интегрируем квесты в кампанию
    faction_quest_chain.add_quest(main_quest)
    faction_quest_chain.add_quest(order_quest)
    faction_quest_chain.add_quest(chaos_quest)
    
    return order_faction, chaos_faction

# Пример использования
if __name__ == "__main__":
    from src.domain.value_objects import TenantId, EntityId
    
    tenant_id = TenantId("tenant_001")
    world_id = EntityId("world_001")
    
    # Создаём фракции
    order_faction, chaos_faction = create_order_vs_chaos_factions(tenant_id, world_id)
    
    print(f"✅ Фракция Order создана: {order_faction.name}")
    print(f"✅ Фракция Chaos создана: {chaos_faction.name}")
    print(f"📊 Количество членов: {order_faction.get_member_count()} (Order) vs {chaos_faction.get_member_count()} (Chaos)")
    print(f"🎯 Репутация: {order_faction.get_alignment()}")
    print(f"📈 Иерархия: {order_faction.get_hierarchy_levels()}")
```

## Альтернативные потоки
1. **Neutral Factions**: Создание нейтральных фракций (торговые гильдии, ученые круги)
2. **Multi-Faction Alliances**: Создание крупных альянсов из нескольких фракций
3. **Faction Reputation Systems**: Сложные системы репутации с рейтинговыми таблицами

## Интеграция с другими системами
- **Quest System**: QuestChain, QuestNode, QuestObjective
- **Location System**: Location, FactionTerritory
- **Character System**: Character, VoiceLine (для диалогов лидеров)
- **Progression**: Experience (награды за фракционные миссии)

## Метрики успеха
- **Faction Engagement Rate**: % игроков, вступивших во фракции
- **Faction Balance**: Насколько сбалансированы силы фракций (метрический анализ)
- **War Participation**: % игроков, участвовавших в войнах фракций
- **Diplomatic Success Rate**: Успешность дипломатии (договоры, союзы)

## Заключение
Этот Use Case демонстрирует создание сложной фракционной системы для AAA-игр:
- Несколько фракций с различными идеологиями
- Иерархии лидеров и структуры
- Системы репутации и кармы
- Территории и ресурсы фракций
- Дипломатия (договоры, союзы)
- Фракционные квесты и миссии
- Интеграция с существующими системами (Quests, Locations, Characters)
