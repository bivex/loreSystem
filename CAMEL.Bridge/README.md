# CAMEL.Bridge

Мини-мост для генерации и записи цепочки `Rumor -> Event -> CharacterRelationship` в `lore_system.db`.

## Что внутри

- `run_rumor_pipeline.py` — CLI-раннер для полной цепочки
- `Whisper Broker` и `Town Crier` — агентные персоны для слухов
- `Chronicle Weaver` — превращает слухи в событие
- `Bond Archivist` — выводит отношение между персонажами

## Пример запуска

```bash
python CAMEL.Bridge/run_rumor_pipeline.py \
  --tenant-id 1 \
  --world-id 1 \
  --theme "moonlit rebellion" \
  --context "The harbor is tense after three disappearances." \
  --character "Mara Voss" \
  --character "Iven Hale"
```

Если CAMEL/API недоступен, мост всё равно создаст fallback-записи и сохранит их в БД.