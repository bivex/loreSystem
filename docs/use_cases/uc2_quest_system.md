# Use Case 2: Создание и управление квестовыми системами

## Описание
Создание и управление сложными цепочками квестов с пререквизитами, вознаграждениями и отслеживанием прогресса игроков.

## Акёры
- **Quest Designer**: Создаёт структуру квестов и цепочки
- **Technical Writer**: Пишет тексты квестов и описания
- **QA Engineer**: Проверяет логику квестов и наград
- **Game Designer**: Балансирует сложность и вознаграждения

## Сценарий
Нарративный дизайнер хочет создать квест "Ancient Artifact Recovery" для RPG-игры с несколькими этапами:
1. Игрок находит древний свиток (объект)
2. Игрок приносит свиток археологу (NPC)
3. Археолог переводит свиток (перевод)
4. Игрок получает вознаграждение (артефакт)
5. Открывается новая область для исследования (локация)

## Предусловия
- Наличие NPC (QuestGiver)
- Наличие артефакта (Item)
- Наличие локации (Location)
- Наличие опыта (Experience)

## Постусловия
- Квест должен быть связан с кампанией (Campaign)
- Прогресс квеста должен быть отслеживаем (QuestTracker)
- Вознаграждения должны быть выданы только после выполнения

## Пример кода

