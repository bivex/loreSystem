# Use Case 5: Валидация и импорт/экспорт лор-данных

## Описание
Комплексная проверка целостности лор-данных перед импортом в игровые движки (Unreal, Unity, Godot), экспорт в форматы (JSON, XML, CSV) и управление версиями.

## Акёры
- **Data Engineer**: Валидация целостности данных
- **Technical Writer**: Создание документации форматов
- **QA Engineer**: Проверка импортов/экспортов

## Сценарии
### **Сценарий 1: Валидация кампании перед импортом**
**Сценарий:** Геймдизайнер создал кампанию "War of Three Kingdoms" и хочет валидировать её перед экспортом.

**Действия:**
1. Проверять целостность кампании (Campaign.validate())
2. Проверять все главы на наличие предусловий (Chapter.validate())
3. Проверять все квесты на корректность зависимостей (Quest.validate())
4. Проверять целостность временной линии (Timeline.validate())

**Пример кода:**
```python
from src.domain import Campaign, Chapter, Quest, Timeline

def validate_campaign_for_export(campaign_id: str) -> list[str]:
    """Валидация кампании для экспорта."""
    errors = []
    
    # Получаем кампанию
    campaign = CampaignRepository.get(campaign_id)
    
    # Проверяем кампанию
    try:
        campaign.validate()
    except InvariantViolation as e:
        errors.append(f"Ошибка кампании: {e}")
    
    # Проверяем главы
    for chapter in campaign.chapters:
        try:
            chapter.validate()
        except InvariantViolation as e:
            errors.append(f"Ошибка главы '{chapter.name}': {e}")
        
        # Проверяем квесты в главах
        for quest in chapter.quests:
            try:
                quest.validate()
            except InvariantViolation as e:
                errors.append(f"Ошибка квеста '{quest.name}': {e}")
    
    # Проверяем временную линию
    timeline = TimelineRepository.get_by_world(campaign.world_id)
    try:
        timeline.validate()
    except InvariantViolation as e:
        errors.append(f"Ошибка временной линии: {e}")
    
    # Проверяем взаимосвязи между сущностями
    for quest in QuestRepository.get_by_campaign(campaign_id):
        for prereq in quest.prerequisites:
            if prereq.is_required:
                prereq_quest = QuestRepository.get(prereq.id)
                if not prereq_quest.is_completed_by_default():
                    errors.append(f"Квест '{quest.name}' требует '{prereq_quest.name}', который не является выполненным по умолчанию")
    
    return errors

if __name__ == "__main__":
    campaign_id = "campaign_001"
    errors = validate_campaign_for_export(campaign_id)
    
    if errors:
        print(f"❌ Найдено {len(errors)} ошибок:")
        for err in errors[:10]:
            print(f"  {err}")
        print(f"📊 Всего ошибок: {len(errors)}")
    else:
        print(f"✅ Кампания валидна и готова к экспорту!")
```

### **Сценарий 2: Экспорт кампании в формат JSON**
**Сценарий:** Геймдизайнер экспортирует кампанию "War of Three Kingdoms" в формат JSON для Unreal Engine.

**Действия:**
1. Конвертировать кампанию в структуру JSON (campaign.to_dict())
2. Добавлять метаданные (версия, дата экспорта, автор)
3. Конвертировать все связанные сущности (главы, квесты, NPC)
4. Обеспечивать совместимость с форматом Unreal (ассеты,蓝图ы)

