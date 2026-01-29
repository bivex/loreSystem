# ADR 001: Use Hexagonal Architecture (Ports and Adapters)

**Status:** Accepted

**Date:** 2026-01-17

## Context

We are building a lore management system that must:
- Support multiple persistence mechanisms (PostgreSQL, Elasticsearch)
- Integrate with external services (Git, LLM APIs)
- Be testable in isolation
- Allow technology swaps without rewriting business logic
- Enforce strict separation between domain and infrastructure

Traditional layered architectures often lead to:
- Domain logic leaking into infrastructure
- Tight coupling to frameworks and databases
- Difficulty in testing
- Unclear dependency direction

## Decision

We will use **Hexagonal Architecture** (also known as Ports and Adapters pattern) with the following structure:

### Layers

1. **Domain Layer** (Core)
   - Pure business logic
   - Entities, value objects, aggregates
   - Domain services and events
   - Repository interfaces (ports)
   - NO dependencies on infrastructure

2. **Application Layer**
   - Use cases (orchestration)
   - DTOs for data transfer
   - Transaction boundaries
   - Depends on domain abstractions

3. **Infrastructure Layer** (Adapters)
   - Concrete repository implementations
   - Database adapters (SQL, Elasticsearch)
   - External service integrations (Git, LLM)
   - Configuration and logging
   - Depends on domain ports

4. **Presentation Layer** (future)
   - CLI, API endpoints
   - Depends on application layer

### Dependency Rule

Dependencies point **inward only**:
```
Presentation → Application → Domain
Infrastructure → Domain (implements ports)
```

Infrastructure and Presentation NEVER imported by Domain.

### Benefits

1. **Testability**: Domain can be tested with mocks, no databases needed
2. **Flexibility**: Swap PostgreSQL for MongoDB without touching domain
3. **Clarity**: Clear separation of concerns
4. **Maintainability**: Changes in one layer don't cascade
5. **DDD Alignment**: Domain is protected and remains pure

## Consequences

### Positive

- Business logic is isolated and reusable
- Easy to write fast unit tests
- Can evolve infrastructure independently
- Clear boundaries prevent accidental coupling

### Negative

- More interfaces and abstractions
- Initial setup overhead
- Requires discipline to maintain boundaries
- DTOs add some boilerplate

### Mitigation

- Use dependency injection container
- Document architecture in README
- Code reviews enforce boundaries
- Examples and tests demonstrate patterns

## Alternatives Considered

### Traditional Layered Architecture

**Rejected** because:
- Often leads to domain depending on infrastructure
- Hard to test without databases
- Framework lock-in

### Clean Architecture (Uncle Bob)

**Accepted with modification**:
- Very similar to Hexagonal
- We use simpler terminology (fewer layers)
- Same core principles apply

## References

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
