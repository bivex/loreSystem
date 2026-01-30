# Use Case 1: Создание и управление сюжетной кампанией

## Описание
Создание и управление ветвляющейся сюжетной кампанией с несколькими концовками, зависящими от выборов игроков.

## Акёры
- **Narrative Designer**: Создаёт сюжет, диалоги, развязки
- **Quest Designer**: Интегрирует кампанию в систему квестов
- **Writer**: Пишет диалоги и лор-тексты
- **Sound Designer**: Добавляет музыкальные темы и озвучку

## Сценарий
Нарративный дизайнер хочет создать кампанию "War of Three Kingdoms" для RPG-игры с несколькими концовками:
1. **Good Ending**: Игрок объединяет все три королевства
2. **Evil Ending**: Игрок захватывает все королевства
3. **Neutral Ending**: Игрок остаётся нейтральным наблюдателем

## Предусловия
- Наличие трёх королевств (Kingdom entities)
- Наличие персонажей (Character entities)
- Наличие квестов (Quest entities)

## Постусловия
- Сюжетные ветви должны быть связанными с квестами
- Каждая концовка должна иметь уникальный reward
- Система ветвления должна быть прозрачной для игроков

## Пример кода

```python
from src.domain import (
    Campaign, Chapter, Episode, Act, Prologue, Epilogue,
    PlotBranch, Consequence, MoralChoice, Ending, AlternateReality,
    Campaign
)
from src.domain.value_objects import TenantId, EntityId, Description, Version

def create_war_of_three_kingdoms_campaign(tenant_id: TenantId, world_id: EntityId) -> Campaign:
    """
    Создаёт сюжетную кампанию "War of Three Kingdoms" с несколькими концовками.
    
    Parameters:
        tenant_id: ID тенанта
        world_id: ID мира
    
    Returns:
        Campaign: Созданная кампания
    """
    
    # 1. Создаём пролог
    prologue = Prologue.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="Prologue: Three Kingdoms United",
        description="Long ago, three kingdoms lived in harmony...",
        is_skippable=True
    )
    
    # 2. Создаём три основные главы (по одной на каждое королевство)
    chapter_1 = Chapter.create(
        tenant_id=tenant_id,
        campaign_id=prologue.id,
        name="Chapter 1: Alliance of Silver",
        type="main",
        number=1
    )
    
    chapter_2 = Chapter.create(
        tenant_id=tenant_id,
        campaign_id=prologue.id,
        name="Chapter 2: Shadow War",
        type="main",
        number=2
    )
    
    chapter_3 = Chapter.create(
        tenant_id=tenant_id,
        campaign_id=prologue.id,
        name="Chapter 3: Final Confrontation",
        type="main",
        number=3
    )
    
    # 3. Создаём финальный акт (выбор концовки)
    final_act = Act.create(
        tenant_id=tenant_id,
        chapter_id=chapter_3.id,
        name="Act 3: The Choice",
        description="Игрок выбирает судьбу трёх королевств",
        is_cinematic=True  # Это катсцена для выбора концовки
    )
    
    # 4. Создаём три концовки
    good_ending = Ending.create(
        tenant_id=tenant_id,
        name="Good Ending: Three Kingdoms United",
        ending_type="good",
        description="Игрок объединяет все три королевства мирным путём",
        is_canon=False,
        rarity="common"
    )
    
    evil_ending = Ending.create(
        tenant_id=tenant_id,
        name="Evil Ending: Eternal Tyrant",
        ending_type="evil",
        description="Игрок захватывает все королевства силой",
        is_canon=False,
        rarity="rare"
    )
    
    neutral_ending = Ending.create(
        tenant_id=tenant_id,
        name="Neutral Ending: Silent Observer",
        ending_type="neutral",
        description="Игрок становится нейтральным наблюдателем конфликта",
        is_canon=False,
        rarity="uncommon"
    )
    
    # 5. Создаём кампанию
    campaign = Campaign.create(
        tenant_id=tenant_id,
        world_id=world_id,
        name="War of Three Kingdoms",
        description="Эпическая война между тремя королевствами",
        campaign_type="main_story",
        difficulty="medium",
        recommended_level_range=[10, 50],
        chapters=[chapter_1.id, chapter_2.id, chapter_3.id]
    )
    
    # 6. Настраиваем ветвление на основе концовок
    plot_branch_good = PlotBranch.create(
        tenant_id=tenant_id,
        campaign_id=campaign.id,
        branch_point_id=final_act.id,
        branch_type="choice",
        description="Игрок выбирает объединение королевств",
        condition_id=None,
        consequences=[good_ending.id]
    )
    
    plot_branch_evil = PlotBranch.create(
        tenant_id=tenant_id,
        campaign_id=campaign.id,
        branch_point_id=final_act.id,
        branch_type="choice",
        description="Игрок выбирает захват королевств",
        condition_id=None,
        consequences=[evil_ending.id]
    )
    
    plot_branch_neutral = PlotBranch.create(
        tenant_id=tenant_id,
        campaign_id=campaign.id,
        branch_point_id=final_act.id,
        branch_type="choice",
        description="Игрок выбирает нейтралитет",
        condition_id=None,
        consequences=[neutral_ending.id]
    )
    
    # 7. Добавляем ветвления к кампании
    campaign.add_plot_branch(plot_branch_good)
    campaign.add_plot_branch(plot_branch_evil)
    campaign.add_plot_branch(plot_branch_neutral)
    
    # 8. Добавляем моральный выбор в финальном акте
    moral_choice = MoralChoice.create(
        tenant_id=tenant_id,
        world_id=world_id,
        prompt="Как вы разрешите конфликт королевств?",
        description="Выбор определит концовку кампании",
        options=[
            {"id": "good", "text": "Объединить королевства", "alignment": "good"},
            {"id": "evil", "text": "Захватить силой", "alignment": "evil"},
            {"id": "neutral", "text": "Остаться наблюдателем", "alignment": "neutral"}
        ],
        choice_alignment=MoralChoice.Neutral,
        urgency=MoralChoice.LOW,
        consequence_ids=[good_ending.id, evil_ending.id, neutral_ending.id]
    )
    
    # 9. Создаём эпилог для каждой концовки
    good_epilogue = Epilogue.create(
        tenant_id=tenant_id,
        ending_id=good_ending.id,
        name="Epilogue: New Era",
        description="Начинается новая эра сотрудничества",
        display_time_minutes=5
    )
    
    evil_epilogue = Epilogue.create(
        tenant_id=tenant_id,
        ending_id=evil_ending.id,
        name="Epilogue: Tyrant's Reign",
        description="Ты правишь миром железной рукой",
        display_time_minutes=5
    )
    
    neutral_epilogue = Epilogue.create(
        tenant_id=tenant_id,
        ending_id=neutral_ending.id,
        name="Epilogue: Silent Witness",
        description="История запишется хрониками",
        display_time_minutes=3
    )
    
    # 10. Соединяем эпилоги с концовками
    good_ending.set_epilogue_id(good_epilogue.id)
    evil_ending.set_epilogue_id(evil_epilogue.id)
    neutral_ending.set_epilogue_id(neutral_epilogue.id)
    
    return campaign

# Пример использования
if __name__ == "__main__":
    from src.domain.value_objects import TenantId
    
    tenant_id = TenantId("tenant_001")
    world_id = EntityId("world_001")
    
    # Создаём кампанию
    campaign = create_war_of_three_kingdoms_campaign(tenant_id, world_id)
    
    # Получаем статистику
    print(f"✅ Кампания создана: {campaign.name}")
    print(f"📚 Главы: {len(campaign.chapters)}")
    print(f"🎬 Концовки: {len([e for e in [good_ending, evil_ending, neutral_ending] if e.ending_type != ''])}")
    print(f"📊 Ветвления: {len(campaign.plot_branches)}")
    print(f"⏱️ Примерное время прохождения: {campaign.estimated_playtime_hours} часов")
```

## Альтернативные потоки
1. **Fast Track**: Создать кампанию без сложного ветвления (одна концовка)
2. **Modular**: Создать каждую главу как отдельную кампанию
3. **Player-Driven**: Концовки зависят от репутации игрока (Reputation entity)

## Интеграция с другими системами
- **Quest System**: Главы кампании связаны с QuestChain
- **Sound System**: Каждая глава имеет Theme и Motif
- **Achievement System**: Концовки открывают достижения (Achievement, Trophy)

## Метрики успеха
- **Engagement Rate**: % игроков, прошедших до финальной концовки
- **Completion Time**: Среднее время прохождения кампании
- **Branch Distribution**: % игроков, выбравших каждую концовку
- **Replayability**: % игроков, прошедших кампанию второй раз

## Заключение
Этот Use Case демонстрирует ключевые возможности AAA-геймдев лор-системы:
- Сложное ветвление сюжета с моральными выборами
- Несколько концовок разной редкости
- Катсцены и эпилоги для кинематографического повествования
- Полная интеграция с Quest, Sound и Achievement системами
