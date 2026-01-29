"""
Elasticsearch Index Mappings

Following DDD principles:
- Mappings reflect domain model
- Denormalized for read performance
- Strict schema (no dynamic fields)
- Full-text search on narrative content
- Aggregations for analytics
"""

# Index template for all lore indices
index_template = {
    "index_patterns": ["lore_*"],
    "priority": 100,
    "template": {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "refresh_interval": "1s",
            "analysis": {
                "analyzer": {
                    "lore_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                    },
                    "autocomplete_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding", "edge_ngram_filter"]
                    }
                },
                "filter": {
                    "edge_ngram_filter": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 20
                    }
                }
            }
        },
        "mappings": {
            "dynamic": "strict",  # Enforce schema
            "properties": {
                "tenant_id": {
                    "type": "integer"
                },
                "created_at": {
                    "type": "date",
                    "format": "strict_date_optional_time"
                },
                "updated_at": {
                    "type": "date",
                    "format": "strict_date_optional_time"
                },
                "version": {
                    "type": "integer"
                }
            }
        }
    }
}

# Worlds index mapping
worlds_mapping = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "lore_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "integer"},
            "tenant_id": {"type": "integer"},
            "world_name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                },
                "analyzer": "lore_analyzer"
            },
            "description": {
                "type": "text",
                "analyzer": "lore_analyzer",
                "term_vector": "with_positions_offsets"  # For highlighting
            },
            "created_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "updated_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "version": {"type": "integer"},
            "character_count": {"type": "integer"},  # Denormalized for perf
            "event_count": {"type": "integer"}       # Denormalized
        }
    }
}

# Characters index mapping
characters_mapping = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "lore_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "integer"},
            "tenant_id": {"type": "integer"},
            "world_id": {"type": "integer"},
            "world_name": {  # Denormalized for filtering without joins
                "type": "keyword"
            },
            "character_name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                },
                "analyzer": "lore_analyzer"
            },
            "backstory": {
                "type": "text",
                "analyzer": "lore_analyzer",
                "term_vector": "with_positions_offsets",
                "fields": {
                    "length": {
                        "type": "token_count",
                        "analyzer": "standard"
                    }
                }
            },
            "status": {
                "type": "keyword"  # active, inactive
            },
            "abilities": {
                "type": "nested",  # Nested for sub-queries
                "properties": {
                    "name": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "lore_analyzer"
                    },
                    "power_level": {
                        "type": "integer"
                    }
                }
            },
            "ability_count": {"type": "integer"},
            "avg_power_level": {"type": "float"},
            "created_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "updated_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "version": {"type": "integer"}
        }
    }
}

# Events index mapping
events_mapping = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "lore_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "integer"},
            "tenant_id": {"type": "integer"},
            "world_id": {"type": "integer"},
            "world_name": {"type": "keyword"},  # Denormalized
            "event_name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256}
                },
                "analyzer": "lore_analyzer"
            },
            "description": {
                "type": "text",
                "analyzer": "lore_analyzer",
                "term_vector": "with_positions_offsets"
            },
            "start_date": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "end_date": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "outcome": {
                "type": "keyword"  # success, failure, ongoing
            },
            "participant_ids": {
                "type": "integer"  # Array of character IDs
            },
            "participant_names": {  # Denormalized for display
                "type": "keyword"
            },
            "participant_count": {"type": "integer"},
            "duration_days": {"type": "integer"},  # Computed
            "is_ongoing": {"type": "boolean"},
            "created_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "updated_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            },
            "version": {"type": "integer"}
        }
    }
}

# Improvements index mapping
improvements_mapping = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "lore_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "integer"},
            "tenant_id": {"type": "integer"},
            "entity_type": {
                "type": "keyword"  # world, character, event
            },
            "entity_id": {"type": "integer"},
            "entity_name": {"type": "keyword"},  # Denormalized
            "suggestion": {
                "type": "text",
                "analyzer": "lore_analyzer"
            },
            "status": {
                "type": "keyword"  # proposed, approved, applied, rejected
            },
            "git_commit_hash": {
                "type": "keyword"
            },
            "created_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            }
        }
    }
}

# Requirements index mapping
requirements_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "lore_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "integer"},
            "tenant_id": {"type": "integer"},
            "entity_type": {
                "type": "keyword"  # world, character, event, or null for global
            },
            "entity_id": {"type": "integer"},
            "entity_name": {"type": "keyword"},  # Denormalized
            "description": {
                "type": "text",
                "analyzer": "lore_analyzer"
            },
            "is_global": {"type": "boolean"},
            "created_at": {
                "type": "date",
                "format": "strict_date_optional_time"
            }
        }
    }
}

# Export all mappings
MAPPINGS = {
    "lore_worlds": worlds_mapping,
    "lore_characters": characters_mapping,
    "lore_events": events_mapping,
    "lore_improvements": improvements_mapping,
    "lore_requirements": requirements_mapping,
}
