#!/usr/bin/env python3
"""
Check which repositories are implemented vs which are defined in the domain model.
Fixed version.
"""

import re
from pathlib import Path
from typing import Dict, List, Set

# Path definitions
domain_repos_dir = Path("/root/clawd/src/domain/repositories")
infrastructure_dir = Path("/root/clawd/src/infrastructure")

# Find all repository interfaces in domain
def find_repository_interfaces():
    """Find all I*Repository interfaces."""
    interfaces = {}

    for filepath in domain_repos_dir.glob("*_repository.py"):
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Find abstract class definitions
            matches = re.findall(r'class\s+(I\w+Repository)\s*\([^)]*\):', content)
            for match in matches:
                # Remove only the 'I' prefix for repository interfaces
                # IWorldRepository -> WorldRepository
                # ICharacterRepository -> CharacterRepository
                name = match[1:]  # Remove first character 'I'
                interfaces[name] = {
                    'interface': match,
                    'file': filepath.name,
                    'path': str(filepath)
                }
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    return interfaces

# Find all repository implementations in infrastructure
def is_interface_name(class_name):
    """
    Check if class name looks like an interface.

    IWorldRepository -> True (starts with I followed by uppercase)
    ICharacterRepository -> True
    InMemoryWorldRepository -> False (starts with In)
    SQLiteWorldRepository -> False (starts with SQ)
    """
    if not class_name.startswith('I'):
        return False
    # Check if second character is uppercase (interface pattern)
    # OR if the third character is uppercase (IImageRepository)
    if len(class_name) > 2:
        # IWorldRepository: W is uppercase -> True
        # IImageRepository: I is NOT uppercase -> False (it's Image, not I-mage)
        # Actually IImageRepository should match because it's I-Image-Repository
        # We need to check if it starts with "I" followed by another letter that starts a word
        # Pattern: I<Word>Repository
        # IWorldRepository -> World
        # IImageRepository -> Image
        # INoteRepository -> Note
        return class_name[1].isupper()
    return False

def find_repository_implementations():
    """Find all concrete repository implementations."""
    implementations = {}

    # Check in_memory_repositories.py
    in_memory_path = infrastructure_dir / "in_memory_repositories.py"
    if in_memory_path.exists():
        try:
            with open(in_memory_path, 'r') as f:
                content = f.read()

            # Find all class definitions ending with Repository
            # Match both with and without parent classes
            matches = re.findall(r'class\s+(\w+Repository)\s*(?:\([^)]*\))?:', content)
            for match in matches:
                # Skip if it's an interface
                if not is_interface_name(match):
                    # Remove prefix to match interface name
                    # "InMemoryWorldRepository" -> "WorldRepository"
                    base_name = match.replace('InMemory', '')
                    base_name = base_name.replace('SQLite', '')

                    if base_name not in implementations:
                        implementations[base_name] = {}
                    implementations[base_name]['in_memory'] = True
        except Exception as e:
            print(f"Error reading {in_memory_path}: {e}")
            import traceback
            traceback.print_exc()

    # Check sqlite_repositories.py
    sqlite_path = infrastructure_dir / "sqlite_repositories.py"
    if sqlite_path.exists():
        try:
            with open(sqlite_path, 'r') as f:
                content = f.read()

            # Find all class definitions ending with Repository
            # Match both with and without parent classes
            matches = re.findall(r'class\s+(\w+Repository)\s*(?:\([^)]*\))?:', content)
            for match in matches:
                # Skip if it's an interface
                if not is_interface_name(match):
                    # Remove prefix to match interface name
                    # "SQLiteWorldRepository" -> "WorldRepository"
                    base_name = match.replace('SQLite', '')
                    base_name = base_name.replace('InMemory', '')

                    if base_name not in implementations:
                        implementations[base_name] = {}
                    implementations[base_name]['sqlite'] = True
        except Exception as e:
            print(f"Error reading {sqlite_path}: {e}")

    # Check for other implementation files
    for filepath in infrastructure_dir.glob("*_repositories.py"):
        if filepath.name in ["in_memory_repositories.py", "sqlite_repositories.py"]:
            continue

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Find all class definitions ending with Repository
            # Match both with and without parent classes
            matches = re.findall(r'class\s+(\w+Repository)\s*(?:\([^)]*\))?:', content)
            for match in matches:
                if not is_interface_name(match):
                    if match not in implementations:
                        implementations[match] = {}
                    implementations[match][filepath.stem] = True
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    return implementations

