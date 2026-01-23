# Лор-Система: Глубокий Анализ и План Улучшений
## Lore System: Deep Analysis and Improvement Plan

> **Цель**: Создать игровую систему с максимальной связностью лора, увлекательным флоу, долгим удержанием игроков и монетизацией через награды и покупки.
>
> **Goal**: Build a game system with maximum lore interconnection, engaging flow, long player retention, and monetization through rewards and purchases.

---

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ / CRITICAL ISSUES

### 1. ❌ ОТСУТСТВУЕТ ИГРОВАЯ ЭКОНОМИКА / Missing Game Economy

**Проблема**: Нет сущностей для монетизации и игровых ценностей.

**Отсутствующие сущности**:
- ❌ `Currency` - игровые валюты (мягкая, твердая, премиум)
- ❌ `PlayerInventory` - инвентарь игрока
- ❌ `PlayerProgress` - прогресс игрока по лору
- ❌ `Reward` - система наград (за квесты, достижения)
- ❌ `Purchase` - покупки за фиат/игровую валюту
- ❌ `Shop` - магазин с предметами
- ❌ `Bundle` - наборы для покупки
- ❌ `Achievement` - достижения
- ❌ `DailyQuest` - ежедневные квесты для удержания
- ❌ `SeasonPass` - сезонный пропуск

**Последствия**:
- Невозможна монетизация
- Нет системы наград
- Нет мотивации для возвращения игроков
- Нет прогрессии

### 2. ❌ СЛАБАЯ СВЯЗАННОСТЬ ЛОРА / Weak Lore Interconnection

**Проблема**: Сущности существуют изолированно, нет глубоких связей.

**Отсутствующие связи**:
- ❌ `CharacterRelationship` - отношения между персонажами (друг, враг, любовник, соперник)
- ❌ `LocationConnection` - связи между локациями (дороги, порталы, тайные проходы)
- ❌ `EventChain` - цепочки событий (причина-следствие)
- ❌ `FactionMembership` - принадлежность к фракциям
- ❌ `ItemOrigin` - история предметов (кто создал, кто владел)
- ❌ `QuestDependency` - зависимости квестов (квесты-предшественники)
- ❌ `CharacterMentor` - система наставничества
- ❌ `LoreReference` - перекрестные ссылки в описаниях

**Последствия**:
- Лор кажется плоским и несвязным
- Нет глубины мира
- Игрок не чувствует влияния своих действий
- Нет эмерджентных историй

### 3. ❌ НЕТ ГАЧА-МЕХАНИКИ / Missing Gacha Mechanics

**Проблема**: Заявлена "gacha RPG", но нет механики коллекционирования.

**Отсутствующие сущности**:
- ❌ `Banner` - баннеры для гачи (ограниченные, стандартные)
- ❌ `Pull` - история вытягиваний игрока
- ❌ `RarityTier` - расширенная система редкостей (SSR, SR, R, N)
- ❌ `CollectionBonus` - бонусы за сбор коллекций
- ❌ `CharacterSkin` - скины персонажей (косметика)
- ❌ `CharacterConstellation` - созвездия/дупликаты для усиления
- ❌ `Pity` - система жалости (гарантированные дропы)

**Последствия**:
- Основная монетизация невозможна
- Нет коллекционного аспекта
- Нет долгосрочных целей для китов

### 4. ❌ НЕТ ИГРОВОГО ФЛОУ / Missing Game Flow

**Проблема**: Нет сущностей для управления потоком игрока.

**Отсутствующие сущности**:
- ❌ `Tutorial` - туториал и онбординг
- ❌ `Milestone` - этапы прогресса
- ❌ `Chapter` - главы основного сюжета
- ❌ `Challenge` - испытания (time-limited)
- ❌ `Expedition` - экспедиции/походы
- ❌ `BattleFormation` - формации для боя
- ❌ `EnemyEncounter` - встречи с врагами
- ❌ `DifficultyLevel` - уровни сложности

**Последствия**:
- Нет структуры прогресса
- Игрок не знает "что дальше"
- Нет системы испытаний
- Низкое удержание

### 5. ❌ НЕТ СОЦИАЛЬНЫХ МЕХАНИК / Missing Social Mechanics

**Проблема**: Одиночная игра без взаимодействия.

