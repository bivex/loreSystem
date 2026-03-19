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

## 🔧 РЕКОМЕНДАЦИИ

### 1. Для Quests (критично)
```python
# Усилить language instruction
system_prompt += """
CRITICAL: ALL text MUST be in Russian. NO English allowed.
Examples:
- "Speak to the dockworkers" → "Поговори с докерами"
- "Light the signal pyre" → "Зажги сигнальный костер"
"""

# Или использовать post-processing translation
def translate_quest_if_english(quest):
    if any(ord(c) < 128 for c in quest["description"]):
        return translate_to_russian(quest)
    return quest
```

### 2. Для Characters
```python
# Добавить explicit language instruction
system_prompt += """
Character backstory MUST be entirely in Russian.
Do NOT mix languages within sentences.
"""
```

### 3. Общая рекомендация
**Использовать более мощную модель для quests:**
- Trinity Mini: хорошо для rumors/events
- GPT-4o/Claude 3.5: необходимо для quests/campaigns

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
