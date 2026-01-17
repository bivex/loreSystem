# ADR 002: PostgreSQL as Primary Database for Transactional Data

**Status:** Accepted

**Date:** 2026-01-17

## Context

The lore system requires:
- ACID transactions for data consistency
- Complex relationships (worlds → characters → abilities)
- Strong data integrity constraints
- Optimistic concurrency control
- Audit trails with timestamps
- Multi-tenancy isolation

We need to choose a primary database for authoritative data storage.

## Decision

We will use **PostgreSQL 15+** as the primary transactional database.

### Rationale

1. **ACID Compliance**: Full transaction support ensures consistency
2. **Rich Constraints**: CHECK, FOREIGN KEY, UNIQUE enforce domain invariants
3. **JSONB Support**: Flexible storage for abilities without normalization overhead
4. **Triggers**: Automatic version increment and timestamp updates
5. **Row Level Security**: Built-in multi-tenancy support
6. **Mature**: Battle-tested, excellent tooling (Alembic migrations)
7. **Performance**: Sufficient for our write load, excellent for complex queries
8. **Open Source**: No vendor lock-in

### Schema Design

- **Normalized to 3NF**: Worlds, Characters, Abilities as separate tables
- **Denormalization where justified**: Only for read-heavy views
- **Enums for type safety**: PostgreSQL custom types for status fields
- **Indexes**: Composite indexes on tenant_id + frequently queried fields
- **Partitioning**: Future option for scaling (by tenant or date)

## Consequences

### Positive

- Strong consistency guarantees
- Domain invariants enforced at DB level (defense in depth)
- Excellent query capabilities for reports
- Mature migration tooling (Alembic)
- Great for small to medium scale (millions of records)

### Negative

- Not horizontally scalable by default (vertical scaling limits)
- Schema migrations require coordination
- Full-text search less powerful than Elasticsearch

### Mitigation

- Use Elasticsearch for full-text search and analytics
- Plan for read replicas if read load increases
- Design schema for backward-compatible migrations
- Keep PostgreSQL as source of truth, ES as projection

## Alternatives Considered

### MongoDB (Document DB)

**Rejected** because:
- Weaker consistency guarantees
- No foreign keys or CHECK constraints
- Schema validation less robust
- Our data is highly relational (worlds → characters → events)

### MySQL

**Rejected** because:
- Less powerful constraint system
- No JSONB equivalent
- Worse handling of complex queries
- PostgreSQL's JSON support is superior

### NoSQL (Cassandra, DynamoDB)

**Rejected** because:
- Overkill for our scale
- Eventual consistency not acceptable for lore integrity
- More complex operations model
- Requirements validation harder

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Martin Fowler on Database Migrations](https://martinfowler.com/articles/evodb.html)
