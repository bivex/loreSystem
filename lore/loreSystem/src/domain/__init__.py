"""
Domain Layer - Pure Business Logic

This layer contains the core business entities, value objects, and domain services.
It has NO dependencies on infrastructure, frameworks, or external libraries.

Key principles:
- Entities encapsulate business rules and invariants
- Value objects are immutable and compared by value
- Domain services contain logic that doesn't belong to a single entity
- Domain events represent significant business occurrences
"""