**Отсутствующие сущности**:
- ❌ `Guild` - гильдии
- ❌ `GuildMember` - члены гильдии
- ❌ `GuildQuest` - гильдейские квесты
- ❌ `Friend` - друзья игрока
- ❌ `GiftExchange` - обмен подарками
- ❌ `Leaderboard` - таблицы лидеров
- ❌ `PvPMatch` - PvP матчи
- ❌ `CoopRaid` - кооперативные рейды

**Последствия**:
- Нет социального удержания
- Нет вирального роста
- Нет соревновательного аспекта

### 6. ❌ НЕТ СИСТЕМЫ ПРОГРЕССИИ / Missing Progression System

**Проблема**: Не ясно, как персонажи и игрок прогрессируют.

**Отсутствующие сущности**:
- ❌ `CharacterLevel` - уровни персонажей
- ❌ `CharacterAscension` - возвышение персонажей
- ❌ `TalentTree` - деревья талантов
- ❌ `EquipmentSet` - наборы экипировки (сет-бонусы)
- ❌ `WeaponUpgrade` - улучшение оружия
- ❌ `ArtifactSet` - наборы артефактов
- ❌ `PlayerLevel` - уровень игрока
- ❌ `Mastery` - мастерство (skill-based progression)

**Последствия**:
- Нет ощущения роста силы
- Нет долгосрочных целей
- Нет эндгейм-контента

---

## 🟡 ВАЖНЫЕ УЛУЧШЕНИЯ / Important Improvements

### 7. ⚠️ СЛАБЫЕ СВЯЗИ МЕЖДУ STORYLINES И GAMEPLAY

**Проблема**: `Storyline` не связан с игровыми механиками.

**Нужные улучшения**:
- Add `recommended_power_level` к storylines
- Add `unlocked_by_quest_ids` для гейтинга контента
- Add `rewards_on_completion` для мотивации
- Add `branching_paths` для реиграбельности

### 8. ⚠️ ITEMS НЕ ИМЕЮТ ИГРОВОЙ ЦЕННОСТИ

**Проблема**: Items просто описания, нет игровых характеристик.

**Нужные улучшения**:
- Add `stats` (attack, defense, HP, etc.)
- Add `required_level` для прогрессии
- Add `set_id` для сет-бонусов
- Add `enhancement_level` (+0 до +15)
- Add `sell_price` и `buy_price`
- Add `stackable` и `max_stack`

### 9. ⚠️ CHARACTERS НЕ ИМЕЮТ ИГРОВОЙ МЕХАНИКИ

**Проблема**: Characters - только лор, нет боевых характеристик.

**Нужные улучшения**:
- Add `base_stats` (HP, ATK, DEF, SPD, CRIT)
- Add `element` (Fire, Water, Earth, etc.)
- Add `role` (DPS, Tank, Healer, Support)
- Add `energy_cost` для ультов
- Add `pull_banner_id` откуда можно получить
- Add `ownership_status` (owned, not_owned)

### 10. ⚠️ QUESTS НЕ ИМЕЮТ НАГРАДЫ

**Проблема**: Quests не возвращают конкретные награды.

**Нужные улучшения**:
- Add `currency_rewards` (gold, gems, etc.)
- Add `item_rewards` с количеством
- Add `character_rewards` (для сюжетных)
- Add `experience_rewards`
- Add `repeatable` флаг
- Add `daily_limit` для фарма

### 11. ⚠️ EVENTS НЕ ВЛИЯЮТ НА МИР

**Проблема**: Events - просто записи, нет последствий.

**Нужные улучшения**:
- Add `world_state_changes` (что изменилось в мире)
- Add `unlocks_locations` (открывает новые локации)
- Add `unlocks_characters` (появление новых персонажей)
- Add `triggers_events` (цепные реакции)
- Add `reputation_changes` (влияние на фракции)

### 12. ⚠️ LOCATIONS НЕ ИМЕЮТ ИГРОВОГО КОНТЕНТА

**Проблема**: Locations - только описания.

**Нужные улучшения**:
- Add `available_resources` (что можно собрать)
- Add `enemy_types` (кто обитает)
- Add `unlock_requirement` (как открыть)
- Add `fast_travel_available` флаг
- Add `danger_level` (1-10)
- Add `discovered_by_player` статус

