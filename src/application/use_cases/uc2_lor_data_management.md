# Use Case 2: Управление лор-данными (CRUD операции)

## Описание
Выполнение базовых CRUD операций (Create, Read, Update, Delete) над сущностями доменной модели с репозиториями, валидацией и версионированием.

## Акёры
- **Application Service**: Бизнес-логика для операций
- **Repository Layer**: Паттерн Repository для всех сущностей
- **Cache Layer**: Redis-кэш для часто используемых данных
- **Service Layer**: Высокоуровневые сервисы для каждого типа сущностей
- **Database**: PostgreSQL с миграциями
- **Validation**: Валидация инвариантов и проверка типов

## Сценарии

### **Сценарий 1: Создание новой кампании**
**Актёры:** Lead Developer, Narrative Designer
**Действия:**
1. Narrative Designer создаёт кампанию через UI
2. Валидирует структуру (Campaign.validate())
3. Сохраняет в БД через CampaignRepository
4. Добавляет в Redis-кэш для быстрого доступа
5. Уведомляет игроков через NotificationService

**Пример кода:**
```python
from src.application.services import CampaignService, CacheService, NotificationService
from src.application.repositories import CampaignRepository
from src.domain.entities import Campaign

def create_campaign(tenant_id: str, data: dict) -> Campaign:
    """Создаёт новую кампанию через сервис."""
    try:
        # Валидация входных данных
        required_fields = ["name", "description", "world_id"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Создаём сущность через factory method
        campaign = Campaign.create(
            tenant_id=TenantId(tenant_id),
            name=data["name"],
            description=Description(data["description"]),
            world_id=EntityId(data["world_id"]),
            campaign_type="main_story",
            difficulty="medium"
        )
        
        # Сохраняем через Repository
        saved_campaign = CampaignRepository.create(campaign)
        
        # Кэшируем в Redis
        CacheService.set(
            key=f"campaign:{saved_campaign.id}",
            value=saved_campaign,
            ttl=3600  # 1 час TTL
        )
        
        # Уведомляем
        NotificationService.send_notification(
            tenant_id=tenant_id,
            type="campaign_created",
            message=f"New campaign '{saved_campaign.name}' created"
        )
        
        return saved_campaign
        
    except InvariantViolation as e:
        # Логируем ошибку валидации
        logger.error(f"Validation failed: {e}")
        raise e
        
    except Exception as e:
        # Логируем системную ошибку
        logger.error(f"Failed to create campaign: {e}")
        raise
```

### **Сценарий 2: Получение кампании с кэшем**
**Актёры:** System, Data Analyst
**Действия:**
1. Игрок запрашивает кампанию через API
2. Система проверяет Redis-кэш
3. Если кэш есть — возвращает из кэша (Cache hit)
4. Если нет — загружает из PostgreSQL (Cache miss) и обновляет кэш

**Пример кода:**
```python
from src.application.services import CampaignService, CacheService
from src.application.repositories import CampaignRepository
from src.domain.entities import Campaign

def get_campaign(campaign_id: str, use_cache: bool = True) -> Campaign:
    """Получает кампанию с поддержкой Redis-кэша."""
    if use_cache:
        # Проверяем кэш
        cached = CacheService.get(f"campaign:{campaign_id}")
        if cached:
            logger.info(f"Cache hit for campaign {campaign_id}")
            return cached
    
    # Загружаем из БД
    campaign = CampaignRepository.get(campaign_id)
    if not campaign:
        raise NotFoundError(f"Campaign {campaign_id} not found")
    
    # Обновляем кэш
    if use_cache:
        CacheService.set(
            key=f"campaign:{campaign.id}",
            value=campaign,
            ttl=3600
        )
    
    return campaign
```

### **Сценарий 3: Обновление существующей кампании**
**Актёры:** Narrative Designer, Quest Designer
**Действия:**
1. Получают существующую кампанию из Repository
2. Валидируют изменения (новые главы, описания)
3. Обновляют через Repository.update()
4. Инкрементируют версию (Version.bump_minor())
5. Уведомляют об изменениях через NotificationService

