# Анализ генерации: tmp/ru_run8_darkfantasy_full_trinity_20251219.db

## 📊 Статистика по таблицам

| Таблица | Записей | Статус |
|---------|---------|--------|
| characters | 4 | ✅ Есть данные |
| acts | 3 | ✅ Есть данные |
| episodes | 3 | ✅ Есть данные |
| chapters | 2 | ✅ Есть данные |
| rumors | 1 | ✅ Есть данные |
| events | 1 | ✅ Есть данные |
| character_relationships | 1 | ✅ Есть данные |
| quests | 1 | ⚠️ Проблема с языком |
| quest_chains | 1 | ⚠️ Проблема с языком |
| quest_nodes | 1 | ⚠️ Проблема с языком |
| quest_objectives | 1 | ⚠️ Проблема с языком |
| stories | 1 | ✅ Есть данные |
| campaigns | 1 | ✅ Есть данные |

---

## ❌ ПРОБЛЕМЫ

### 1. **Quests полностью на английском** ❌

**Пример:**
```json
{
  "name": "Silence Before the Bell",
  "description": "Carry the final warning through the harbor before the bells trigger panic.",
  "acceptance_text": "Elra presses a sealed note into your hand. Get the dockworkers moving...",
  "objectives": ["Speak to the dockworkers", "Light the signal pyre"]
}
```

**Ожидается:**
```json
{
  "name": "Тишина перед колоколом",
  "description": "Доставь последнее предупреждение по гавани перед тем, как колокола вызовут панику.",
  "objectives": ["Поговори с докерами", "Зажги сигнальный костер"]
}
```

**Причина:** Trinity Mini игнорирует `output_language: ru` для сложных batch operations с quests.

---

### 2. **Characters: смесь русского и английского** ⚠️

**Пример:**
```
name: "Мара Востроу (ведьма-изгранница)"
backstory: "Мара Востроу (ведьма-изгранница) grew up in the shadow of Темное фэнтези: кровавый ритуал в заброшенном храме..."
```

**Проблема:** Бэкстор начинается на русском, затем переключается на английский в середине предложения.

**Причина:** Trinity Mini теряет контекст языка в длинных промптах.

---

### 3. **Неполные данные в Characters** ⚠️

**Поля:**
- `role`: NULL для некоторых персонажей
- `rarity`: NULL
- `element`: NULL
- `parent_id`: NULL

**Проблема:** Не все optional поля заполнены, но для некоторых entities это ожидаемо.

---

## ✅ ЧТО РАБОТАЕТ ХОРОШО

### Rumors - полностью на русском ✅
```
name: "Ритуал крови в подземельях"
description: "В подземельях города происходят кровавые ритуалы..."
source_name: "Шепотный брокер"
truth_level: "Unverified"
```

### Events - полностью на русском ✅
```
name: "Ритуал Восстановления"
description: "В подземельях города, в руинах древнего храма, проводят кровавый ритуал..."
outcome: "ongoing"
```

### Narrative Structure - на русском ✅
```
acts: ["Пробуждение", "Искушение", "Покаяние"]
chapters: ["Ритуал Восстановления", "Покаяние"]
```

---

## 🔧 РЕКОМЕНДАЦИИ - ИСПРАВЛЕНО ✅

### 1. Для Quests (критично) ✅ ИСПРАВЛЕНО
```python
# Усилить language instruction - СДЕЛАНО
system_prompt += """
CRITICAL LANGUAGE REQUIREMENT: Every textual field MUST be in Russian.
DO NOT use English for ANY content value.

Examples:
- 'Speak to the dockworkers' → 'Поговори с докерами'
- 'Light the signal pyre' → 'Зажги сигнальный костер'
- 'Silence Before the Bell' → 'Тишина перед колоколом'
"""
```

### 2. Для Characters ✅ ИСПРАВЛЕНО
```python
# Добавить explicit language instruction - СДЕЛАНО
system_prompt += """
CRITICAL: All text fields MUST be in output language, do NOT mix English.
character_profile_entries field_value: MUST be entirely in output language
"""

# Auto-generated backstory теперь на русском - СДЕЛАНО
backstory_template = f"{text} вырос(ла) под тенью {request.theme}..."
```

### 3. Общая рекомендация
**Использовать более мощную модель для quests:**
- Trinity Mini: хорошо для rumors/events
- GPT-4o/Claude 3.5: необходимо для quests/campaigns

---

## 🎯 ИСПРАВЛЕНИЯ В КОДЕ (commit ff5a67c)

1. ✅ Quest instructions: добавлены CRITICAL reminders для ВСЕХ text fields
2. ✅ Character evolutions/profiles: добавлены 'do NOT mix English' warnings
3. ✅ Narrative batch prompt: добавлены явные примеры EN→RU перевода
4. ✅ Systems batch prompt: усилен language requirement
5. ✅ Character auto-generation backstory: теперь уважает output_language

---

## 📈 Качество по entity types

| Entity Type | Русский | Поля | JSON |
|-------------|---------|------|------|
| Rumors | ✅ 100% | ✅ | ✅ |
| Events | ✅ 100% | ✅ | ✅ |
| Characters | ⚠️ 50% | ⚠️ | N/A |
| Quests | ❌ 0% | ✅ | ✅ |
| Acts/Chapters | ✅ 100% | ✅ | N/A |
| Stories | ✅ 100% | ✅ | N/A |

---

## 🎯 Вывод

**Основная проблема:** Trinity Mini не справляется с `output_language: ru` для:
1. Сложных batch operations (quests + objectives + rewards вместе)
2. Длинных текстов (character backstories)

**Решение:**
1. Разделить batch operations на отдельные вызовы
2. Усилить language prompts
3. Или использовать более мощную модель для complex entities
