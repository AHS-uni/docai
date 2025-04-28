"""
Mapping logic for converting Page objects between Domain, DTO, and ORM representations.

This module defines the PageMapper class, which provides methods to translate
pages across different layers of the application: Domain models, ORM models, and
DTOs used for API communication.
"""

import logging

from docai.shared.models.domain.page import Page as DomainPage
from docai.shared.models.orm.page import Page as ORMPage
from docai.shared.models.dto.page import Page as DTOPage
from docai.mapping.base import BaseMapper
from docai.mapping.exceptions import (
    DomainToDtoError,
    DtoToDomainError,
    DomainToOrmError,
    OrmToDomainError,
)

logger = logging.getLogger(__name__)


class PageMapper(BaseMapper):
    """Mapper for converting between DomainPage, DTOPage, and ORMPage."""

    def to_dto(self, domain_obj: DomainPage) -> DTOPage:
        """Convert a DomainPage to a DTOPage.

        Args:
            domain_obj (DomainPage): The domain page instance to convert.

        Returns:
            DTOPage: The resulting DTO page instance.

        Raises:
            DomainToDtoError: If conversion fails.
        """
        try:
            data = domain_obj.to_dict()
            return DTOPage.model_validate(data)
        except Exception as e:
            logger.error("PageMapper.to_dto failed for %r", domain_obj, exc_info=True)
            raise DomainToDtoError(f"Domain→DTO failed for page {domain_obj.id}") from e

    def from_dto(self, dto_obj: DTOPage) -> DomainPage:
        """Convert a DTOPage to a DomainPage.

        Args:
            dto_obj (DTOPage): The DTO page instance to convert.

        Returns:
            DomainPage: The resulting domain page instance.

        Raises:
            DtoToDomainError: If conversion fails.
        """
        try:
            return DomainPage(
                page_id=dto_obj.id,
                page_number=dto_obj.page_number,
                image_path=dto_obj.image_path,
            )
        except Exception as e:
            logger.error("PageMapper.from_dto failed for %r", dto_obj, exc_info=True)
            raise DtoToDomainError(f"DTO→Domain failed for page {dto_obj.id}") from e

    def to_orm(self, domain_obj: DomainPage, orm_obj: ORMPage | None = None) -> ORMPage:
        """Convert a DomainPage to an ORMPage.

        Args:
            domain_obj (DomainPage): The domain page instance to convert.
            orm_obj (Optional[ORMPage]): An existing ORM page to update. If None, a new ORMPage is created.

        Returns:
            ORMPage: The resulting ORM page instance.

        Raises:
            DomainToOrmError: If conversion fails.
        """
        try:
            orm = orm_obj or ORMPage()
            orm.id = domain_obj.id
            orm.page_number = domain_obj.page_number
            orm.image_path = domain_obj.image_path
            return orm
        except Exception as e:
            logger.error("PageMapper.to_orm failed for %r", domain_obj, exc_info=True)
            raise DomainToOrmError(f"Domain→ORM failed for page {domain_obj.id}") from e

    def from_orm(self, orm_obj: ORMPage) -> DomainPage:
        """Convert an ORMPage to a DomainPage.

        Args:
            orm_obj (ORMPage): The ORM page instance to convert.

        Returns:
            DomainPage: The resulting domain page instance.

        Raises:
            OrmToDomainError: If conversion fails.
        """
        try:
            return DomainPage(
                page_id=orm_obj.id,
                page_number=orm_obj.page_number,
                image_path=orm_obj.image_path,
            )
        except Exception as e:
            logger.error("PageMapper.from_orm failed for %r", orm_obj, exc_info=True)
            raise OrmToDomainError(f"ORM→Domain failed for page {orm_obj.id}") from e
