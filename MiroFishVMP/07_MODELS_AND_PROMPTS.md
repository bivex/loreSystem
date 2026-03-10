# Модели и prompt-layer'ы MiroFish

## 1. Зачем нужен этот документ

Этот файл фиксирует не архитектуру данных, а **архитектуру вызовов модели** в `MiroFish`.

Для интеграции с `loreSystem` это критично, потому что мы почти наверняка будем менять не только mapping и DTO, но и:

- model routing
- system prompt'ы
- формат generation prompt'ов
- report framing
- runtime assumptions

## 2. Главный вывод

Сейчас `MiroFish` в основном построен вокруг **единого OpenAI-compatible LLM-контура**:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL_NAME`

Базовый дефолт:

- `LLM_BASE_URL = https://api.openai.com/v1`
- `LLM_MODEL_NAME = gpt-4o-mini`

То есть проект не жестко привязан именно к OpenAI SaaS, но ожидает **OpenAI-compatible API contract**.

## 3. Где берется модель сейчас

### 3.1 Общий config-слот

Файл: `MiroFish/backend/app/config.py`

Там заданы:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL_NAME`

Именно этот слот является основой почти для всех LLM-вызовов в проекте.

### 3.2 `LLMClient`-слой

Файл: `MiroFish/backend/app/utils/llm_client.py`

`LLMClient` берет значения из `Config` и создает OpenAI-compatible client.

Через него идут как минимум:

- ontology generation
- `ReportAgent`

### 3.3 Прямой `openai.OpenAI` в profile/config генераторах

Файлы:

- `MiroFish/backend/app/services/oasis_profile_generator.py`
- `MiroFish/backend/app/services/simulation_config_generator.py`

Оба слоя создают `OpenAI(...)` напрямую, но используют те же значения:

- `Config.LLM_API_KEY`
- `Config.LLM_BASE_URL`
- `Config.LLM_MODEL_NAME`

То есть технически клиент другой, но routing модели логически тот же самый.

### 3.4 Runtime-агенты OASIS/CAMEL

Файлы:

- `MiroFish/backend/scripts/run_twitter_simulation.py`
- `MiroFish/backend/scripts/run_reddit_simulation.py`
- `MiroFish/backend/scripts/run_parallel_simulation.py`

Runtime не использует `LLMClient`. Вместо этого он:

- читает `LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_NAME` из `.env`
- прокидывает их в CAMEL/OASIS через `ModelFactory.create(...)`
- создает runtime model для agent graph

То есть live-агенты в симуляции сидят уже на **OASIS/CAMEL model layer**, а не на нашем application-side client layer.

### 3.5 Boost-модель в parallel runtime

В `run_parallel_simulation.py` есть отдельная ускоряющая конфигурация:

- `LLM_BOOST_API_KEY`
- `LLM_BOOST_BASE_URL`
- `LLM_BOOST_MODEL_NAME`

Текущая логика такая:

- `Twitter` идет через обычный model slot
- `Reddit` в parallel mode может идти через boost-slot
- если boost не задан, происходит fallback на обычный slot

Это уже первый зачаток **разделения моделей по слоям/каналам**, но пока только в runtime.

## 4. Карта prompt-layer'ов

В `MiroFish` prompt'ы лежат не в одном месте, а в нескольких семантических слоях.

### 4.1 Ontology prompt

Файл: `MiroFish/backend/app/services/ontology_generator.py`

Слой отвечает за:

- выбор `entity_types`
- выбор `edge_types`
- ограничение ontology под social-media simulation

Ключевые особенности текущего prompt'а:

- требует **ровно 10 entity types**
- требует сущности, которые могут **говорить / реагировать / влиять**
- запрещает абстракции вроде "эмоций", "трендов" и "тем"
- требует JSON-output
- принудительно держит social-simulation framing

Это хороший prompt для `MiroFish` как отдельной системы, но слабое место для интеграции с `loreSystem`, потому что он не совпадает с идеей полноценного lore-canon.

### 4.2 Profile/persona prompt

Файл: `MiroFish/backend/app/services/oasis_profile_generator.py`

Там есть несколько слоев:

- общий system prompt для profile generation
- prompt для индивидуального персонажа
- prompt для группы / институции / официального аккаунта

Что просит текущий prompt:

- `bio`
- длинное `persona`
- `age`
- `gender`
- `mbti`
- `country`
- `profession`
- `interested_topics`

При этом prompt очень заточен под:

- реалистичный современный social-media профиль
- китайский язык вывода
- личную или институциональную соцсетевую идентичность

### 4.3 Simulation config prompts

Файл: `MiroFish/backend/app/services/simulation_config_generator.py`

Здесь не один prompt, а серия generation prompt'ов:

- time config
- event config
- agent activity config

Что важно:

- там явно зашиты assumptions про **китайский распорядок дня**
- активность моделируется как social-media behavior
- initial posts генерируются с привязкой к `poster_type`
- agent behavior задается через активность, частоту постов, задержку реакции, stance, influence

Это уже не канон, а **операционализация поведения** для запуска симуляции.

### 4.4 ReportAgent prompts

Файл: `MiroFish/backend/app/services/report_agent.py`

У `ReportAgent` минимум четыре prompt-слоя:

- plan prompt
- section prompt
- ReACT loop prompts
- chat prompt

Текущая рамка очень конкретная:

- агент пишет **future prediction report**
- работает как наблюдатель с "god view"
- обязан вызывать инструменты
- обязан строить текст из simulation evidence
- section-writing построен вокруг `Final Answer:` discipline

Это мощный слой, но он тоже явно доменно окрашен и не нейтрален.

### 4.5 Interview prompt prefix

Файл: `MiroFish/backend/app/api/simulation.py`

Там есть специальный префикс, который заставляет runtime-agent:

- отвечать из persona + memory + past actions
- не вызывать инструменты
- отвечать напрямую текстом

Это маленький, но важный слой, потому что именно он влияет на то, как мы будем получать "живые ответы" агентов после запуска.

### 4.6 Внутренние runtime prompt'ы лежат не только в MiroFish

Важно: не все prompt'ы находятся в самом `MiroFish`.

Когда проект вызывает:

- `generate_twitter_agent_graph(...)`
- `generate_reddit_agent_graph(...)`

часть внутреннего decision-prompting уходит в:

- `oasis-ai`
- `camel-ai`

То есть `MiroFish` задает profile, model и available actions, но не полностью контролирует весь внутренний reasoning/runtime prompt stack.

## 5. Что именно мы, скорее всего, захотим менять

### 5.1 Ontology layer

Наиболее вероятное решение для интеграции с `loreSystem`:

- либо сильно переписать ontology prompt
- либо вообще обходить raw-text ontology generation, если canonical world уже построен у нас

Для интеграции `loreSystem -> MiroFish` второй путь обычно правильнее.

### 5.2 Profile/persona layer

С высокой вероятностью придется менять:

- язык prompt'ов
- modern social assumptions
- поля типа `country`, `mbti`, `profession`, если мир не современный
- логику official-account vs individual-account

Иначе fantasy / sci-fi / political-fiction world будет искусственно прижат к современной китайской соцсети.

### 5.3 Behavior/config layer

С высокой вероятностью придется менять:

- China-specific daily rhythm
- типовые эвристики активности
- правила initial posts
- `stance` и `influence` heuristics

Именно здесь симуляция начинает отражать не канон, а культурную и платформенную модель мира.

### 5.4 Report layer

Если мы используем `MiroFish` для сценарного lore-analysis, то, возможно, стоит менять framing:

- не только "future prediction report"
- а, например, "scenario analysis report"
- или "emergent world dynamics report"
- или "faction reaction report"

Иначе отчет будет тащить слишком узкую интерпретацию результата.

### 5.5 Runtime model routing

Сейчас разнесение моделей по слоям почти отсутствует.

Для реальной интеграции разумно предусмотреть отдельные model slots хотя бы для:

- ontology
- profile generation
- simulation config generation
- report generation
- twitter runtime
- reddit runtime

Иначе любая замена модели будет менять сразу весь pipeline.

## 6. Что стоит зафиксировать в нашем target-design

Для совместной системы `loreSystem + MiroFish` стоит заранее проектировать не один `LLM_MODEL_NAME`, а набор:

- `ONTOLOGY_LLM_MODEL`
- `PROFILE_LLM_MODEL`
- `SIM_CONFIG_LLM_MODEL`
- `REPORT_LLM_MODEL`
- `RUNTIME_TWITTER_LLM_MODEL`
- `RUNTIME_REDDIT_LLM_MODEL`

И опционально:

- `RUNTIME_REDDIT_BOOST_MODEL`
- `PROMPT_PROFILE_VERSION`
- `PROMPT_REPORT_VERSION`
- `PROMPT_SIM_CONFIG_VERSION`

Это даст:

- контроль стоимости
- контроль качества по слоям
- возможность A/B-замены prompt'ов
- возможность держать canon-adapter отдельно от runtime-экспериментов

## 7. Практический вывод

Если формулировать совсем коротко, то интеграция потребует менять **три вещи одновременно**:

- данные
- модели
- prompt'ы

Поэтому правильная формула такая:

`canonical lore -> social projection -> model routing -> prompt routing -> runtime simulation -> normalized results`

То есть adapter между системами — это не только DTO-конвертер, а еще и:

- selector того, какие сущности вообще становятся агентами
- selector того, какие модели используются на каждом шаге
- selector того, какие prompt-template'ы применяются к данному миру и сценарию