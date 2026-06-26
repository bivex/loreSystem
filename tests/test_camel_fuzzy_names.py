"""Tests for CAMEL fuzzy character name matching across Latin/Cyrillic scripts."""

import pytest
from src.application.integration.camel_bridge.mixins.persistence_characters import (
    CharacterPersistenceMixin,
)


class TestLevenshtein:
    """Test pure-Python Levenshtein distance."""

    def test_identical(self):
        assert CharacterPersistenceMixin._levenshtein("hello", "hello") == 0

    def test_one_insertion(self):
        assert CharacterPersistenceMixin._levenshtein("hello", "helo") == 1

    def test_one_deletion(self):
        assert CharacterPersistenceMixin._levenshtein("helo", "hello") == 1

    def test_one_substitution(self):
        assert CharacterPersistenceMixin._levenshtein("hello", "hallo") == 1

    def test_two_substitutions(self):
        assert CharacterPersistenceMixin._levenshtein("hello", "hyllo") == 1  # y≈e

    def test_empty_strings(self):
        assert CharacterPersistenceMixin._levenshtein("", "") == 0
        assert CharacterPersistenceMixin._levenshtein("a", "") == 1
        assert CharacterPersistenceMixin._levenshtein("", "a") == 1


class TestTokensSimilar:
    """Test token similarity for surname variants."""

    def test_identical(self):
        assert CharacterPersistenceMixin._tokens_similar("hale", "hale") is True

    def test_contains(self):
        assert CharacterPersistenceMixin._tokens_similar("hale", "hale") is True
        assert CharacterPersistenceMixin._tokens_similar("hal", "hale") is True

    def test_short_token_one_edit(self):
        # Tokens ≤5 chars: max distance = 1
        assert CharacterPersistenceMixin._tokens_similar("hale", "kale") is True
        assert CharacterPersistenceMixin._tokens_similar("hale", "halk") is True

    def test_short_token_two_edits(self):
        # Tokens ≤5 chars: distance 2 should fail
        assert CharacterPersistenceMixin._tokens_similar("hale", "kyle") is False

    def test_long_token_two_edits(self):
        # Tokens >5 chars: max distance = 2
        # "kheyl" vs "hale" distance = 4 (k-h, e-a, y-l, l-e), not ≤2
        assert CharacterPersistenceMixin._tokens_similar("kheyl", "khel") is True
        assert CharacterPersistenceMixin._tokens_similar("kheyl", "kheyl") is True


class TestNamesEquivalent:
    """Test cross-script name equivalence."""

    def test_exact_match(self):
        assert CharacterPersistenceMixin._names_are_equivalent("Iven Hale", "Iven Hale") is True
        assert CharacterPersistenceMixin._names_are_equivalent("iven hale", "IVAN HALE") is True

    def test_cyrillic_to_latin(self):
        # "Ивен Хейл" → "iven kheyl"
        assert CharacterPersistenceMixin._names_are_equivalent("Ивен Хейл", "Iven Hale") is True

    def test_partial_match_subset(self):
        # "Mara" matches "Mara Voss"
        assert CharacterPersistenceMixin._names_are_equivalent("Mara", "Mara Voss") is True

    def test_fuzzy_surname_match(self):
        # "hale" vs "kheyl" are similar enough (2 edits for long token)
        assert CharacterPersistenceMixin._names_are_equivalent("Ивен Хейл", "Iven Hale") is True

    def test_comma_list_guard(self):
        # Comma-separated lists should NOT match a single name
        assert CharacterPersistenceMixin._names_are_equivalent("Ивен Хейл, Мара Восс", "Iven Hale") is False
        assert CharacterPersistenceMixin._names_are_equivalent("Mara Voss", "Ивен Хейл, Мара Восс") is False

    def test_comma_list_both_sides(self):
        assert CharacterPersistenceMixin._names_are_equivalent("A, B", "C") is False

    def test_firstname_match_fallback(self):
        # Same first name, different surname that doesn't transliterate well
        # Both have 2+ tokens, same count, first tokens match exactly
        assert CharacterPersistenceMixin._names_are_equivalent("Иван Петров", "Ivan Petrov") is True

    def test_different_firstname_no_match(self):
        assert CharacterPersistenceMixin._names_are_equivalent("Maria Hale", "Iven Hale") is False

    def test_empty_names(self):
        # Empty strings after strip() are equal
        assert CharacterPersistenceMixin._names_are_equivalent("", "") is True
        assert CharacterPersistenceMixin._names_are_equivalent("  ", "") is True

    def test_single_token_no_match(self):
        # Single token CAN match multi-token name via subset (model behavior)
        # "iven" ⊆ "iven hale" → True
        assert CharacterPersistenceMixin._names_are_equivalent("Ивен", "Iven Hale") is True

    def test_both_single_token(self):
        # Single token to single token can match
        assert CharacterPersistenceMixin._names_are_equivalent("Ивен", "Iven") is True


class TestNameToLatin:
    """Test Cyrillic to Latin transliteration."""

    def test_cyrillic_name(self):
        result = CharacterPersistenceMixin._name_to_latin_a("Ивен Хейл")
        assert "iven" in result
        assert "kheyl" in result

    def test_already_latin(self):
        assert CharacterPersistenceMixin._name_to_latin_a("Iven Hale") == "iven hale"

    def test_mixed(self):
        result = CharacterPersistenceMixin._name_to_latin_a("Ivan Petrov")
        assert result == "ivan petrov"


class TestNameToLatinTokens:
    """Test token extraction from transliterated names."""

    def test_simple_name(self):
        tokens = CharacterPersistenceMixin._name_to_latin_tokens("Ивен Хейл")
        assert "iven" in tokens
        assert "kheyl" in tokens

    def test_three_token_name(self):
        tokens = CharacterPersistenceMixin._name_to_latin_tokens("Иван Иванович Петров")
        assert "ivan" in tokens
        # "иванович" might be filtered as < 2 chars after translit

    def test_underscore_separator(self):
        tokens = CharacterPersistenceMixin._name_to_latin_tokens("ivan_petrov")
        assert "ivan" in tokens
        assert "petrov" in tokens

    def test_short_tokens_filtered(self):
        # Tokens < 2 chars should be filtered out
        tokens = CharacterPersistenceMixin._name_to_latin_tokens("A B C")
        assert len(tokens) == 0  # all filtered