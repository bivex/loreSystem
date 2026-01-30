# Use Case 3: Валидация лор-данных

## Описание
Комплексная проверка целостности, согласованности и отсутствия ошибок в лор-данных (кампании, квесты, фракции, персонажи) перед импортом в игровые движки.

## Акёры
- **QA Engineer**: Разрабатывает тестовые сценарии и проверяет валидацию
- **Data Analyst**: Анализирует паттерны данных для улучшения качества
- **Technical Writer**: Документирует правила валидации

## Сценарии

### **Сценарий 1: Валидация кампании**
**Актёры:** QA Engineer, Technical Writer
**Действия:**
1. Проверяют целостность кампании (Campaign.validate())
2. Проверяют наличие всех глав (Chapter.validate())
3. Проверяют отсутствие циклических зависимостей в квестах (Quest.validate())
4. Валидируют временные линии (Timeline.validate())
5. Проверяют консистентность окончений с сюжетом

**Пример кода:**
```python
from src.domain import Campaign, Chapter, Timeline
from src.application.exceptions import ValidationError

def validate_campaign_for_export(campaign_id: str) -> list[str]:
    """Валидация кампании для экспорта."""
    errors = []
    
    campaign = CampaignRepository.get(campaign_id)
    
    try:
        campaign.validate()
    except ValidationError as e:
        errors.append(f"Кампания: {e.message}")
    
    # Проверяем главы
    for i, chapter in enumerate(campaign.chapters, 1):
        try:
            chapter.validate()
        except ValidationError as e:
            errors.append(f"Глава {i} ({chapter.name}): {e.message}")
    
    # Проверяем временные линии
    if campaign.timeline_id:
        timeline = TimelineRepository.get(campaign.timeline_id)
        try:
            timeline.validate()
        except ValidationError as e:
            errors.append(f"Временная линия: {e.message}")
    
    # Проверяем консистентность
    endings = [e for e in campaign.endings if e.is_canon]
    if len(endings) == 0:
        errors.append("Кампания должна иметь хотя бы одну канонную концовку")
    
    return errors
```

### **Сценарий 2: Валидация квестовой цепочки**
**Актёры:** Quest Designer, QA Engineer
**Действия:**
1. Проверяют правильную структуру цепочки (QuestChain.validate())
2. Проверяют наличие всех пререквизитов (QuestPrerequisite.validate())
3. Проверяют корректность наград (QuestRewardTier.validate())
4. Проверяют сбалансированность опыта (Experience.validate())
5. Проверяют логические связи между квестами

**Пример кода:**
```python
from src.domain import QuestChain, QuestNode, QuestPrerequisite, QuestRewardTier
from src.application.exceptions import ValidationError

def validate_quest_chain(quest_chain_id: str) -> list[str]:
    """Валидация квестовой цепочки."""
    errors = []
    
    quest_chain = QuestChainRepository.get(quest_chain_id)
    
    try:
        quest_chain.validate()
    except ValidationError as e:
        errors.append(f"Квестовая цепочка: {e.message}")
    
    # Проверяем пререквизиты
    for quest in quest_chain.quests:
        for prereq in quest.prerequisites:
            prereq_entity = QuestRepository.get(prereq.id)
            if not prereq_entity.is_required_by_default():
                errors.append(f"Квест '{quest.name}' требует '{prereq_entity.name}', который не является обязательным по умолчанию")
    
    # Проверяем награды
    for quest in quest_chain.quests:
        if quest.reward_tier_id:
            reward_tier = QuestRewardTierRepository.get(quest.reward_tier_id)
            if not reward_tier.is_balanced():
                errors.append(f"Квест '{quest.name}' имеет несбалансированный уровень наград {reward_tier.tier}")
    
    # Проверяем опыт
    total_xp_required = sum(quest.experience_reward for quest in quest_chain.quests)
    if total_xp_required > quest_chain.estimated_playtime_hours * 100:
        errors.append(f"Квестовая цепочка требует {total_xp_required} XP, но рассчитана на {quest_chain.estimated_playtime_hours} часов")
    
    return errors
```

### **Сценарий 3: Валидация фракционной системы**
**Актёры:** Game Designer, QA Engineer
**Действия:**
1. Проверяют целостность фракций (Faction.validate())
2. Проверяют иерархии (FactionHierarchy.validate())
3. Проверяют идейологии (FactionIdeology.validate())
4. Проверяют репутации и кармы (Reputation.validate(), Karma.validate())
5. Проверяют отношения между фракциями (Treaty.validate(), Alliance.validate())

**Пример кода:**
```python
from src.domain import Faction, FactionHierarchy, FactionIdeology, Reputation, Karma, Treaty, Alliance
from src.application.exceptions import ValidationError

def validate_faction_system(faction_id: str) -> list[str]:
    """Валидация фракционной системы."""
    errors = []
    
    faction = FactionRepository.get(faction_id)
    
    try:
        faction.validate()
    except ValidationError as e:
        errors.append(f"Фракция: {e.message}")
    
    # Проверяем иерархию
    if faction.hierarchy_id:
        hierarchy = FactionHierarchyRepository.get(faction.hierarchy_id)
        try:
            hierarchy.validate()
        except ValidationError as e:
            errors.append(f"Иерархия: {e.message}")
    
    # Проверяем идеологию
    if faction.ideology_id:
        ideology = FactionIdeologyRepository.get(faction.ideology_id)
        try:
            ideology.validate()
        except ValidationError as e:
            errors.append(f"Идеология: {e.message}")
    
    # Проверяем репутацию
    if not faction.reputation_id:
        errors.append("Фракция должна иметь привязанную систему репутации")
    
    # Проверяем договоры
    for treaty in faction.treaties:
        try:
            treaty.validate()
        except ValidationError as e:
            errors.append(f"Договор '{treaty.name}': {e.message}")
    
    return errors
```

## Альтернативные потоки
1. **Batch Validation**: Проверять сразу несколько кампаний/квестов/фракций
2. **Incremental Validation**: Валидировать только изменённые сущности
3. **Parallel Validation**: Использовать несколько процессов для проверки больших объёмов

## Интеграция с другими Use Cases
- **UC1: Campaign Management** — использует валидацию кампаний
- **UC2: Quest System** — использует валидацию квестовых цепочек
- **UC3: Faction System** — использует валидацию фракций
- **UC4: Economy** — использует валидацию торговых маршрутов

## Метрики успеха
- **Validation Success Rate**: % кампаний/квестов/фракций, прошедших валидацию
- **Error Rate**: % валидаций, завершившихся с ошибками
- **Average Fix Time**: Среднее время исправления ошибок
- **Data Quality Score**: Оценка качества данных на основе количества ошибок

## Заключение
Система валидации обеспечивает:
- ✅ Целостность лор-данных перед импортом
- ✅ Отсутствие циклических зависимостей
- ✅ Согласованность между кампаниями, квестами и фракциями
- ✅ Профессиональный контроль качества

Это делает loreSystem готовым для экспорта данных в профессиональные AAA-игровые движки (Unreal Engine, Unity, Godot) с минимальным риском ошибок.
