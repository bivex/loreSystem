#!/usr/bin/env python3
"""
Parse chapter text and extract entities, relationships, and context.
Input: chapter text (file or stdin)
Output: parsed_data.json with chapter_id and entities array
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

def extract_entities(text):
    """
    Extract entity mentions from chapter text.
    This is a simplified extractor - in production, use NLP/LLM.
    """
    entities = []

    # Extract character names (capitalized words followed by verbs or dialogue)
    character_pattern = r'\b([A-Z][a-z]+)\b(?=\s+(?:said|asked|replied|thought|walked|ran|looked))'
    characters = set(re.findall(character_pattern, text))
    for char in characters:
        entities.append({
            'type': 'character',
            'name': char,
            'mentions': text.count(char)
        })

    # Extract location names (simplified)
    location_pattern = r'(?:in|at|near|from|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    locations = set(re.findall(location_pattern, text))
    for loc in locations:
        if len(loc.split()) > 1:  # Multi-word location
            entities.append({
                'type': 'location',
                'name': loc,
                'mentions': text.count(loc)
            })

    # Extract potential quest keywords
    quest_keywords = ['find', 'rescue', 'retrieve', 'defeat', 'explore', 'investigate']
    for keyword in quest_keywords:
        if keyword.lower() in text.lower():
            entities.append({
                'type': 'quest_keyword',
                'keyword': keyword,
                'context': 'potential_quest'
            })

    return entities

def extract_relationships(text, entities):
    """Extract relationships between entities based on text analysis."""
    relationships = []

    # Simplified: characters mentioned together might have relationships
    character_entities = [e for e in entities if e['type'] == 'character']
    for i, char1 in enumerate(character_entities):
        for char2 in character_entities[i+1:]:
            # If characters appear near each other in text
            if char1['name'] in text and char2['name'] in text:
                relationships.append({
                    'entity_a': char1['name'],
                    'entity_b': char2['name'],
                    'type': 'mentioned_together',
                    'confidence': 'low'
                })

    return relationships

def generate_chapter_id():
    """Generate a unique chapter ID."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"chapter_{timestamp}"

def main():
    # Read chapter text from file or stdin
    if len(sys.argv) > 1:
        chapter_file = sys.argv[1]
        try:
            with open(chapter_file, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"ERROR: Chapter file not found: {chapter_file}")
            sys.exit(1)
    else:
        text = sys.stdin.read()

    if not text or len(text.strip()) < 50:
        print("ERROR: Chapter text is too short or empty")
        sys.exit(1)

    # Extract entities and relationships
    entities = extract_entities(text)
    relationships = extract_relationships(text, entities)

    # Generate chapter ID
    chapter_id = generate_chapter_id()

    # Create parsed data output
    parsed_data = {
        'chapter_id': chapter_id,
        'text_length': len(text),
        'word_count': len(text.split()),
        'entities': entities,
        'relationships': relationships,
        'metadata': {
            'parser_version': '1.0',
            'extraction_method': 'regex_patterns',
            'timestamp': datetime.now().isoformat()
        }
    }

    # Write output files
    with open('parsed_data.json', 'w') as f:
        json.dump(parsed_data, f, indent=2)

    with open('extracted_entities.json', 'w') as f:
        json.dump(entities, f, indent=2)

    with open('relationships.json', 'w') as f:
        json.dump(relationships, f, indent=2)

    print(f"✓ Chapter parsed successfully")
    print(f"  Chapter ID: {chapter_id}")
    print(f"  Word count: {parsed_data['word_count']}")
    print(f"  Entities extracted: {len(entities)}")
    print(f"  Relationships found: {len(relationships)}")

    sys.exit(0)

if __name__ == '__main__':
    main()
