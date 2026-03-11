# CAMEL.Bridge

Мини-мост для генерации и записи цепочки `Rumor -> Event -> CharacterRelationship` в `lore_system.db`.

## ENV support

Bridge автоматически пытается загрузить `.env` из корня workspace.

Поддерживаемые переменные:

- `OPENAI_API_KEY` / другой provider key
- `CAMEL_MODEL_PLATFORM` (например, `OPENAI`)
- `CAMEL_MODEL_TYPE` (например, `GPT_4O_MINI` или raw model string вроде `openai/gpt-oss-20b`)
- `CAMEL_MODEL_BASE_URL` (например, `https://api.groq.com/openai/v1` для OpenAI-compatible провайдера)
- `CAMEL_MODEL_TEMPERATURE` (например, `0.7`)
- `CAMEL_MODEL_MAX_TOKENS`
- `CAMEL_BRIDGE_STRICT_MODEL=true` — полностью выключает fallback

### Пример `.env`

```bash
OPENAI_API_KEY=sk-...
CAMEL_MODEL_PLATFORM=OPENAI
CAMEL_MODEL_TYPE=openai/gpt-oss-20b
CAMEL_MODEL_BASE_URL=https://api.groq.com/openai/v1
CAMEL_BRIDGE_STRICT_MODEL=true
```

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
  --character "Iven Hale" \
  --strict-model
```

Если `--strict-model` или `CAMEL_BRIDGE_STRICT_MODEL=true` включены, bridge **не использует fallback** и упадёт, если:

- нет API key,
- CAMEL/model call сломался,
- модель вернула невалидный JSON.

Без strict-mode мост всё ещё умеет создавать fallback-записи.