---

## 🟢 ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ / Additional Improvements

### 13. ✅ УЛУЧШЕНИЯ GUI (из gui_todo.txt)

**Проблема**: GUI не юзер-френдли.

**Критичные исправления**:
- Replace JSON text inputs with visual editors (ChoiceTab, TokenboardTab)
- Add search and filtering to all tabs
- Add date/time pickers (SessionsTab)
- Add relationship visualization
- Add real-time validation indicators

### 14. ✅ ДОБАВИТЬ СИСТЕМУ ТЕГОВ

**Улучшение**: Расширить систему тегов для фильтрации.

**Нужно**:
- Add `TagCategory` (gameplay, lore, monetization, etc.)
- Add `TagColor` для визуализации
- Add auto-tagging rules
- Add tag popularity tracking

### 15. ✅ УЛУЧШИТЬ СИСТЕМУ ВЫБОРОВ (Choices)

**Проблема**: Choices примитивные, нет игровых последствий.

**Нужно**:
- Add `stat_requirements` (нужна харизма 5+)
- Add `item_requirements` (нужен ключ)
- Add `currency_cost` (заплатить за выбор)
- Add `reputation_impact` (влияние на фракции)
- Add `permanent_consequences` флаг

---

## 📋 ПЛАН РЕАЛИЗАЦИИ / Implementation Plan

### Phase 1: Игровая Экономика (1-2 недели)
**Цель**: Сделать игру монетизируемой

**Новые сущности**:
1. ✅ Create `Currency` entity (gold, gems, premium currency)
2. ✅ Create `PlayerProfile` entity (profile with currencies and progress)
3. ✅ Create `Purchase` entity (IAP transactions)
4. ✅ Create `Shop` entity (in-game shop)
5. ✅ Create `Bundle` entity (special offers)
6. ✅ Create `Reward` entity (quest/achievement rewards)

**Связи**:
- Quest → Reward (many-to-many)
- Purchase → Bundle (one-to-many)
- PlayerProfile → Currency (balances)
- Shop → Item (available items)

### Phase 2: Гача-Механика (1-2 недели)
**Цель**: Реализовать основной драйвер монетизации

**Новые сущности**:
1. ✅ Create `Banner` entity (gacha banners)
2. ✅ Create `Pull` entity (pull history)
3. ✅ Create `CharacterRarity` extended enum (SSR, SR, R, N)
4. ✅ Create `Pity` entity (pity counter)
5. ✅ Create `CollectionMilestone` entity (collection bonuses)
6. ✅ Create `CharacterDuplicate` entity (constellation system)

**Связи**:
- Banner → Character (featured characters)
- Pull → Banner (where pulled)
- Pull → Character (what pulled)
- PlayerProfile → Pity (per banner)
- CollectionMilestone → Reward

### Phase 3: Прогрессия и Силовая Система (2-3 недели)
**Цель**: Дать игроку ощущение роста

**Расширения сущностей**:
1. ✅ Extend `Character` with combat stats
2. ✅ Extend `Item` with game stats
3. ✅ Create `CharacterLevel` entity
4. ✅ Create `CharacterAscension` entity
5. ✅ Create `TalentTree` entity
6. ✅ Create `EquipmentSet` entity
7. ✅ Create `WeaponUpgrade` entity

**Связи**:
- Character → CharacterLevel (current level)
- Character → TalentTree (unlocked talents)
- Item → EquipmentSet (set membership)
- Item → WeaponUpgrade (upgrade level)

### Phase 4: Связность Лора (2-3 недели)
**Цель**: Сделать мир живым и связным

**Новые сущности**:
1. ✅ Create `CharacterRelationship` entity
2. ✅ Create `Faction` entity
3. ✅ Create `FactionMembership` entity
4. ✅ Create `LocationConnection` entity
5. ✅ Create `EventChain` entity
6. ✅ Create `ItemHistory` entity
7. ✅ Create `LoreReference` entity

**Связи**:
- Character ↔ Character (via Relationship)
- Character → Faction (via Membership)
- Location → Location (via Connection)
- Event → Event (via Chain)
- Item → Character (via History - who owned)
- Story → Character/Location/Item (via Reference)

### Phase 5: Игровой Флоу (2-3 недели)
**Цель**: Структурировать путь игрока