```python
from src.domain import (
    QuestChain, QuestNode, QuestPrerequisite, QuestObjective,
    QuestGiver, QuestTracker, QuestRewardTier,
    Campaign, Location, Item, Experience
)
from src.domain.value_objects import TenantId, EntityId, Description, Version, Timestamp

def create_ancient_artifact_quest(tenant_id: TenantId, world_id: EntityId, campaign_id: EntityId) -> QuestChain:
    """
    Создаёт сложную цепочку квестов "Ancient Artifact Recovery".
    """
    
    # 1. Создаём квестового раздающего (археолог)
    quest_giver = QuestGiver.create(
        tenant_id=tenant_id,
        name="Dr. Elena Vance",
        location_id=EntityId("location_ruins_of_kingdom"),
        dialogue="Магистр! Я нашла древний свиток..."
    )
    
    # 2. Создаём основной квест (находка свитка)
    main_quest = QuestNode.create(
        tenant_id=tenant_id,
        name="Find the Ancient Artifact",
        description="Dr. Vance discovered an artifact in the Ruins. Retrieve it.",
        quest_type="main",
        difficulty="hard",
        quest_giver_id=quest_giver.id,
        chain_id=quest_giver.id,
        is_repeatable=False,
        estimated_time_minutes=60
    )
    
    # 3. Создаём этапы квеста (квестовые задачи)
    objective_1 = QuestObjective.create(
        tenant_id=tenant_id,
        quest_node_id=main_quest.id,
        description="Find the artifact in the Ruins",
        objective_type="interaction",
        target_entity_id=EntityId("location_ruins"),
        is_required=True
    )
    
    objective_2 = QuestObjective.create(
        tenant_id=tenant_id,
        quest_node_id=main_quest.id,
        description="Bring the artifact to Dr. Vance",
        objective_type="item_delivery",
        target_entity_id=quest_giver.id,
        target_item_id=EntityId("item_ancient_artifact"),
        is_required=True
    )
    
    # 4. Создаём вознаграждения за квест
    reward_tier = QuestRewardTier.create(
        tenant_id=tenant_id,
        name="Ancient Artifact Rewards",
        tier=2,
        reward_ids=[EntityId("xp_1000"), EntityId("item_scarab_amulet")]
    )
    
    # 5. Создаём пререквизиты для квеста
    prerequisite = QuestPrerequisite.create(
        tenant_id=tenant_id,
        quest_node_id=main_quest.id,
        requirement_type="level",
        value=30,
        description="Requires level 30 to access Ruins"
    )
    
    # 6. Создаём связку с кампанией
    campaign = CampaignRepository.get(campaign_id)
    
    # 7. Создаём цепочку квестов
    quest_chain = QuestChain.create(
        tenant_id=tenant_id,
        name="Ancient Artifact Recovery",
        campaign_id=campaign_id,
        difficulty="hard",
        estimated_playtime_hours=4,
        quest_giver_id=quest_giver.id,
        quests=[main_quest.id]
    )
    
    # 8. Настраиваем вознаграждения для квеста
    main_quest.set_reward_tier_id(reward_tier.id)
    main_quest.set_experience_reward(1000)
    
    # 9. Добавляем вознаграждения (артефакт)
    artifact_item = Item.create(
        tenant_id=tenant_id,
        name="Ancient Scarab Amulet",
        description="Проклятый амулет древних жрецов",
        item_type="artifact",
        rarity="legendary"
    )
    
    # 10. Создаём квест для открытия новой области (эпилог)
    epilogue_quest = QuestNode.create(
        tenant_id=tenant_id,
        name="Explore the Discovered Ruins",
        description="В открытые руины скрываются новые тайны",
        quest_type="side",
        difficulty="medium",
        quest_giver_id=quest_giver.id,
        chain_id=quest_chain.id,
        is_repeatable=False,
        is_hidden=True
    )
    
    # 11. Добавляем эпилог в кампанию
    epilogue = Epilogue.create(
        tenant_id=tenant_id,
        name="Discovery Epilogue",
        description="Открытие древних руин меняет историю мира",
        ending_id=EndingRepository.get("ending_good").id
    )
    
    # 12. Создаём систему отслеживания прогресса
    quest_tracker = QuestTracker.create(
        tenant_id=tenant_id,
        player_id=EntityId("player_hero"),
        quest_chain_id=quest_chain.id,
        started_at=Timestamp.now(),
        completed_objectives=[],
        status="in_progress"
    )
    
    # 13. Добавляем побочные квесты (опционально)
    side_quest_1 = QuestNode.create(
        tenant_id=tenant_id,
        name="Defend the Ruins from Bandits",
        description="Бандиты пытаются захватить руины. Защити их.",
        quest_type="side",
        difficulty="medium",
        quest_giver_id=quest_giver.id,
        chain_id=quest_chain.id,
        is_repeatable=True,
        estimated_time_minutes=30
    )
    
    side_quest_2 = QuestNode.create(
        tenant_id=tenant_id,
        name="Translate the Artifact Text",
        description="Древний текст на амулете нужно перевести",
        quest_type="side",
        difficulty="easy",
        quest_giver_id=quest_giver.id,
        chain_id=quest_chain.id,
        is_repeatable=False,
        is_hidden=False,
        objectives=[QuestObjective.create(...)]  # Перевод текста
    )
    
    # 14. Финальная сборка квестовой цепочки
    quest_chain.add_quest(side_quest_1)
    quest_chain.add_quest(side_quest_2)
    quest_chain.set_epilogue_id(epilogue.id)
    
    # 15. Создаём секретный квест (Easter Egg)
    easter_egg = EasterEgg.create(
        tenant_id=tenant_id,
        name="Hidden Passage Behind Artifact",
        description="За амулетом скрывается секретный проход",
        condition="interact_with_item",
        secret_item_id=EntityId("item_secret_key")
    )
    
    # 16. Добавляем секрет в систему квестов
    side_quest_2.add_secret_reference(easter_egg.id)
    
    # 17. Связываем квестовую цепочку с кампанией
    campaign.add_quest_chain(quest_chain)
    
    # 18. Настраиваем автоматическое принятие квеста
    quest_chain.set_auto_acceptable(False)  # Игрок должен принять квест вручную
    
    # 19. Добавляем систему повторяемости
    quest_chain.set_cooldown_days(7)  # Квест можно проходить каждые 7 дней
    
    # 20. Создаём систему отзывов (отзывы на квест)
    quest_review = Quest.create(
        tenant_id=tenant_id,
        name="Quest Review: Ancient Artifact Recovery",
        description="Игроки могут оставить отзыв на этот квест",
        quest_type="system",
        review_enabled=True
    )
    
    return quest_chain

# Пример использования
if __name__ == "__main__":
    from src.domain.value_objects import TenantId, EntityId
    
    tenant_id = TenantId("tenant_001")
    world_id = EntityId("world_001")
    campaign_id = EntityId("campaign_001")
    
    # Создаём квестовую цепочку
    quest_chain = create_ancient_artifact_quest(tenant_id, world_id, campaign_id)
    
    # Получаем информацию
    print(f"✅ Квестовая цепочка создана: {quest_chain.name}")
    print(f"📚 Количество квестов: {len(quest_chain.quests)}")
    print(f"⏱️ Ожидаемое время: {quest_chain.estimated_playtime_hours} часов")
    print(f"🎯 Вознаграждения: {len([q.reward_tier_id for q in quest_chain.quests if q.reward_tier_id])}")
    print(f"🔒 Побочные квесты: {len([q for q in quest_chain.quests if q.is_side])}")
    print(f"🎬 Эпилог: {quest_chain.epilogue_id}")
```

## Метрики успеха
- **Quest Completion Rate**: % игроков, завершивших квестовую цепочку
- **Quest Abandonment Rate**: % игроков, бросивших квест
- **Average Quest Completion Time**: Среднее время завершения
- **Quest Difficulty Rating**: Оценка сложности игроками
- **Reward Satisfaction**: Оценка вознаграждений

## Интеграция с другими системами
- **Quest System**: QuestChain, QuestNode, QuestObjective, QuestPrerequisite
- **Reward System**: QuestRewardTier, Item
- **Experience System**: Experience
- **Achievement System**: Achievement (квестовый квест открывает достижение)

## Заключение
Этот Use Case демонстрирует создание сложной квестовой системы для AAA-игр:
- Многоступенчатые квесты с разными типами (main, side, system)
- Пререквизиты и условия выполнения
- Сложная система вознаграждений
- Интеграция с кампаниями и достижениями
- Отслеживание прогресса игроков
- Секретные квесты и пасхалки для продвинутых игроков
