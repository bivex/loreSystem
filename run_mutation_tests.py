#!/usr/bin/env python
"""
Mutation testing runner script.

This script runs mutation tests using mutmut to find gaps in test coverage.
It will mutate the code and check if tests catch the mutations.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    return True

def main():
    """Main entry point."""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧬 Mutation Testing for LoreSystem")
    print("=" * 60)
    
    # Check if mutmut is installed
    try:
        import mutmut
        print(f"✓ mutmut version: {mutmut.__version__}")
    except ImportError:
        print("❌ mutmut is not installed. Please run:")
        print("   pip install -r requirements-dev.txt")
        sys.exit(1)
    
    # Run mutation tests
    # First, run all mutations
    print("\n🔍 Running mutation tests...")
    print("This may take a while. Mutmut will mutate the code and check if tests catch the mutations.")
    
    cmd = [
        sys.executable, "-m", "mutmut", "run",
        "--paths-to-mutate=src/presentation/gui/lore_data.py",
        "--tests-dir=tests/unit",
        "--test-command=python -m pytest tests/unit/test_lore_data.py -x --tb=short"
    ]
    
    if not run_command(cmd, "Mutation testing"):
        print("\n⚠️  Some mutations were not caught by tests!")
        print("   This indicates gaps in test coverage.")
        print("\n   To see results:")
        print("   python -m mutmut results")
        print("   python -m mutmut show <mutation_id>")
        sys.exit(1)
    
    # Show results
    print("\n📊 Mutation test results:")
    subprocess.run([sys.executable, "-m", "mutmut", "results"])
    
    print("\n✅ Mutation testing complete!")
    print("\nTo investigate specific mutations:")
    print("  python -m mutmut show <mutation_id>")
    print("  python -m mutmut apply <mutation_id>  # Apply mutation to see the change")

if __name__ == "__main__":
    main()