**Новые сущности**:
1. ✅ Create `Tutorial` entity
2. ✅ Create `Chapter` entity
3. ✅ Create `Milestone` entity
4. ✅ Create `Challenge` entity (time-limited)
5. ✅ Create `Expedition` entity
6. ✅ Create `DifficultyLevel` entity
7. ✅ Create `PlayerProgress` entity

**Связи**:
- Chapter → Quest (main story quests)
- Chapter → Milestone (chapter completion milestones)
- Milestone → Reward (milestone rewards)
- Challenge → Reward (challenge rewards)
- Expedition → Location (expedition destinations)
- PlayerProgress → Chapter/Quest/Challenge (completion tracking)

### Phase 6: Социальные Механики (2-3 недели)
**Цель**: Удержание через социал

**Новые сущности**:
1. ✅ Create `Guild` entity
2. ✅ Create `GuildMember` entity
3. ✅ Create `GuildQuest` entity
4. ✅ Create `Friend` entity
5. ✅ Create `GiftExchange` entity
6. ✅ Create `Leaderboard` entity
7. ✅ Create `CoopRaid` entity

**Связи**:
- Guild → GuildMember (members)
- Guild → GuildQuest (guild activities)
- PlayerProfile → Friend (friend list)
- PlayerProfile → Leaderboard (rankings)
- CoopRaid → PlayerProfile (participants)

### Phase 7: Ретеншн-Механики (1-2 недели)
**Цель**: Ежедневное возвращение игроков

**Новые сущности**:
1. ✅ Create `DailyQuest` entity
2. ✅ Create `DailyLogin` entity
3. ✅ Create `SeasonPass` entity
4. ✅ Create `Achievement` entity
5. ✅ Create `TimeGate` entity (energy system)
6. ✅ Create `WeeklyBoss` entity

**Связи**:
- DailyQuest → Reward (daily rewards)
- DailyLogin → Reward (login bonuses)
- SeasonPass → Milestone (tier rewards)
- Achievement → Reward (achievement rewards)
- WeeklyBoss → Character (boss enemies)

### Phase 8: GUI Улучшения (3-4 недели)
**Цель**: Сделать редактор профессиональным

**Задачи** (из gui_todo.txt):
1. ✅ Replace JSON inputs with visual editors
2. ✅ Add search and filtering
3. ✅ Add date/time pickers
4. ✅ Add validation indicators
5. ✅ Add relationship graph view
6. ✅ Add entity preview panels
7. ✅ Add keyboard shortcuts
8. ✅ Add undo/redo system

---

## 🎯 ПРИОРИТЕТЫ ДЛЯ БЫСТРОГО СТАРТА / Quick Start Priorities

### Минимальный MVP для Игры (2-3 недели):

**Неделя 1: Базовая Экономика**
- [ ] Currency entity
- [ ] PlayerProfile entity
- [ ] Reward entity
- [ ] Extend Quest with rewards
- [ ] Simple shop

**Неделя 2: Базовая Гача**
- [ ] Banner entity
- [ ] Pull entity
- [ ] Character rarity tiers
- [ ] Simple pity system

**Неделя 3: Базовая Прогрессия**
- [ ] Character stats (HP, ATK, DEF)
- [ ] Item stats
- [ ] Character levels (1-100)
- [ ] Simple combat formula

### Критические Связи для Лора (параллельно):
- [ ] CharacterRelationship
- [ ] Faction + FactionMembership
- [ ] EventChain (причина-следствие)
- [ ] LocationConnection

---

## 📊 МЕТРИКИ УСПЕХА / Success Metrics

### Технические Метрики:
- **Связность**: Средний # связей на сущность > 3
- **Покрытие**: Все сущности имеют игровую ценность
- **Реюзабельность**: Все предметы можно получить через gameplay

### Игровые Метрики:
- **Retention D1**: > 40%
- **Retention D7**: > 20%
- **Retention D30**: > 10%
- **ARPU**: > $5
- **Conversion**: > 3%
- **Session Length**: > 15 минут
- **Sessions per Day**: > 3

### Метрики Лора:
- **Lore Depth**: Каждый персонаж связан >= 3 другими
- **World Cohesion**: Все события влияют на мир
- **Player Agency**: Выборы влияют на 50%+ контента

