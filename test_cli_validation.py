#!/usr/bin/env python3
"""
Comprehensive CLI validation test

Tests all CLI features to ensure production readiness.
"""
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from cli import main

def test_cli_features():
    """Test all CLI features."""
    print("=" * 70)
    print("LoreSystem CLI - Validation Tests")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "tests": []}

    def run_test(name, args, expected_exit_code=0):
        """Run a single test."""
        print(f"\nTest: {name}")
        try:
            exit_code = main(args)
            if exit_code == expected_exit_code:
                print(f"  ✅ PASSED")
                results["passed"] += 1
                results["tests"].append((name, "PASS"))
                return True
            else:
                print(f"  ❌ FAILED (expected {expected_exit_code}, got {exit_code})")
                results["failed"] += 1
                results["tests"].append((name, f"FAIL (exit={exit_code})"))
                return False
        except Exception as e:
            print(f"  ❌ FAILED (exception: {e})")
            results["failed"] += 1
            results["tests"].append((name, f"FAIL ({e})"))
            return False

    # Test 1: Help command
    run_test("Display help", ["--help"])

    # Test 2: World list (empty)
    run_test("List worlds (empty)", ["world", "list"])

    # Test 3: World create - validation error (missing description)
    run_test(
        "World create - validation error",
        ["world", "create", "--name", "Test"],
        expected_exit_code=2  # argparse error
    )

    # Test 4: World create - success
    run_test("World create", [
        "world", "create",
        "--name", "Test World",
        "--description", "A test world"
    ])

    # Test 5: World list (with data - will be empty due to in-memory repo)
    run_test("List worlds (after create)", ["world", "list"])

    # Test 6: World show (non-existent)
    run_test(
        "World show (not found)",
        ["world", "show", "--world-id", "999"],
        expected_exit_code=1
    )

    # Test 7: Character list
    run_test("List characters", ["character", "list"])

    # Test 8: Character create - validation error (missing backstory)
    run_test(
        "Character create - validation error",
        ["character", "create", "--world-id", "1", "--name", "Test"],
        expected_exit_code=2
    )

    # Test 9: Character create - validation error (short backstory)
    run_test(
        "Character create - backstory too short",
        ["character", "create", "--world-id", "1", "--name", "Test", "--backstory", "Too short"],
        expected_exit_code=1
    )

    # Test 10: Character create (world doesn't exist - will fail)
    run_test(
        "Character create (world not found)",
        ["character", "create", "--world-id", "999", "--name", "Test", "--backstory", "A" * 100],
        expected_exit_code=1
    )

    # Test 11: Event list
    run_test("List events", ["event", "list", "--world-id", "1"])

    # Test 12: Story list
    run_test("List stories", ["story", "list", "--world-id", "1"])

    # Test 13: Export functionality
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        export_file = f.name

    try:
        run_test("Export to JSON", ["export", "--output", export_file])

        # Verify export file exists and is valid JSON
        if Path(export_file).exists():
            with open(export_file) as f:
                data = json.load(f)
                if "worlds" in data and "characters" in data:
                    print("  ✅ Export file valid")
                    results["passed"] += 1
                else:
                    print("  ❌ Export file invalid format")
                    results["failed"] += 1
        else:
            print("  ❌ Export file not created")
            results["failed"] += 1
    finally:
        Path(export_file).unlink(missing_ok=True)

    # Test 14: Import functionality
    import_data = {
        "exported_at": "2024-01-15T10:30:00",
        "tenant_id": 1,
        "worlds": [],
        "characters": [],
        "events": [],
        "stories": []
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(import_data, f)
        import_file = f.name

    try:
        run_test("Import from JSON", ["import", "--input", import_file])
    finally:
        Path(import_file).unlink(missing_ok=True)

    # Test 15: Stats command
    run_test("Show statistics", ["stats"])

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Success Rate: {results['passed'] / (results['passed'] + results['failed']) * 100:.1f}%")

    print("\nDetailed Results:")
    for name, result in results["tests"]:
        status = "✅" if result == "PASS" else "❌"
        print(f"  {status} {name}")

    print("\n" + "=" * 70)
    if results["failed"] == 0:
        print("All tests PASSED! ✅")
        return 0
    else:
        print(f"Some tests FAILED: {results['failed']} ❌")
        return 1

if __name__ == '__main__':
    sys.exit(test_cli_features())