# Main check
def main():
    print("=" * 80)
    print("REPOSITORY IMPLEMENTATION CHECK")
    print("=" * 80)
    print()

    # Find interfaces
    print("📋 Domain Repository Interfaces:")
    interfaces = find_repository_interfaces()

    if not interfaces:
        print("  ⚠️  No repository interfaces found!")
        return

    sorted_interfaces = sorted(interfaces.items(), key=lambda x: x[0])
    for name, info in sorted_interfaces:
        print(f"  • {info['interface']:30} ({info['file']})")

    print()
    print(f"Total: {len(interfaces)} interfaces defined")
    print()

    # Find implementations
    print("🔨 Infrastructure Implementations:")
    implementations = find_repository_implementations()

    if not implementations:
        print("  ⚠️  No repository implementations found!")
    else:
        sorted_impls = sorted(implementations.items(), key=lambda x: x[0])
        for name, impls in sorted_impls:
            backends = ", ".join(impls.keys())
            print(f"  • {name:30} ({backends})")

    print()
    print(f"Total: {len(implementations)} concrete implementations")
    print()

    # Check coverage
    print("=" * 80)
    print("📊 COVERAGE REPORT")
    print("=" * 80)
    print()

    # Fully implemented
    fully_implemented = []
    partially_implemented = []
    not_implemented = []

    for name, interface_info in sorted(interfaces.items(), key=lambda x: x[0]):
        if name in implementations:
            impl_info = implementations[name]

            # Check which backends are implemented
            backends = []
            if 'in_memory' in impl_info:
                backends.append('in_memory')
            if 'sqlite' in impl_info:
                backends.append('sqlite')

            if len(backends) >= 2:
                fully_implemented.append((name, backends))
            else:
                partially_implemented.append((name, backends))
        else:
            not_implemented.append(name)

    # Print summary
    print("✅ FULLY IMPLEMENTED (2+ backends):")
    if fully_implemented:
        for name, backends in sorted(fully_implemented):
            print(f"  ✓ {name:30} ({', '.join(backends)})")
    else:
        print("  (none)")
    print()

    print("⚠️  PARTIALLY IMPLEMENTED (1 backend):")
    if partially_implemented:
        for name, backends in sorted(partially_implemented):
            print(f"  ~ {name:30} ({', '.join(backends)})")
    else:
        print("  (none)")
    print()

    print("❌ NOT IMPLEMENTED:")
    if not_implemented:
        for name in sorted(not_implemented):
            print(f"  ✗ {name}")
    else:
        print("  (none)")
    print()

    # Statistics
    total_interfaces = len(interfaces)
    total_implemented = len(fully_implemented) + len(partially_implemented)
    coverage = (total_implemented / total_interfaces * 100) if total_interfaces > 0 else 0

    print("=" * 80)
    print("📈 STATISTICS")
    print("=" * 80)
    print(f"  Total interfaces:       {total_interfaces}")
    print(f"  Fully implemented:      {len(fully_implemented)}")
    print(f"  Partially implemented: {len(partially_implemented)}")
    print(f"  Not implemented:       {len(not_implemented)}")
    print()
    print(f"  Coverage:              {coverage:.1f}%")
    print()

    # Backend breakdown
    print("=" * 80)
    print("🗄️  BACKEND BREAKDOWN")
    print("=" * 80)

    in_memory_count = sum(1 for impls in implementations.values() if 'in_memory' in impls)
    sqlite_count = sum(1 for impls in implementations.values() if 'sqlite' in impls)

    # Also count other backends
    other_backends = {}
    for impls in implementations.values():
        for backend in impls:
            if backend not in ['in_memory', 'sqlite']:
                other_backends[backend] = other_backends.get(backend, 0) + 1

    print(f"  In-Memory: {in_memory_count} implementations")
    print(f"  SQLite:     {sqlite_count} implementations")

    if other_backends:
        for backend, count in sorted(other_backends.items()):
            print(f"  {backend.capitalize():<12} {count} implementations")

    print()

if __name__ == "__main__":
    main()
