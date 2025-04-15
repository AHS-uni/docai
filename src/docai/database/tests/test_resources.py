import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional, Any, Dict


from docai.models.query import Query, QueryStatus
from docai.models.document import Document, Page, DocumentStatus


# -------------------- Synthetic Data Creation --------------------


def create_synthetic_documents() -> List[Document]:
    """
    Create synthetic Document objects with associated Page objects and perform status transitions.

    Returns:
        List[Document]: A list of synthetic Document objects.
    """
    documents = []
    # Create 5 Document objects
    for i in range(1, 6):
        doc_id = f"doc{i}"
        file_name = f"document{i}.pdf"
        # Create at least 2 pages per document
        pages = []
        for page_number in range(1, 3):  # Two pages per document
            page_id = f"{doc_id}_page{page_number}"
            image_path = f"images/{doc_id}_page{page_number}.jpg"
            pages.append(
                Page(page_id=page_id, page_number=page_number, image_path=image_path)
            )

        metadata = {"title": f"Sample Document {i}", "author": f"Author {i}"}
        document = Document(
            doc_id=doc_id, file_name=file_name, pages=pages, metadata=metadata
        )

        # Perform valid status transitions for the document:
        # CREATED -> PROCESSED -> INDEXED
        try:
            document.status = DocumentStatus.PROCESSED
            document.status = DocumentStatus.INDEXED
        except ValueError as e:
            print(f"Error updating document status for {doc_id}: {e}")

        documents.append(document)
    return documents


def create_synthetic_queries(document_ids: List[str]) -> List[Query]:
    """
    Create synthetic Query objects that reference real Document ids and perform status transitions.

    Args:
        document_ids (List[str]): A list of valid Document ids to be targeted by queries.

    Returns:
        List[Query]: A list of synthetic Query objects.
    """
    queries = []

    query1 = Query(
        query_id="query1",
        text="Find documents authored by Author 1 or Author 2.",
        target_document_ids=document_ids[:3],
        metadata={"priority": "high"},
    )
    try:
        query1.status = QueryStatus.PROCESSED
        query1.status = QueryStatus.INDEXED
        query1.status = QueryStatus.CONTEXT_RETRIEVED
        query1.status = QueryStatus.ANSWERED
        query1.answer = "Dummy answer: Documents by Author 1 or Author 2 found."
    except ValueError as e:
        print(f"Error updating query status for query1: {e}")

    queries.append(query1)

    query2 = Query(
        query_id="query2",
        text="Retrieve documents containing the keyword 'Sample'.",
        target_document_ids=document_ids[-3:],
        metadata={"priority": "medium"},
    )
    try:
        query2.status = QueryStatus.PROCESSED
        query2.status = QueryStatus.INDEXED
        query2.status = QueryStatus.CONTEXT_RETRIEVED
        query2.status = QueryStatus.ANSWERED
        query2.answer = (
            "Dummy answer: Documents containing 'Sample' were successfully retrieved."
        )
    except ValueError as e:
        print(f"Error updating query status for query2: {e}")

    queries.append(query2)

    return queries


if __name__ == "__main__":
    documents = create_synthetic_documents()
    document_ids = [doc.id for doc in documents]
    queries = create_synthetic_queries(document_ids)

    print("Synthetic Documents:")
    for doc in documents:
        print(json.dumps(doc.to_dict(), indent=4))

    print("\nSynthetic Queries:")
    for query in queries:
        print(json.dumps(query.to_dict(), indent=4))