---

## 🚨 РИСКИ И МИТИГАЦИЯ / Risks and Mitigation

### Риск 1: Перегрузка Сложностью
**Проблема**: Слишком много сущностей = сложность разработки

**Митигация**:
- Начать с MVP (Currency, Banner, Stats)
- Итеративно добавлять фичи
- Приоритет: Монетизация → Прогрессия → Социал

### Риск 2: Несбалансированная Экономика
**Проблема**: Плохой баланс убивает монетизацию

**Митигация**:
- Моделирование экономики в Excel
- A/B тестирование цен
- Мониторинг метрик (ARPU, Conversion)

### Риск 3: Слабый Лор
**Проблема**: Игроков не зацепит история

**Митигация**:
- Писать backstories >= 200 символов
- Проверять связность (граф-визуализация)
- Тестировать на фокус-группах

### Риск 4: Низкий Retention
**Проблема**: Игроки не возвращаются

**Митигация**:
- Ежедневные квесты с 1-го дня
- Туториал-гайдинг < 5 минут
- Push-нотификации (energy full, events)

---

## 📝 КОНКРЕТНЫЕ TODO / Specific TODOs

### TODO: Новые Entity Файлы

#### Экономика:
- [ ] `src/domain/entities/currency.py` (Currency)
- [ ] `src/domain/entities/player_profile.py` (PlayerProfile)
- [ ] `src/domain/entities/purchase.py` (Purchase)
- [ ] `src/domain/entities/shop.py` (Shop)
- [ ] `src/domain/entities/bundle.py` (Bundle)
- [ ] `src/domain/entities/reward.py` (Reward)

#### Гача:
- [ ] `src/domain/entities/banner.py` (Banner)
- [ ] `src/domain/entities/pull.py` (Pull)
- [ ] `src/domain/entities/pity.py` (Pity)
- [ ] `src/domain/entities/collection_milestone.py` (CollectionMilestone)
- [ ] `src/domain/entities/character_duplicate.py` (CharacterDuplicate)

#### Прогрессия:
- [ ] `src/domain/entities/character_level.py` (CharacterLevel)
- [ ] `src/domain/entities/character_ascension.py` (CharacterAscension)
- [ ] `src/domain/entities/talent_tree.py` (TalentTree)
- [ ] `src/domain/entities/equipment_set.py` (EquipmentSet)
- [ ] `src/domain/entities/weapon_upgrade.py` (WeaponUpgrade)
- [ ] `src/domain/entities/artifact_set.py` (ArtifactSet)

#### Связность Лора:
- [ ] `src/domain/entities/character_relationship.py` (CharacterRelationship)
- [ ] `src/domain/entities/faction.py` (Faction)
- [ ] `src/domain/entities/faction_membership.py` (FactionMembership)
- [ ] `src/domain/entities/location_connection.py` (LocationConnection)
- [ ] `src/domain/entities/event_chain.py` (EventChain)
- [ ] `src/domain/entities/item_history.py` (ItemHistory)
- [ ] `src/domain/entities/lore_reference.py` (LoreReference)

#### Игровой Флоу:
- [ ] `src/domain/entities/tutorial.py` (Tutorial)
- [ ] `src/domain/entities/chapter.py` (Chapter)
- [ ] `src/domain/entities/milestone.py` (Milestone)
- [ ] `src/domain/entities/challenge.py` (Challenge)
- [ ] `src/domain/entities/expedition.py` (Expedition)
- [ ] `src/domain/entities/difficulty_level.py` (DifficultyLevel)
- [ ] `src/domain/entities/player_progress.py` (PlayerProgress)

#### Социальные:
- [ ] `src/domain/entities/guild.py` (Guild)
- [ ] `src/domain/entities/guild_member.py` (GuildMember)
- [ ] `src/domain/entities/guild_quest.py` (GuildQuest)
- [ ] `src/domain/entities/friend.py` (Friend)
- [ ] `src/domain/entities/gift_exchange.py` (GiftExchange)
- [ ] `src/domain/entities/leaderboard.py` (Leaderboard)
- [ ] `src/domain/entities/coop_raid.py` (CoopRaid)

