from abc import ABC, abstractmethod


class BaseMapper(ABC):
    """
    Abstract base class for all mappers.
    Defines a uniform interface for Domain<->DTO and Domain<->ORM conversions.
    """

    @abstractmethod
    def to_dto(self, domain_obj):
        raise NotImplementedError

    @abstractmethod
    def from_dto(self, dto_obj):
        raise NotImplementedError

    @abstractmethod
    def to_orm(self, domain_obj, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def from_orm(self, orm_obj):
        raise NotImplementedError
