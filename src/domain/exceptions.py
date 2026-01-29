"""Domain Exceptions - Business rule violations."""


class DomainException(Exception):
    """Base exception for all domain errors."""
    pass


class InvariantViolation(DomainException):
    """Raised when a domain invariant is violated."""
    pass


class EntityNotFound(DomainException):
    """Raised when an entity cannot be found."""
    pass


class DuplicateEntity(DomainException):
    """Raised when attempting to create a duplicate entity."""
    pass


class RequirementViolation(DomainException):
    """Raised when a business requirement is not met."""
    pass


class ConcurrencyConflict(DomainException):
    """Raised when optimistic locking detects a conflict."""
    pass


class InvalidState(DomainException):
    """Raised when an entity is in an invalid state for an operation."""
    pass


class InvalidImprovement(DomainException):
    """Raised when an improvement proposal is invalid."""
    pass