#### Ретеншн:
- [ ] `src/domain/entities/daily_quest.py` (DailyQuest)
- [ ] `src/domain/entities/daily_login.py` (DailyLogin)
- [ ] `src/domain/entities/season_pass.py` (SeasonPass)
- [ ] `src/domain/entities/achievement.py` (Achievement)
- [ ] `src/domain/entities/time_gate.py` (TimeGate)
- [ ] `src/domain/entities/weekly_boss.py` (WeeklyBoss)

### TODO: Value Objects

- [ ] `src/domain/value_objects/currency_amount.py` (CurrencyAmount)
- [ ] `src/domain/value_objects/stats.py` (CharacterStats, ItemStats)
- [ ] `src/domain/value_objects/element.py` (Element enum)
- [ ] `src/domain/value_objects/role.py` (CharacterRole enum)
- [ ] `src/domain/value_objects/relationship_type.py` (RelationshipType enum)
- [ ] `src/domain/value_objects/faction_rank.py` (FactionRank enum)

### TODO: Расширения Существующих Entities

#### Character:
- [ ] Add `base_stats: CharacterStats`
- [ ] Add `element: Element`
- [ ] Add `role: CharacterRole`
- [ ] Add `energy_cost: int`
- [ ] Add `pull_banner_id: Optional[EntityId]`
- [ ] Add `rarity_tier: CharacterRarity` (SSR, SR, R, N)
- [ ] Add `level: int` (1-100)
- [ ] Add `ascension_level: int` (0-6)
- [ ] Add `friendship_level: int` (1-10)

#### Item:
- [ ] Add `stats: ItemStats`
- [ ] Add `required_level: int`
- [ ] Add `set_id: Optional[EntityId]`
- [ ] Add `enhancement_level: int` (0-15)
- [ ] Add `sell_price: CurrencyAmount`
- [ ] Add `buy_price: CurrencyAmount`
- [ ] Add `stackable: bool`
- [ ] Add `max_stack: int`

#### Quest:
- [ ] Add `currency_rewards: List[CurrencyAmount]`
- [ ] Add `item_rewards: List[Tuple[EntityId, int]]`
- [ ] Add `character_rewards: List[EntityId]`
- [ ] Add `experience_rewards: int`
- [ ] Add `repeatable: bool`
- [ ] Add `daily_limit: Optional[int]`
- [ ] Add `required_power_level: int`

#### Event:
- [ ] Add `world_state_changes: Dict[str, Any]`
- [ ] Add `unlocks_locations: List[EntityId]`
- [ ] Add `unlocks_characters: List[EntityId]`
- [ ] Add `triggers_events: List[EntityId]`
- [ ] Add `reputation_changes: Dict[EntityId, int]`

#### Location:
- [ ] Add `available_resources: List[EntityId]`
- [ ] Add `enemy_types: List[str]`
- [ ] Add `unlock_requirement: Optional[str]`
- [ ] Add `fast_travel_available: bool`
- [ ] Add `danger_level: int` (1-10)

#### Storyline:
- [ ] Add `recommended_power_level: int`
- [ ] Add `unlocked_by_quest_ids: List[EntityId]`
- [ ] Add `rewards_on_completion: List[EntityId]`
- [ ] Add `branching_paths: bool`

#### Choice:
- [ ] Add `stat_requirements: Dict[str, int]`
- [ ] Add `item_requirements: List[EntityId]`
- [ ] Add `currency_cost: Optional[CurrencyAmount]`
- [ ] Add `reputation_impact: Dict[EntityId, int]`
- [ ] Add `permanent_consequences: bool`

### TODO: GUI Tabs (Новые)

- [ ] `src/presentation/gui/tabs/currency_tab.py`
- [ ] `src/presentation/gui/tabs/player_profile_tab.py`
- [ ] `src/presentation/gui/tabs/purchase_tab.py`
- [ ] `src/presentation/gui/tabs/shop_tab.py`
- [ ] `src/presentation/gui/tabs/banner_tab.py`
- [ ] `src/presentation/gui/tabs/faction_tab.py`
- [ ] `src/presentation/gui/tabs/relationship_tab.py`
- [ ] `src/presentation/gui/tabs/achievement_tab.py`
- [ ] `src/presentation/gui/tabs/guild_tab.py`
- [ ] `src/presentation/gui/tabs/challenge_tab.py`
- [ ] `src/presentation/gui/tabs/daily_quest_tab.py`
- [ ] `src/presentation/gui/tabs/season_pass_tab.py`

