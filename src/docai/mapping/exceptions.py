class MappingError(Exception):
    """Base class for all mapping‐related errors."""


class DomainToDtoError(MappingError):
    """Raised when a failure occurs converting from Domain → DTO."""


class DtoToDomainError(MappingError):
    """Raised when a failure occurs converting from DTO → Domain."""


class DomainToOrmError(MappingError):
    """Raised when a failure occurs converting from Domain → ORM."""


class OrmToDomainError(MappingError):
    """Raised when a failure occurs converting from ORM → Domain."""


class OrmToDtoError(MappingError):
    """Raised when a failure occurs converting from ORM → DTO."""


class LinkDocumentsError(MappingError):
    """Raised when linking documents to a query fails."""


class LinkPagesError(MappingError):
    """Raised when linking pages to a query fails."""
