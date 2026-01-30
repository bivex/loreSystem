# Use Case 4: Создание и управление системами экономики и торговли

## Описание
Создание и управление сложными экономическими системами с несколькими валютами, торговыми маршрутами, бартерными рынками, налогами и инфляцией.

## Акёры
- **Economy Designer**: Создаёт торговые маршруты и балансирует экономику
- **Technical Designer**: Интегрирует экономику с другими системами
- **Data Analyst**: Анализирует потоки валют и товаров

## Сценарий
Игра имеет несколько валют (золото, серебро, кристаллы) и сложную торговую систему с налогами, инфляцией и бартерными рынками.

## Предусловия
- Наличие миров и локаций (World, Location)
- Наличие валют (Currency) или товаров (Item)
- Наличие NPC-торговцев (Character)

## Постусловия
- Торговые маршруты должны быть прибыльными для игроков
- Налоги должны быть сбалансированы
- Инфляция должна быть контролируемой

## Пример кода

```python
from src.domain import (
    Trade, Barter, Tax, Tariff, Supply, Demand, Inflation, Currency, Location, Character
)
from src.domain.value_objects import TenantId, EntityId, Description, Version, Timestamp

def create_complex_economy(tenant_id: TenantId, world_id: EntityId, main_currency_id: EntityId) -> None:
    """Создаёт сложную экономическую систему."""
    
    # 1. Создаём три основные валюты
    gold_currency = Currency.create(
        tenant_id=tenant_id,
        name="Gold Coins",
        symbol="G",
        is_crypto=False,
        is_global=True
    )
    
    silver_currency = Currency.create(
        tenant_id=tenant_id,
        name="Silver Coins",
        symbol="S",
        is_crypto=False,
        is_global=True
    )
    
    crystal_currency = Currency.create(
        tenant_id=tenant_id,
        name="Magic Crystals",
        symbol="C",
        is_crypto=False,
        is_global=True
    )
    
    # 2. Создаём торговый маршрут
    capital_city = LocationRepository.get(world_id, name="Capital City")
    trade_town = LocationRepository.get(world_id, name="Trade Town")
    
    trade_route = Trade.create(
        tenant_id=tenant_id,
        name="Capital <-> Trade Town Route",
        from_location_id=capital_city.id,
        to_location_id=trade_town.id,
        profit_margin=0.2,  # 20% прибыль
        estimated_daily_volume=1000,  # ~1000 сделок в день
        trade_type="regular"
    )
    
    # 3. Создаём бартерный рынок
    barter = Barter.create(
        tenant_id=tenant_id,
        location_id=capital_city.id,
        name="Grand Barter Square",
        description="Площадка для обмена товаров между игроками",
        is_npc_managed=True,
        commission_rate=0.05  # 5% комиссия
    )
    
    # 4. Настраиваем налоги
    income_tax = Tax.create(
        tenant_id=tenant_id,
        name="Income Tax",
        tax_rate=0.1,  # 10% налог
        applies_to="income",
        currency_id=gold_currency.id
    )
    
    luxury_tax = Tax.create(
        tenant_id=tenant_id,
        name="Luxury Tax",
        tax_rate=0.15,  # 15% налог
        applies_to="luxury",
        currency_id=gold_currency.id
    )
    
    # 5. Настраиваем инфляцию
    inflation = Inflation.create(
        tenant_id=tenant_id,
        rate=1.05,  # 5% инфляция в месяц
        period_days=30,
        currency_id=gold_currency.id
    )
    
    # 6. Настраиваем спрос и предложение
    supply_weapon = Supply.create(
        tenant_id=tenant_id,
        name="Weapon Supply",
        item_type="weapon",
        quantity=1000,
        currency_id=gold_currency.id,
        location_id=capital_city.id
    )
    
    demand_weapon = Demand.create(
        tenant_id=tenant_id,
        name="Weapon Demand",
        item_type="weapon",
        desired_quantity=500,
        currency_id=gold_currency.id,
        location_id=trade_town.id
    )
    
    # 7. Создаём тарифы для торговли
    tariff = Tariff.create(
        tenant_id=tenant_id,
        name="Trade Tariff",
        from_faction_id=None,  # Нет фракции, свободная торговля
        to_faction_id=None,
        item_tax_rate=0.02,  # 2% таможенный сбор
        currency_exchange_rate=1.0
    )
    
    print(f"✅ Экономика создана с 3 валютами")
    print(f"📊 Торговый маршрут: {trade_route.name} (прибыль {trade_route.profit_margin * 100}%)")
    print(f"💰 Налоги: {income_tax.tax_rate * 100}% (доход), {luxury_tax.tax_rate * 100}% (роскошь)")
    print(f"📈 Инфляция: {inflation.rate * 100}% в месяц")
    print(f"📉 Спрос/Предложение: {demand_weapon.desired_quantity} / {supply_weapon.quantity}")

## Альтернативные потоки
1. **Direct Trade**: Игроки могут торговать напрямую без посредников
2. **NPC Merchants**: Использование NPC-торговцев для бартера
3. **Auction Houses**: Аукционы для редких предметов

## Интеграция с другими системами
- **Location System**: Торговые маршруты между локациями
- **Character System**: NPC-торговцы как персонажи
- **Inventory System**: Управление товарами на бартерных рынках
- **Quest System**: Квесты на доставку грузов

## Метрики успеха
- **Transaction Volume**: Количество сделок в час
- **Average Profit**: Средняя прибыль на сделку
- **Currency Velocity**: Скорость оборота валюты
- **Market Efficiency**: Эффективность рынков (% выполненных сделок)
- **Trade Route Optimization**: Самые прибыльные маршруты

## Заключение
Сложная экономика делает мир живым и интересным.
Игроки будут планировать маршруты, следить за ценами и торговать на бартерных рынках.
