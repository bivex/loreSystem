"""
Mutmut configuration for mutation testing.

This file configures mutmut to run mutation tests on the codebase.
Mutation testing helps find gaps in test coverage by introducing bugs
and checking if tests catch them.
"""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def pre_mutation(context):
    """Called before each mutation."""
    # Skip mutations in test files
    if '/test' in context.filename or '\\test' in context.filename:
        return False
    # Skip __init__ files
    if '__init__.py' in context.filename:
        return False
    return True

def timeouts_multiplier():
    """Timeout multiplier for slow tests."""
    return 3

# Paths to mutate (can be expanded)
paths_to_mutate = [
    'src/presentation/gui/lore_data.py',
]

# Test command - runs specific test file
test_command = 'python -m pytest tests/unit/test_lore_data.py -x --tb=short -v'

# Paths to exclude from mutation
exclude = [
    '*/tests/*',
    '*/test_*',
    '*/__pycache__/*',
    '*/migrations/*',
    '*/__init__.py',
    '*/venv/*',
    '*/.venv/*',
]