**Пример кода:**
```python
from src.domain import Campaign, Chapter, Quest
import json
from datetime import datetime

def export_campaign_to_unreal_json(campaign_id: str, output_path: str) -> str:
    """Экспорт кампании в формат Unreal Engine JSON."""
    
    campaign = CampaignRepository.get(campaign_id)
    
    # Структура Unreal JSON для кампании
    unreal_data = {
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
            "description": str(campaign.description),
            "campaign_type": campaign.campaign_type,
            "difficulty": campaign.difficulty,
            "recommended_level_range": campaign.recommended_level_range,
            "chapters": [
                {
                    "id": str(chapter.id),
                    "name": chapter.name,
                    "type": chapter.type,
                    "number": chapter.number,
                    "quests": [
                        {
                            "id": str(quest.id),
                            "name": quest.name,
                            "type": quest.type,
                            "difficulty": quest.difficulty,
                            "estimated_time": quest.estimated_time_minutes,
                            "prerequisites": [str(p.id) for p in quest.prerequisites],
                            "objectives": [
                                {
                                    "id": str(obj.id),
                                    "description": str(obj.description),
                                    "type": obj.objective_type
                                } for obj in quest.objectives
                            ]
                        } for quest in chapter.quests
                    ]
                } for chapter in campaign.chapters
            ]
        },
        "metadata": {
            "version": str(campaign.version),
            "export_date": datetime.now().isoformat(),
            "export_tool": "loreSystem v1.0",
            "author": "MythWeave Chronicles"
        },
        "assets": {
            "icons": [f"campaign_{campaign.id}"],
            "backgrounds": [f"bg_{campaign.id}"],
            "soundtracks": [campaign.music_theme_id]
        }
    }
    
    # Записываем в JSON файл
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unreal_data, f, indent=2, ensure_ascii=False)
    
    return output_path

if __name__ == "__main__":
    campaign_id = "campaign_001"
    output_path = "exports/war_of_three_kingdoms_unreal.json"
    
    exported_file = export_campaign_to_unreal_json(campaign_id, output_path)
    print(f"✅ Кампания экспортирована в {exported_file}")
```

### **Сценарий 3: Импорт существующего лор-дата из JSON**
**Сценарий:** Команда хочет импортировать существующий JSON-файл с лор-данными из предыдущего проекта и влить его в текущую систему.

**Действия:**
1. Парсить JSON-файл и проверять структуру
2. Проверять версию файла и конфликты с существующими данными
3. Сливать или перезаписывать существующие сущности
4. Создавать новые версии сущностей при конфликтах (Version.bump_minor())

**Пример кода:**
```python
from src.domain import Campaign, Chapter, Quest, Version
import json
from datetime import datetime

def import_campaign_from_json(json_path: str) -> Campaign:
    """Импорт кампании из JSON-файла."""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Проверяем версию
    existing_campaign = CampaignRepository.get_by_tenant_and_name(
        tenant_id=data['campaign']['tenant_id'],
        name=data['campaign']['name']
    )
    
    if existing_campaign:
        if existing_campaign.version < Version.parse(data['metadata']['version']):
            # Существующая версия старше, перезаписываем
            existing_campaign.update_from_dict(data['campaign'])
            return existing_campaign
        else:
            # Версия новее или совпадает, оставляем без изменений
            return existing_campaign
    
    # Создаём новую кампанию из JSON
    campaign = Campaign.from_dict(data['campaign'])
    
    return campaign

if __name__ == "__main__":
    json_path = "exports/legacy_campaign.json"
    campaign = import_campaign_from_json(json_path)
    print(f"✅ Импортирована кампания: {campaign.name}")
```

### **Сценарий 4: Экспорт всех лор-данных тенанта**
**Сценарий:** Тенант хочет экспортировать ВСЕ свои кампании, квесты, фракции и персонажей в один пакет для бэкапа или миграции.

**Действия:**
1. Получать все сущности тенанта из репозиториев
2. Конвертировать в единый формат (JSON или SQLite)
3. Добавлять метаданные пакета (дата экспорта, количество сущностей)
4. Обеспечивать целостность ссылок между сущностями

