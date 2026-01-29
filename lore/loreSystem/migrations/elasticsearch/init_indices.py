"""
Elasticsearch Index Initialization Script

Creates all indices with proper mappings and settings.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from elasticsearch import Elasticsearch
from migrations.elasticsearch.mappings import MAPPINGS
import os


def get_es_client():
    """Get Elasticsearch client from environment."""
    es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
    es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
    es_user = os.getenv('ELASTICSEARCH_USER', 'elastic')
    es_password = os.getenv('ELASTICSEARCH_PASSWORD', '')
    
    if es_password:
        return Elasticsearch(
            [{'host': es_host, 'port': es_port, 'scheme': 'http'}],
            basic_auth=(es_user, es_password)
        )
    else:
        return Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])


def create_indices(es: Elasticsearch, recreate: bool = False):
    """
    Create all lore indices with mappings.
    
    Args:
        es: Elasticsearch client
        recreate: If True, delete existing indices first
    """
    for index_name, mapping in MAPPINGS.items():
        if es.indices.exists(index=index_name):
            if recreate:
                print(f"Deleting existing index: {index_name}")
                es.indices.delete(index=index_name)
            else:
                print(f"Index already exists: {index_name}, skipping")
                continue
        
        print(f"Creating index: {index_name}")
        es.indices.create(index=index_name, body=mapping)
        print(f"  ✓ Created with {len(mapping['mappings']['properties'])} fields")


def verify_indices(es: Elasticsearch):
    """Verify all indices were created successfully."""
    print("\nVerifying indices...")
    for index_name in MAPPINGS.keys():
        if es.indices.exists(index=index_name):
            stats = es.indices.stats(index=index_name)
            doc_count = stats['indices'][index_name]['total']['docs']['count']
            print(f"  ✓ {index_name}: {doc_count} documents")
        else:
            print(f"  ✗ {index_name}: NOT FOUND")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Elasticsearch indices')
    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Delete and recreate existing indices'
    )
    args = parser.parse_args()
    
    print("Connecting to Elasticsearch...")
    es = get_es_client()
    
    # Test connection
    if not es.ping():
        print("ERROR: Cannot connect to Elasticsearch")
        sys.exit(1)
    
    info = es.info()
    print(f"Connected to Elasticsearch {info['version']['number']}")
    
    # Create indices
    create_indices(es, recreate=args.recreate)
    
    # Verify
    verify_indices(es)
    
    print("\n✓ Initialization complete")


if __name__ == '__main__':
    main()
