#!/bin/bash
# Test CAMEL Bridge with LM Studio local model
# Generates Rank 1 and Rank 2 entities

set -e

# Configuration
DB_PATH="tmp/lm_studio_test_$(date +%Y%m%d_%H%M%S).db"
TENANT_ID=1
WORLD_ID=1
THEME="Dark Fantasy"
LANGUAGE="ru"

# LM Studio settings
export CAMEL_MODEL_PLATFORM="OPENAI"
export CAMEL_MODEL_BASE_URL="http://127.0.0.1:1234"
export CAMEL_MODEL_TYPE="l3-8b-stheno-v3.2-mlx"
export CAMEL_MODEL_TEMPERATURE="0.8"

echo "🚀 CAMEL Bridge + LM Studio Test"
echo "================================"
echo "DB: $DB_PATH"
echo "Theme: $THEME"
echo "Language: $LANGUAGE"
echo "Model: $CAMEL_MODEL_TYPE"
echo ""

# Check LM Studio is running
echo "🔌 Checking LM Studio..."
if ! curl -s http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
    echo "❌ LM Studio not running! Start LM Studio first."
    exit 1
fi
echo "✅ LM Studio is running"
echo ""

# Rank 1: Basic rumors (character, event, rumor)
echo "📊 Rank 1: Basic Generation"
echo "----------------------------"
python3 CAMEL.Bridge/run_rumor_pipeline.py \
    --tenant-id $TENANT_ID \
    --world-id $WORLD_ID \
    --theme "$THEME" \
    --context "Мрачный мир, где древнее зло пробуждается" \
    --output-language $LANGUAGE \
    --count 2 \
    --db-path "$DB_PATH"

echo ""
echo "✅ Rank 1 complete!"
echo ""

# Rank 2: With campaign story and systems
echo "📊 Rank 2: Campaign + Systems"
echo "------------------------------"
python3 CAMEL.Bridge/run_rumor_pipeline.py \
    --tenant-id $TENANT_ID \
    --world-id $WORLD_ID \
    --theme "$THEME - Осада тёмного замка" \
    --context "Осада проклятого замка тьмы, где герои должны сразиться с нежитью" \
    --output-language $LANGUAGE \
    --count 1 \
    --db-path "$DB_PATH" \
    --with-campaign-story \
    --with-systems

echo ""
echo "✅ Rank 2 complete!"
echo ""

# Summary
echo "📊 Results"
echo "----------"
echo "DB: $DB_PATH"
sqlite3 "$DB_PATH" "SELECT 'rumors', COUNT(*) FROM rumors
UNION ALL SELECT 'characters', COUNT(*) FROM characters
UNION ALL SELECT 'events', COUNT(*) FROM events
UNION ALL SELECT 'quests', COUNT(*) FROM quests
UNION ALL SELECT 'stories', COUNT(*) FROM stories
UNION ALL SELECT 'items', COUNT(*) FROM items;"

echo ""
echo "✅ Test complete! Open DB Tree Server:"
echo "   python3 scripts/db_tree_server.py --db-path $DB_PATH"