**Пример кода:**
```python
from src.domain import Campaign, Quest, Faction, Character, QuestChain
import json
from datetime import datetime

def export_tenant_data(tenant_id: str, output_path: str) -> str:
    """Экспорт всех данных тенанта."""
    
    # Получаем все данные тенанта
    campaigns = CampaignRepository.get_all_by_tenant(tenant_id)
    quests = QuestRepository.get_all_by_tenant(tenant_id)
    factions = FactionRepository.get_all_by_tenant(tenant_id)
    characters = CharacterRepository.get_all_by_tenant(tenant_id)
    
    # Создаём структуру экспорта
    export_data = {
        "tenant_id": tenant_id,
        "export_date": datetime.now().isoformat(),
        "campaigns": [c.to_dict() for c in campaigns],
        "quests": [q.to_dict() for q in quests],
        "factions": [f.to_dict() for f in factions],
        "characters": [ch.to_dict() for ch in characters],
        "metadata": {
            "total_campaigns": len(campaigns),
            "total_quests": len(quests),
            "total_factions": len(factions),
            "total_characters": len(characters)
        }
    }
    
    # Записываем в JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return output_path

if __name__ == "__main__":
    tenant_id = "tenant_001"
    output_path = "exports/tenant_full_backup.json"
    
    exported_file = export_tenant_data(tenant_id, output_path)
    print(f"✅ Экспортированы все данные тенанта {tenant_id} в {exported_file}")
```

### **Сценарий 5: Автоматическое версионирование при конфликтах**
**Сценарий:** Два геймдизайнера редактируют одну кампанию одновременно. Второй сохраняет свои изменения и перезаписывает работу первого.

**Действия:**
1. Проверять версию кампании перед изменением
2. Создавать новую версию при каждом сохранении (Version.bump_patch())
3. Хранить историю изменений (VersionHistory)
4. Уведомлять о конфликтах и предлагать слияния

**Пример кода:**
```python
from src.domain import Campaign, VersionHistory
from datetime import datetime

def save_campaign_with_version(campaign_id: str, changes: dict) -> Campaign:
    """Сохраняет кампанию с новой версией."""
    
    campaign = CampaignRepository.get(campaign_id)
    
    # Создаём новую версию
    new_version = campaign.version.bump_patch()
    campaign.version = new_version
    campaign.updated_at = Timestamp.now()
    
    # Добавляем историю изменений
    history_entry = VersionHistory.create(
        tenant_id=campaign.tenant_id,
        campaign_id=campaign.id,
        version=new_version,
        changes=changes,
        author_id=EntityId("user_current"),
        description="Автоматическое версионирование",
        change_date=Timestamp.now()
    )
    
    # Сохраняем
    CampaignRepository.update(campaign)
    VersionHistoryRepository.add(history_entry)
    
    return campaign

if __name__ == "__main__":
    campaign_id = "campaign_001"
    changes = {
        "name": {"old": "War of Three Kingdoms", "new": "War of Three Kingdoms: Revised"},
        "description": {"old": "...", "new": "Добавлены новые квесты"}
    }
    
    campaign = save_campaign_with_version(campaign_id, changes)
    print(f"✅ Кампания сохранена с версией {campaign.version}")
```

## Интеграция с движками
### **Unreal Engine**
- JSON формат (campaign.to_dict()) совместим с Unreal
- Ассеты (icons, backgrounds) автоматически добавляются
- Квесты привязываются к блупринтам

### **Unity**
- ScriptableObject формат для кампаний
- Prefab для NPC и локаций
- ScriptableObject для квестов

### **Godot**
- .gd/.tscn файлы для кампаний
- PackedScene для диалогов

## Метрики успеха
- **Export Success Rate**: % успешных экспортов
- **Import Success Rate**: % успешных импортов
- **Validation Error Rate**: % данных с ошибками
- **Average Data Size**: Средний размер экспортов
- **Export Frequency**: Количество экспортов в день

## Заключение
Система валидации и импорта обеспечивает:
- ✅ Целостность данных перед интеграцией с движками
- ✅ Поддержка нескольких форматов (JSON, XML, CSV, SQLite)
- ✅ Автоматическое версионирование
- ✅ Профессиональный контроль качества лор-данных
- ✅ Совместимость с AAA-игровыми движками

Это делает loreSystem готовым для использования в профессиональных AAA-игровых студиях.
