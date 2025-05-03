"""
Mapping logic for converting Document objects between Domain, DTO, and ORM representations.

This module defines the DocumentMapper class, which provides methods to translate
documents across different layers of the application: Domain models, ORM models, and
DTOs used for API communication.

Exceptions are raised for failures during conversions.
"""

import logging
from typing import Optional

from docai.mapping.base import BaseMapper
from docai.mapping.exceptions import (
    DomainToDtoError,
    DomainToOrmError,
    DtoToDomainError,
    OrmToDomainError,
)
from docai.mapping.page_mapper import PageMapper
from docai.shared.models.domain.document import Document as DomainDocument
from docai.shared.models.domain.document import MinimalDocument as DomainMinDocument
from docai.shared.models.dto.document import Document as DTODocument
from docai.shared.models.dto.document import MinimalDocument as DTOMinimalDocument
from docai.shared.models.orm.document import Document as ORMDocument

logger = logging.getLogger(__name__)


class DocumentMapper(BaseMapper):
    """Mapper for converting between DomainDocument, DTODocument, and ORMDocument."""

    def to_dto(self, domain_obj: DomainDocument) -> DTODocument:
        """Convert a DomainDocument to a DTODocument.

        Args:
            domain_obj (DomainDocument): The domain document to convert.

        Returns:
            DTODocument: The resulting DTO document.

        Raises:
            DomainToDtoError: If conversion fails.
        """
        try:
            page_dtos = [PageMapper().to_dto(p) for p in domain_obj.pages]
            data = {
                "id": domain_obj.id,
                "file_name": domain_obj.file_name,
                "status": domain_obj.status,
                "metadata": domain_obj.extra,
                "created_at": domain_obj.created_at,
                "processed_at": domain_obj.processed_at,
                "indexed_at": domain_obj.indexed_at,
                "pages": [p.model_dump() for p in page_dtos],
            }
            return DTODocument.model_validate(data)
        except Exception as e:
            logger.error(
                "DocumentMapper.to_dto failed for %r", domain_obj, exc_info=True
            )
            raise DomainToDtoError(
                f"Domain→DTO failed for document {domain_obj.id}"
            ) from e

    def from_dto(self, dto_obj: DTODocument) -> DomainDocument:
        """Convert a DTODocument to a DomainDocument.

        Args:
            dto_obj (DTODocument): The DTO document to convert.

        Returns:
            DomainDocument: The resulting domain document.

        Raises:
            DtoToDomainError: If conversion fails.
        """
        try:
            pages = [PageMapper().from_dto(p) for p in dto_obj.pages]
            domain = DomainDocument(
                doc_id=dto_obj.id,
                file_name=dto_obj.file_name,
                pages=pages,
                extra=dto_obj.metadata,
            )
            domain.created_at = dto_obj.created_at
            domain.processed_at = dto_obj.processed_at
            domain.indexed_at = dto_obj.indexed_at
            domain._status = dto_obj.status
            return domain
        except Exception as e:
            logger.error(
                "DocumentMapper.from_dto failed for %r", dto_obj, exc_info=True
            )
            raise DtoToDomainError(
                f"DTO→Domain failed for document {dto_obj.id}"
            ) from e

    def to_orm(
        self, domain_obj: DomainDocument, orm_obj: Optional[ORMDocument] = None
    ) -> ORMDocument:
        """Convert a DomainDocument to an ORMDocument.

        Args:
            domain_obj (DomainDocument): The domain document to convert.
            orm_obj (ORMDocument, optional): An existing ORM document to update. If None, creates a new one.

        Returns:
            ORMDocument: The resulting ORM document.

        Raises:
            DomainToOrmError: If conversion fails.
        """
        try:
            orm = orm_obj or ORMDocument()
            orm.id = domain_obj.id
            orm.file_name = domain_obj.file_name
            orm.created_at = domain_obj.created_at
            orm.processed_at = domain_obj.processed_at
            orm.indexed_at = domain_obj.indexed_at
            orm.status = domain_obj.status
            orm.extra = domain_obj.extra
            orm.pages = [PageMapper().to_orm(p, orm) for p in domain_obj.pages]
            return orm
        except Exception as e:
            logger.error(
                "DocumentMapper.to_orm failed for %r", domain_obj, exc_info=True
            )
            raise DomainToOrmError(
                f"Domain→ORM failed for document {domain_obj.id}"
            ) from e

    def from_orm(self, orm_obj: ORMDocument) -> DomainDocument:
        """Convert an ORMDocument to a DomainDocument.

        Args:
            orm_obj (ORMDocument): The ORM document to convert.

        Returns:
            DomainDocument: The resulting domain document.

        Raises:
            OrmToDomainError: If conversion fails.
        """
        try:
            pages = [PageMapper().from_orm(p) for p in orm_obj.pages]
            domain = DomainDocument(
                doc_id=orm_obj.id,
                file_name=orm_obj.file_name,
                pages=pages,
                extra=orm_obj.extra,
            )
            domain.created_at = orm_obj.created_at
            domain.processed_at = orm_obj.processed_at
            domain.indexed_at = orm_obj.indexed_at
            domain._status = orm_obj.status
            return domain
        except Exception as e:
            logger.error(
                "DocumentMapper.from_orm failed for %r", orm_obj, exc_info=True
            )
            raise OrmToDomainError(
                f"ORM→Domain failed for document {orm_obj.id}"
            ) from e

    def to_minimal_dto(self, domain_obj: DomainDocument) -> DTOMinimalDocument:
        """Convert a DomainDocument to a DTOMinimalDocument.

        Args:
            domain_obj (DomainDocument): The domain document to convert.

        Returns:
            DTOMinimalDocument: The resulting minimal DTO document.

        Raises:
            DomainToDtoError: If conversion fails.
        """
        try:
            min_dom = domain_obj.to_minimal()
            return DTOMinimalDocument.model_validate(
                {
                    "id": min_dom.id,
                    "status": min_dom.status,
                    "updated_at": min_dom.updated_at,
                }
            )
        except Exception as e:
            logger.error(
                "DocumentMapper.to_minimal_dto failed for %r", domain_obj, exc_info=True
            )
            raise DomainToDtoError(
                f"Domain→DTO failed for minimal document {domain_obj.id}"
            ) from e

    def from_minimal_dto(self, dto_obj: DTOMinimalDocument) -> DomainMinDocument:
        """Convert a DTOMinimalDocument to a DomainMinDocument.

        Args:
            dto_obj (DTOMinimalDocument): The minimal DTO document to convert.

        Returns:
            DomainMinDocument: The resulting minimal domain document.

        Raises:
            DtoToDomainError: If conversion fails.
        """
        try:
            return DomainMinDocument(
                id=dto_obj.id,
                status=dto_obj.status,
                updated_at=dto_obj.updated_at,
            )
        except Exception as e:
            logger.error(
                "DocumentMapper.from_minimal_dto failed for %r", dto_obj, exc_info=True
            )
            raise DtoToDomainError(
                f"DTO→Domain failed for minimal document {dto_obj.id}"
            ) from e
