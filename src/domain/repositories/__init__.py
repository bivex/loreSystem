"""
Repository Interfaces (Ports)

These are abstract interfaces defining how the domain interacts with
persistence. Implementations are in the infrastructure layer.

Key principles:
- Repositories work with aggregates, not individual entities
- Methods express domain operations, not database operations
- No infrastructure concerns (SQL, ES) leak into interfaces
"""
