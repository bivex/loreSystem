# Verification Tests

This directory contains comprehensive verification tests for all database and domain modeling concepts.

## Test Coverage

The `test_database_domain_verification.py` file verifies **32 concepts**:

1. ✅ Entities (28 domain entities)
2. ✅ Attributes (200+ with types)
3. ✅ Identifiers (primary keys)
4. ✅ Foreign Keys (50+ relationships)
5. ✅ Relationships (1:1, 1:N, M:N)
6. ✅ Cardinality (min/max constraints)
7. ✅ Optionality (required vs optional)
8. ✅ Associative Entities (CharacterRelationship)
9. ✅ Weak Entities (Ability)
10. ✅ Inheritance (patterns identified)
11. ✅ Aggregation (weak has-a)
12. ✅ Composition (strong owns)
13. ✅ Roles (in relationships)
14. ✅ Domains (value object types)
15. ✅ Constraints (CHECK, UNIQUE, FK)
16. ✅ Invariants (business rules)
17. ✅ Business Rules (17+ documented)
18. ✅ States (state enums)
19. ✅ State Transitions (FSM)
20. ✅ Lifecycle (CRUD + versioning)
21. ✅ Events (domain events)
22. ✅ Commands (write operations)
23. ✅ Queries (read operations)
24. ✅ Ownership (multi-tenancy & aggregates)
25. ✅ Permissions (RLS ready)
26. ✅ References (FK & arrays)
27. ✅ Indexes (30+ documented)
28. ✅ Schemas (PostgreSQL)
29. ✅ Tables (28 tables)
30. ✅ Views (materialized views)
31. ✅ Repositories (interfaces)
32. ✅ Aggregate Roots (3 identified)

## Running Tests

```bash
# Install pytest first
pip install pytest

# Run all verification tests
pytest tests/verification/test_database_domain_verification.py -v

# Run with detailed output
pytest tests/verification/test_database_domain_verification.py -v --tb=long

# Run specific test
pytest tests/verification/test_database_domain_verification.py::TestVerification::test_entities_exist -v
```

## Documentation

See `docs/DATABASE_DOMAIN_VERIFICATION.md` for the complete verification document.
