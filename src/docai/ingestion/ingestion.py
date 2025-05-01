from docai.ingestion.services import DocumentProcessor, QueryProcessor


class IngestionService:
    def __init__(
        self, document_processor: DocumentProcessor, query_processor: QueryProcessor
    ):
        self.document_processor = document_processor
        self.query_processor = query_processor

    async def process_document(self, raw_document_data):
        """Ingest a raw document and initiate processing"""
        document = await self.document_processor.process(raw_document_data)
        return document

    async def process_query(self, query_data):
        """Ingest a query and initiate processing"""
        query = await self.query_processor.process(query_data)
        return query