### TODO: GUI Improvements (Существующие)

- [ ] ChoiceTab: Replace JSON inputs with visual option/consequence editors
- [ ] TokenboardTab: Replace JSON with counters table widget
- [ ] SessionsTab: Replace text inputs with QDateTimeEdit
- [ ] All tabs: Add search bars
- [ ] All tabs: Add world filter dropdown
- [ ] All tabs: Add relationship graph view
- [ ] CharactersTab: Add stats editor (HP, ATK, DEF, etc.)
- [ ] ItemsTab: Add stats editor and enhancement level
- [ ] QuestsTab: Add rewards editor

### TODO: Documentation

- [ ] Update README with new entities
- [ ] Create GAME_DESIGN.md (игровой дизайн)
- [ ] Create MONETIZATION.md (стратегия монетизации)
- [ ] Create ECONOMY_BALANCE.md (баланс экономики)
- [ ] Create LORE_GUIDELINES.md (гайдлайны по лору)
- [ ] Update STRUCTURE.md with new entities
- [ ] Create ADR-003: Gacha System Design
- [ ] Create ADR-004: Economy and Monetization
- [ ] Create ADR-005: Progression System

### TODO: Tests

- [ ] Unit tests for all new entities
- [ ] Integration tests for gacha system
- [ ] Integration tests for economy
- [ ] Balance tests (ensure economy is not broken)
- [ ] Relationship integrity tests (orphan detection)

### TODO: Validation

- [ ] Add validation for economy balance (rewards vs costs)
- [ ] Add validation for gacha rates (must sum to 100%)
- [ ] Add validation for character power curves
- [ ] Add validation for lore references (no broken links)
- [ ] Add validation for quest dependencies (no cycles)

### TODO: Examples

- [ ] Create `examples/complete_game_lore.json` with all entities
- [ ] Create `examples/gacha_system_example.json`
- [ ] Create `examples/faction_war_storyline.json`
- [ ] Create `examples/event_chain_example.json`
- [ ] Create `examples/guild_raid_example.json`

---

## 💡 КЛЮЧЕВЫЕ ИНСАЙТЫ / Key Insights

### Для Удержания Игроков:
1. **Ежедневные Цели**: Минимум 3 ежедневных квеста с прогрессом 10-15 минут каждый
2. **Энергия**: Система энергии с восстановлением = постоянные возвращения
3. **События**: Ограниченные по времени события (2-3 недели) = FOMO
4. **Социал**: Гильдии и кооп = социальное удержание
5. **Сезонный Пропуск**: Сезоны по 6-8 недель = долгосрочная цель

### Для Монетизации:
1. **Гача**: Основной источник (70%+ дохода)
2. **Battle Pass**: Стабильный доход ($10-20/месяц от активных)
3. **Convenience**: Энергия, skip tickets = мелкие покупки
4. **Косметика**: Скины персонажей = дополнительный доход
5. **Пакеты**: Ограниченные офферы = импульсные покупки

### Для Глубины Лора:
1. **Отношения**: Минимум 2-3 отношения на персонажа
2. **Фракции**: 5-7 фракций с конфликтами
3. **История Предметов**: Легендарные предметы имеют историю владения
4. **Цепочки Событий**: События влияют друг на друга (причина-следствие)
5. **Перекрестные Ссылки**: Персонажи упоминают друг друга в диалогах

---

## 🎮 ПРИМЕРЫ СВЯЗНОСТИ / Connectivity Examples

### Пример 1: Персонаж "Лира Кровавый Шёпот"

**Текущее состояние** (изолировано):
```
Character: Лира
- Abilities: 3
- No relationships
- No faction
- No item history
```

**Улучшенное состояние** (связанное):
```
Character: Лира
├── Relationships:
│   ├── Враг → Виктор (он убил её семью)
│   ├── Любовник → Элиза (запретная любовь)
│   └── Наставник → Древний Вампир (её создатель)
├── Faction: Клан Кровавой Луны (ранг: Наследница)
├── Items Owned:
│   ├── Клинок Луны (получен от наставника)
│   └── Амулет Крови (семейная реликвия)
├── Quests:
│   ├── "Месть Виктору" (основной квест)
│   └── "Спасти Элизу" (побочный квест)
├── Events:
│   ├── "Уничтожение Клана" (причина её пути)
│   └── "Ритуал Превращения" (её становление)
└── Stats:
    ├── HP: 2500
    ├── ATK: 350
    ├── Element: Dark
    ├── Role: Assassin/DPS
    └── Rarity: SSR
```

