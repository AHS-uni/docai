class DocumentProcessor:
    async def process(self, raw_document_data):
        # Create and store metadata for the document
        document_metadata = await self._create_document_metadata(raw_document_data)
        await self._store_document_metadata(document_metadata)
        # Convert the document (e.g., PDF to JPG images)
        images = await self._convert_document(raw_document_data)
        await self._store_page_images(images)
        # Push to background queue for further processing
        await self._enqueue_for_processing(raw_document_data)
        return document_metadata

    async def _create_document_metadata(self, raw_data):
        return {"id": "doc123", "status": "created"}

    async def _store_document_metadata(self, metadata):
        # Store document metadata in the database
        pass

    async def _convert_document(self, raw_data):
        # Convert PDF or raw document to images (JPG, PNG, etc.)
        pass

    async def _store_page_images(self, images):
        # Store the images in the database or file system
        pass

    async def _enqueue_for_processing(self, raw_document_data):
        # Push the document to the processing queue
        pass


class QueryProcessor:
    async def process(self, query_data):
        # Create and store metadata for the query
        query_metadata = await self._create_query_metadata(query_data)
        await self._store_query_metadata(query_metadata)
        # Process the query (find associated documents, etc.)
        return query_metadata

    async def _create_query_metadata(self, query_data):
        return {"id": "query123", "status": "created"}

    async def _store_query_metadata(self, metadata):
        # Store query metadata in the database
        pass
