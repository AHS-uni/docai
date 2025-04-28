from typing import Any, Dict


class DocumentFactory:
    """Build in‐memory domain objects for a new document."""

    def create_from_request(self, req: DocumentIngestRequest) -> Dict[str, Any]:
        """Instantiate a new Document domain object.

        Args:
            req: The parsed ingestion request.

        Returns:
            A dict (or real Document model) with fields:
            - id: str
            - file_name: str
            - pages: List[...] (empty for now)
            - state: str = "created"
            - created_at: datetime
        """

    pass


class QueryFactory:
    pass
