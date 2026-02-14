---
name: entity-validator
description: Validation rules for extracted entities. Checks data types, required fields, cross-entity references, and detects duplicates or conflicts.
user-invocable: false
---
# entity-validator

Базовый скил для валидации извлечённых сущностей.

## Проверки

1. **Типы**: Проверяй типы данных (string, number, boolean, array, object)
2. **Обязательные поля**: Каждая сущность должна иметь все обязательные поля
3. **Связи**: Ссылки на другие сущности должны существовать
4. **Конфликты**: Проверяй на дубликаты и противоречивые данные

## Исправление

- Предупреждай о пропущенных обязательных полях
- Исправляй очевидные ошибки форматирования
- Помечай неуверенные извлечения