### Пример 2: Квест "Forge the Eternal Blade"

**Текущее состояние**:
```
Quest: Forge the Eternal Blade
- Objectives: 3
- No rewards
- No requirements
- No consequences
```

**Улучшенное состояние**:
```
Quest: Forge the Eternal Blade
├── Prerequisites:
│   ├── Complete Quest: "Meet Valorian"
│   ├── Player Level: 20+
│   └── Unlock Location: Shadowmere Wastes
├── Objectives:
│   ├── Gather rare materials (0/5)
│   ├── Temper blade (0/1)
│   └── Infuse soul essence (0/1)
├── Rewards:
│   ├── Currency: 10,000 Gold
│   ├── Currency: 500 Gems
│   ├── Item: Soulfire Blade +5
│   ├── Experience: 5,000 XP
│   └── Achievement: "Master Blacksmith"
├── Unlocks:
│   ├── Quest: "The Great Reforging"
│   ├── Location: Heart of the Forge
│   └── Character: Ancient Smith (recruitable)
└── Consequences:
    ├── Event: "Dimensional Rift Opens"
    ├── World State: forge_power = "awakened"
    └── Reputation: Crystal Guardians +100
```

### Пример 3: Событие "The Great Reforging"

**Текущее состояние**:
```
Event: The Great Reforging
- Description: text
- Participants: 2 characters
- No consequences
```

**Улучшенное состояние**:
```
Event: The Great Reforging
├── Triggered By:
│   ├── Quest: "Forge the Eternal Blade" (completed)
│   └── World State: forge_power = "awakened"
├── Participants:
│   ├── Aria Flameheart (main)
│   ├── Valorian the Eternal (mentor)
│   └── Crystal Guardians (faction)
├── Consequences:
│   ├── Unlocks Location: "Cosmic Anchor Chamber"
│   ├── Triggers Event: "Reality Stabilization Ritual"
│   ├── World State: rifts_sealed = true
│   ├── Reputation Changes:
│   │   ├── Crystal Guardians: +500
│   │   └── Shadow King: -200
│   └── Character Changes:
│       ├── Aria: New Ability "Reality Anchoring II"
│       └── Valorian: Status = "weakened"
├── Branches:
│   ├── Success Path → Peace ending
│   └── Failure Path → Apocalypse ending
└── Lore Impact:
    ├── Mentioned in: 5 future storylines
    ├── Referenced by: 3 characters
    └── Affects: All world locations
```

---

## 📈 ИЗМЕРЕНИЯ ПРОГРЕССА / Progress Tracking

### Метрики Связности (на 18.01.2026):
- **Entities**: 24 типов
- **Avg Connections per Entity**: ~1.5 (НИЗКО, цель: 3+)
- **Entities with Game Value**: ~30% (НИЗКО, цель: 100%)
- **Lore Depth Score**: 3/10 (нужно: 8+)

### После Улучшений (цель):
- **Entities**: 50+ типов
- **Avg Connections per Entity**: 5+
- **Entities with Game Value**: 100%
- **Lore Depth Score**: 9/10

---

## ✅ ВЫВОД / Conclusion

**Текущая система** - хорошая основа для редактора лора, но **не готова для игры**.

**Критические дыры**:
1. ❌ Нет монетизации
2. ❌ Нет гачи
3. ❌ Нет прогрессии
4. ❌ Слабая связность
5. ❌ Нет социала

**Рекомендация**: 
Реализовать **Phase 1-2 (Экономика + Гача)** в первую очередь для MVP, затем **Phase 4 (Связность)** для глубины лора.

**Ожидаемый результат**:
- Игра с полноценной монетизацией
- Глубокий, связанный лор
- Высокое удержание игроков (D7 > 20%)
- Профессиональный редактор для контент-команды

---

**Дата**: 2026-01-18  
**Автор**: Senior Lore System Expert  
**Статус**: Ready for Implementation
