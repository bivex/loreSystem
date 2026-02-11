# Use Case 1: Инициализация приложения

## Описание
Первый запуск приложения loreSystem, проверка зависимостей, подключение к базе данных и инициализация основных систем.

## Акёры
- **Lead Developer**: Архитектор приложения
- **Database Engineer**: Настраивает подключение к PostgreSQL
- **System Admin**: Проверяет наличие необходимых сервисов (Redis, кэш)

## Сценарий
Пользователь запускает приложение loreSystem впервые:
1. Проверяется наличие всех зависимостей
2. Подключается к базе данных PostgreSQL
3. Инициализируются основные сервисы (auth, cache, messaging)
4. Загружаются базовые конфигурации и шаблоны

## Предусловия
- PostgreSQL database running (configured)
- Redis cache running (optional)
- Configuration file exists
- User has valid credentials

## Постусловия
- Приложение запущено и готово к работе
- Все системы инициализированы без ошибок
- Конфигурация загружена

## Пример кода

```python
from src.application.services import (
    DatabaseService, CacheService, AuthService,
    ConfigService
)
from src.application.exceptions import (
    InitializationException, DatabaseConnectionException
)
from src.domain import entities

def initialize_application(config_path: str, tenant_id: str) -> bool:
    """
    Инициализация приложения loreSystem.
    
    Parameters:
        config_path: Путь к конфигурационному файлу
        tenant_id: ID тенанта для инициализации
    
    Returns:
        bool: True если инициализация успешна
    """
    try:
        # 1. Загружаем конфигурацию
        config = ConfigService.load(config_path, tenant_id)
        
        # 2. Проверяем наличие необходимых сервисов
        if not DatabaseService.is_available():
            raise InitializationException("PostgreSQL database not available")
        
        if config.get("cache_enabled"):
            if not CacheService.is_available():
                raise InitializationException("Redis cache not available")
        
        # 3. Подключаемся к базе данных
        DatabaseService.connect(
            host=config.get("db_host"),
            port=config.get("db_port"),
            database=config.get("db_name"),
            user=config.get("db_user"),
            password=config.get("db_password")
        )
        
        # 4. Инициализируем кэш (если включён)
        if config.get("cache_enabled"):
            CacheService.connect(
                host=config.get("cache_host"),
                port=config.get("cache_port"),
                db=config.get("cache_db")
            )
        
        # 5. Инициализируем авторизацию
        AuthService.initialize(config)
        
        # 6. Проверяем наличие базовых сущностей в БД
        # Загружаем хотя бы одну кампанию для каждого тенанта
        campaigns = entities.CampaignRepository.get_all(tenant_id)
        if not campaigns:
            # Создаём базовую кампанию для новых тенантов
            from src.domain.entities import Campaign
            baseline_campaign = Campaign.create(
                tenant_id=tenant_id,
                name="First Campaign",
                description="Default campaign for new tenant",
                campaign_type="main_story",
                difficulty="medium"
            )
            campaigns.append(baseline_campaign)
        
        # 7. Создаём конфигурацию приложения
        app_config = ApplicationConfig.create(
            tenant_id=tenant_id,
            init_timestamp=Timestamp.now(),
            db_connected=True,
            cache_connected=config.get("cache_enabled"),
            system_status="ready"
        )
        
        # 8. Логируем успешную инициализацию
        logger.info(f"Application initialized for tenant {tenant_id}")
        logger.info(f"Campaigns found: {len(campaigns)}")
        
        return True
        
    except DatabaseConnectionException as e:
        logger.error(f"Database connection failed: {e}")
        raise InitializationException(f"Failed to connect to database: {e}")
        
    except InitializationException as e:
        logger.error(f"Initialization failed: {e}")
        raise e

# Пример использования
if __name__ == "__main__":
    from src.domain.value_objects import TenantId
    
    tenant_id = TenantId("tenant_001")
    config_path = "/etc/loresystem/config.yaml"
    
    try:
        success = initialize_application(config_path, str(tenant_id))
        
        if success:
            print("✅ Приложение инициализировано успешно")
            print("📚 Все системы готовы к работе")
        else:
            print("❌ Ошибка инициализации приложения")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
```

## Альтернативные потоки
1. **Graceful Degradation**: Если Redis недоступен, приложение работает без кэша
2. **Offline Mode**: Если БД недоступна, приложение запускается с локальным кэшем
3. **Quick Start**: Использование кэшированных конфигураций для быстрого запуска

## Интеграция с другими Use Cases
- **UC2: Управление лор-данными** — использует инициализированные репозитории
- **UC3: Импорт/экспорт** — использует подключение к БД
- **UC6: API для движков** — использует авторизацию

## Метрики успеха
- **Initialization Time**: < 3 секунд для нормального запуска
- **Dependency Check**: 100% доступность всех сервисов
- **Database Connection**: Успешное подключение к PostgreSQL
- **Cache Hit Rate**: 90% для часто используемых данных

## Заключение
Этот Use Case обеспечивает надежную инициализацию приложения loreSystem с проверкой всех зависимостей. Приложение запускается только после того, как все системы готовы, что повышает стабильность и предотвращает ошибки на старте.
