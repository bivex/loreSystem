#!/usr/bin/env python
"""
Custom mutation testing script for Windows.

This script introduces mutations (bugs) into the code and checks if tests catch them.
Mutations that survive indicate gaps in test coverage.
"""
import ast
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Tuple
import re


class MutationTester:
    """Custom mutation tester that works on Windows."""
    
    def __init__(self, source_file: str, test_file: str):
        self.source_file = Path(source_file)
        self.test_file = Path(test_file)
        self.backup_file = self.source_file.with_suffix('.py.mutmut_backup')
        self.mutations_found = []
        self.mutations_caught = []
        self.mutations_survived = []
    
    def backup_source(self):
        """Create backup of source file."""
        if self.backup_file.exists():
            self.backup_file.unlink()
        shutil.copy2(self.source_file, self.backup_file)
        print(f"[OK] Backed up {self.source_file} to {self.backup_file}")
    
    def restore_source(self):
        """Restore source file from backup."""
        if self.backup_file.exists():
            shutil.copy2(self.backup_file, self.source_file)
            self.backup_file.unlink()
            print(f"[OK] Restored {self.source_file}")
    
    def run_tests(self) -> bool:
        """Run tests and return True if they pass."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(self.test_file), "-x", "--tb=short", "-q"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def apply_mutation(self, line_num: int, old_str: str, new_str: str, description: str) -> bool:
        """Apply a mutation and test if it's caught."""
        # Read source
        content = self.source_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        if line_num < 1 or line_num > len(lines):
            return False
        
        # Apply mutation
        line_idx = line_num - 1
        original_line = lines[line_idx]
        
        if old_str not in original_line:
            return False
        
        lines[line_idx] = original_line.replace(old_str, new_str, 1)
        self.source_file.write_text('\n'.join(lines), encoding='utf-8')
        
        # Test if mutation is caught
        tests_pass = self.run_tests()
        
        # Restore original
        self.restore_source()
        
        mutation_id = len(self.mutations_found) + 1
        self.mutations_found.append({
            'id': mutation_id,
            'line': line_num,
            'old': old_str,
            'new': new_str,
            'description': description,
            'caught': not tests_pass
        })
        
        if tests_pass:
            self.mutations_survived.append(mutation_id)
            print(f"[SURVIVED] Mutation {mutation_id}: {description} (line {line_num})")
            return False
        else:
            self.mutations_caught.append(mutation_id)
            print(f"[CAUGHT] Mutation {mutation_id}: {description} (line {line_num})")
            return True
    
    def test_mutations(self):
        """Test various mutations."""
        print("\n[MUTATION] Starting mutation testing...")
        print("=" * 60)
        
        self.backup_source()
        
        try:
            content = self.source_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Test mutations on key methods
            mutations_to_test = [
                # Arithmetic mutations
                (r'self\._next_id\s*\+=\s*1', 'self._next_id += 1', 'self._next_id += 2', 'Increment mutation'),
                (r'self\._next_id\s*\+=\s*1', 'self._next_id += 1', 'self._next_id -= 1', 'Decrement mutation'),
                (r'self\._next_id\s*\+=\s*1', 'self._next_id += 1', 'self._next_id += 0', 'No-op mutation'),
                
                # Comparison mutations
                (r'if\s+world\.id\s+is\s+None', 'if world.id is None', 'if world.id is not None', 'None check inversion'),
                (r'if\s+item\.id\s+is\s+None', 'if item.id is None', 'if item.id is not None', 'None check inversion'),
                
                # Return mutations
                (r'return\s+world', 'return world', 'return None', 'Return None mutation'),
                (r'return\s+item', 'return item', 'return None', 'Return None mutation'),
                
                # List operation mutations
                (r'\.append\(', '.append(', '.remove(', 'Append to remove mutation'),
                (r'len\(self\.worlds\)', 'len(self.worlds)', 'len(self.worlds) + 1', 'Length mutation'),
            ]
            
            # Find and test mutations - test all occurrences
            for pattern, old_str, new_str, description in mutations_to_test:
                found_any = False
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line) and old_str in line:
                        self.apply_mutation(line_num, old_str, new_str, f"{description} (line {line_num})")
                        found_any = True
                if not found_any:
                    # Try without regex, just string match
                    for line_num, line in enumerate(lines, 1):
                        if old_str in line:
                            self.apply_mutation(line_num, old_str, new_str, f"{description} (line {line_num})")
                            break
            
            # Test specific line mutations - more comprehensive
            specific_mutations = [
                # ID generation mutations
                (100, 'self._next_id += 1', 'self._next_id += 2', 'ID increment mutation (line 100)'),
                (100, 'self._next_id += 1', 'self._next_id -= 1', 'ID decrement mutation (line 100)'),
                (100, 'self._next_id += 1', 'self._next_id = 1', 'ID reset mutation (line 100)'),
                
                # World mutations
                (105, 'if world.id is None:', 'if world.id is not None:', 'World ID check inversion (line 105)'),
                (106, 'object.__setattr__(world, \'id\', self.get_next_id())', 'pass', 'World ID assignment removal (line 106)'),
                (107, 'self.worlds.append(world)', 'pass', 'World append removal (line 107)'),
                (108, 'return world', 'return None', 'World return None (line 108)'),
                
                # Character mutations
                (112, 'if character.id is None:', 'if character.id is not None:', 'Character ID check inversion (line 112)'),
                (114, 'self.characters.append(character)', 'pass', 'Character append removal (line 114)'),
                
                # Item mutations
                (133, 'if item.id is None:', 'if item.id is not None:', 'Item ID check inversion (line 133)'),
                (135, 'self.items.append(item)', 'pass', 'Item append removal (line 135)'),
                (140, 'if existing.id == item.id:', 'if existing.id != item.id:', 'Item equality to inequality (line 140)'),
                (141, 'self.items[i] = item', 'pass', 'Item update removal (line 141)'),
                (144, 'raise ValueError', 'pass  # raise ValueError', 'Exception removal (line 144)'),
                
                # Quest mutations
                (148, 'if quest.id is None:', 'if quest.id is not None:', 'Quest ID check inversion (line 148)'),
                (150, 'self.quests.append(quest)', 'pass', 'Quest append removal (line 150)'),
            ]
            
            for line_num, old_str, new_str, description in specific_mutations:
                if line_num <= len(lines):
                    line_content = lines[line_num - 1] if line_num > 0 else ''
                    if old_str in line_content:
                        self.apply_mutation(line_num, old_str, new_str, description)
        
        finally:
            self.restore_source()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print mutation testing summary with mutation score."""
        total = len(self.mutations_found)
        caught = len(self.mutations_caught)
        survived = len(self.mutations_survived)

        # Calculate mutation score (industry standard metric)
        mutation_score = (caught / total * 100) if total > 0 else 0

        print("\n" + "=" * 70)
        print("MUTATION TESTING SUMMARY")
        print("=" * 70)
        print(f"Total mutations tested: {total}")
        print(f"Mutations caught by tests: {caught}")
        print(f"Mutations survived: {survived}")
        print(f"Mutation Score: {mutation_score:.1f}%")
        if mutation_score >= 90:
            print("Grade: A (Excellent test coverage)")
        elif mutation_score >= 75:
            print("Grade: B (Good test coverage)")
        elif mutation_score >= 60:
            print("Grade: C (Adequate test coverage)")
        else:
            print("Grade: D/F (Poor test coverage - needs improvement)")

        if self.mutations_survived:
            print("\n[CRITICAL] TEST COVERAGE GAPS FOUND:")
            print("-" * 70)
            print("These mutations survived, indicating missing or weak tests:")
            for mut_id in self.mutations_survived:
                mut = next(m for m in self.mutations_found if m['id'] == mut_id)
                print(f"\nMutation {mut_id}: {mut['description']}")
                print(f"  Line {mut['line']}: {mut['old']} -> {mut['new']}")
                print(f"  [CRITICAL] This mutation was NOT caught by tests!")
                print("  -> Add tests that would fail with this change")
        else:
            print("\n[SUCCESS] All mutations were caught by tests!")
            print("  -> Test suite has excellent behavioral coverage")

        print(f"\n{'=' * 70}")
        print("RECOMMENDATIONS:")
        if mutation_score < 90:
            print("- Review surviving mutations and strengthen tests")
            print("- Consider assertion amplification for better coverage")
            print("- Add edge case tests for uncovered scenarios")
        else:
            print("- Excellent mutation score! Consider testing other modules")
            print("- Review periodically to maintain high coverage")
        print(f"{'=' * 70}")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    source_file = "src/presentation/gui/lore_data.py"
    test_file = "tests/unit/test_lore_data.py"
    
    if not Path(source_file).exists():
        print(f"[ERROR] Source file not found: {source_file}")
        sys.exit(1)
    
    if not Path(test_file).exists():
        print(f"[ERROR] Test file not found: {test_file}")
        sys.exit(1)
    
    tester = MutationTester(source_file, test_file)
    tester.test_mutations()


if __name__ == "__main__":
    main()