**Пример кода:**
```python
from src.application.services import CampaignService, NotificationService
from src.application.repositories import CampaignRepository
from src.domain.entities import Campaign

def update_campaign(campaign_id: str, updates: dict) -> Campaign:
    """Обновляет существующую кампанию."""
    # Получаем кампанию
    campaign = CampaignRepository.get(campaign_id)
    if not campaign:
        raise NotFoundError(f"Campaign {campaign_id} not found")
    
    # Применяем обновления
    if "name" in updates:
        campaign.name = updates["name"]
    
    if "description" in updates:
        campaign.description = Description(updates["description"])
    
    if "chapters" in updates:
        for chapter_id in updates["chapters"]:
            if chapter_id not in campaign.chapter_ids:
                campaign.add_chapter(chapter_id)
    
    # Инкрементируем версию
    campaign.version = campaign.version.bump_minor()
    campaign.updated_at = Timestamp.now()
    
    # Валидируем
    try:
        campaign.validate()
    except InvariantViolation as e:
        logger.error(f"Validation failed: {e}")
        raise e
    
    # Сохраняем
    updated_campaign = CampaignRepository.update(campaign)
    
    # Очищаем кэш
    CacheService.delete(f"campaign:{campaign.id}")
    
    # Уведомляем
    NotificationService.send_notification(
        tenant_id=campaign.tenant_id,
        type="campaign_updated",
        message=f"Campaign '{campaign.name}' updated to v{campaign.version}"
    )
    
    return updated_campaign
```

### **Сценарий 4: Удаление кампании**
**Актёры:** System Admin, Lead Developer
**Действия:**
1. Проверяют прав доступа и статус кампании
2. Проверяют наличие связей (квесты, персонажи)
3. Выполняют мягкое удаление или полное удаление
4. Инкрементируют версию для аудита (Version.bump_patch())

**Пример кода:**
```python
from src.application.services import CampaignService, AuditService
from src.application.repositories import CampaignRepository
from src.domain.entities import Campaign

def delete_campaign(campaign_id: str, soft_delete: bool = False) -> bool:
    """Удаляет кампанию (soft или hard)."""
    # Получаем кампанию
    campaign = CampaignRepository.get(campaign_id)
    if not campaign:
        raise NotFoundError(f"Campaign {campaign_id} not found")
    
    # Проверяем права доступа
    if not AuditService.has_delete_permission(campaign.tenant_id):
        raise PermissionError("No permission to delete campaign")
    
    # Проверяем связи
    if campaign.has_active_quests():
        if soft_delete:
            raise BusinessRuleError("Cannot delete campaign with active quests")
    
    # Выполняем удаление
    if soft_delete:
        campaign.is_deleted = True
        campaign.deleted_at = Timestamp.now()
        campaign.version = campaign.version.bump_patch()
    else:
        CampaignRepository.delete(campaign_id)
    
    # Логируем удаление
    AuditService.log_action(
        action="delete",
        entity_type="campaign",
        entity_id=campaign_id,
        actor_id=EntityId("user_current")
    )
    
    return True
```

## Метрики успеха
- **CRUD Performance**: Среднее время выполнения операций (Create < 100ms, Read < 50ms, Update < 100ms, Delete < 50ms)
- **Cache Hit Rate**: % операций, выполнённых из кэша (цель > 80%)
- **Validation Rate**: % операций, прошедших валидацию без ошибок
- **Database Query Time**: Среднее время запросов к PostgreSQL (цель < 20ms)
- **Operation Throughput**: Количество операций в секунду (цель > 100 ops/sec)

## Интеграция с другими Use Cases
- **UC1: Campaign Management** — кампании используют CRUD
- **UC3: Faction System** — фракции связаны с кампаниями
- **UC5: Analytics** — операции CRUD логируются в аналитику

## Заключение
Этот Use Case обеспечивает надежное управление лор-данными с:
- ✅ Репозиторий для каждого типа сущности
- ✅ Redis-кэширование для производительности
- ✅ Валидация на уровне доменной модели
- ✅ Версионирование для аудита
- ✅ Интеграция с системой уведомлений
- ✅ Аудит всех операций для безопасности
