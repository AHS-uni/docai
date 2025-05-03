"""
Mapping logic for converting Query objects between Domain, DTO, and ORM representations.

This module defines the QueryMapper class, which handles translation of queries across
different layers of the application, including support for linking documents and pages.
"""

import logging
from typing import Optional

from docai.database.database import DatabaseService
from docai.mapping.base import BaseMapper
from docai.mapping.exceptions import (
    DomainToDtoError,
    DomainToOrmError,
    DtoToDomainError,
    OrmToDomainError,
)
from docai.mapping.utils import link_documents_to_query, link_pages_to_query
from docai.shared.models.domain.query import MinimalQuery as DomainMinQuery
from docai.shared.models.domain.query import Query as DomainQuery
from docai.shared.models.dto.query import MinimalQuery as DTOMinimalQuery
from docai.shared.models.dto.query import Query as DTOQuery
from docai.shared.models.orm.query import Query as ORMQuery

logger = logging.getLogger(__name__)


class QueryMapper(BaseMapper):
    """Mapper for converting between DomainQuery, DTOQuery, and ORMQuery."""

    def to_dto(self, domain_obj: DomainQuery) -> DTOQuery:
        """Convert a DomainQuery to a DTOQuery.

        Args:
            domain_obj (DomainQuery): The domain query to convert.

        Returns:
            DTOQuery: The resulting DTO query.

        Raises:
            DomainToDtoError: If conversion fails.
        """
        try:
            data = {
                "id": domain_obj.id,
                "text": domain_obj.text,
                "target_document_ids": domain_obj.target_document_ids,
                "context_page_ids": domain_obj.context_page_ids or [],
                "metadata": domain_obj.extra,
                "answer": domain_obj.answer,
                "created_at": domain_obj.created_at,
                "processed_at": domain_obj.processed_at,
                "indexed_at": domain_obj.indexed_at,
                "context_retrieved_at": domain_obj.context_retrieved_at,
                "answered_at": domain_obj.answered_at,
                "status": domain_obj.status,
            }
            return DTOQuery.model_validate(data)
        except Exception as e:
            logger.error("QueryMapper.to_dto failed for %r", domain_obj, exc_info=True)
            raise DomainToDtoError(
                f"Domain→DTO failed for query {domain_obj.id}"
            ) from e

    def from_dto(self, dto_obj: DTOQuery) -> DomainQuery:
        """Convert a DTOQuery to a DomainQuery.

        Args:
            dto_obj (DTOQuery): The DTO query to convert.

        Returns:
            DomainQuery: The resulting domain query.

        Raises:
            DtoToDomainError: If conversion fails.
        """
        try:
            domain = DomainQuery(
                query_id=dto_obj.id,
                text=dto_obj.text,
                target_document_ids=dto_obj.target_document_ids,
                extra=dto_obj.metadata,
            )
            domain.context_page_ids = dto_obj.context_page_ids
            domain.answer = dto_obj.answer
            domain.created_at = dto_obj.created_at
            domain.processed_at = dto_obj.processed_at
            domain.indexed_at = dto_obj.indexed_at
            domain.context_retrieved_at = dto_obj.context_retrieved_at
            domain.answered_at = dto_obj.answered_at
            domain._status = dto_obj.status
            return domain
        except Exception as e:
            logger.error("QueryMapper.from_dto failed for %r", dto_obj, exc_info=True)
            raise DtoToDomainError(f"DTO→Domain failed for query {dto_obj.id}") from e

    def to_orm(
        self,
        domain_obj: DomainQuery,
        db_service: DatabaseService,
        orm_obj: Optional[ORMQuery] = None,
    ) -> ORMQuery:
        """Convert a DomainQuery to an ORMQuery.

        Args:
            domain_obj (DomainQuery): The domain query to convert.
            db_service (DatabaseService): Used to fetch and link documents/pages.
            orm_obj (Optional[ORMQuery]): An existing ORM query to update. Creates a new one if None.

        Returns:
            ORMQuery: The resulting ORM query.

        Raises:
            DomainToOrmError: If conversion fails.
        """
        try:
            orm = orm_obj or ORMQuery()
            orm.id = domain_obj.id
            orm.text = domain_obj.text
            orm.created_at = domain_obj.created_at
            orm.processed_at = domain_obj.processed_at
            orm.indexed_at = domain_obj.indexed_at
            orm.context_retrieved_at = domain_obj.context_retrieved_at
            orm.answered_at = domain_obj.answered_at
            orm.status = domain_obj.status
            orm.extra = domain_obj.extra
            orm.answer = domain_obj.answer

            # link both documents and pages
            orm = link_documents_to_query(
                db_service, orm, domain_obj.target_document_ids
            )
            orm = link_pages_to_query(
                db_service, orm, domain_obj.context_page_ids or []
            )
            return orm
        except Exception as e:
            logger.error("QueryMapper.to_orm failed for %r", domain_obj, exc_info=True)
            raise DomainToOrmError(
                f"Domain→ORM failed for query {domain_obj.id}"
            ) from e

    def from_orm(self, orm_obj: ORMQuery) -> DomainQuery:
        """Convert an ORMQuery to a DomainQuery.

        Args:
            orm_obj (ORMQuery): The ORM query to convert.

        Returns:
            DomainQuery: The resulting domain query.

        Raises:
            OrmToDomainError: If conversion fails.
        """
        try:
            domain = DomainQuery(
                query_id=orm_obj.id,
                text=orm_obj.text,
                target_document_ids=[d.id for d in orm_obj.documents],
                extra=orm_obj.extra,
            )
            domain.context_page_ids = [p.id for p in orm_obj.pages]
            domain.answer = orm_obj.answer
            domain.created_at = orm_obj.created_at
            domain.processed_at = orm_obj.processed_at
            domain.indexed_at = orm_obj.indexed_at
            domain.context_retrieved_at = orm_obj.context_retrieved_at
            domain.answered_at = orm_obj.answered_at
            domain._status = orm_obj.status
            return domain
        except Exception as e:
            logger.error("QueryMapper.from_orm failed for %r", orm_obj, exc_info=True)
            raise OrmToDomainError(f"ORM→Domain failed for query {orm_obj.id}") from e

    def to_minimal_dto(self, domain_obj: DomainQuery) -> DTOMinimalQuery:
        """Convert a DomainQuery to a DTOMinimalQuery.

        Args:
            domain_obj (DomainQuery): The domain query to convert.

        Returns:
            DTOMinimalQuery: The resulting minimal DTO query.

        Raises:
            DomainToDtoError: If conversion fails.
        """
        try:
            min_dom = domain_obj.to_minimal()
            return DTOMinimalQuery.model_validate(
                {
                    "id": min_dom.id,
                    "status": min_dom.status,
                    "updated_at": min_dom.updated_at,
                }
            )
        except Exception as e:
            logger.error(
                "QueryMapper.to_minimal_dto failed for %r", domain_obj, exc_info=True
            )
            raise DomainToDtoError(
                f"Domain→DTO failed for minimal query {domain_obj.id}"
            ) from e

    def from_minimal_dto(self, dto_obj: DTOMinimalQuery) -> DomainMinQuery:
        """Convert a DTOMinimalQuery to a DomainMinQuery.

        Args:
            dto_obj (DTOMinimalQuery): The minimal DTO query to convert.

        Returns:
            DomainMinQuery: The resulting minimal domain query.

        Raises:
            DtoToDomainError: If conversion fails.
        """
        try:
            return DomainMinQuery(
                id=dto_obj.id, status=dto_obj.status, updated_at=dto_obj.updated_at
            )
        except Exception as e:
            logger.error(
                "QueryMapper.from_minimal_dto failed for %r", dto_obj, exc_info=True
            )
            raise DtoToDomainError(
                f"DTO→Domain failed for minimal query {dto_obj.id}"
            ) from e
