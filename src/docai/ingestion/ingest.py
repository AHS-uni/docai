import time
import logging
from pathlib import Path
from typing import Dict, Any

from docai.ingestion.pdf_to_jpg import convert_pdf_to_images
from docai.ingestion.id_generator import generate_id
from docai.ingestion.models import Document, PageImage, DocumentStatus
from docai.config import load_environment, load_config
from docai.shared.utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)


def process_document(pdf_path: Path, config: Dict[str, Any]) -> Document:
    """
    Process a single PDF document: convert to images, generate IDs, and create a Document model.

    Args:
        pdf_path (Path): Path to the PDF file.
        config (dict): Loaded configuration settings.

    Returns:
        Document: A Document instance with associated PageImage objects.
    """
    logging.info(f"Starting processing for {pdf_path}")
    start_time = time.time()

    image_output_dir: Path = Path(config["ingestion"]["paths"]["image_output_dir"])
    dpi: int = config["ingestion"]["pdf_conversion"]["dpi"]
    quality: int = config["ingestion"]["pdf_conversion"]["quality"]

    try:
        doc_id, image_paths = convert_pdf_to_images(
            pdf_path, image_output_dir, quality=quality, dpi=dpi
        )
        file_name: str = pdf_path.name
        document: Document = Document(doc_id, file_name)

        for i, img_path in enumerate(image_paths):
            page_id: str = generate_id("page")
            page: PageImage = PageImage(page_id, i, img_path)
            document.pages.append(page)

        document.status = DocumentStatus.PROCESSED

        duration: float = time.time() - start_time
        logging.info(
            f"Processed {pdf_path}: {len(image_paths)} pages in {duration:.2f} seconds, assigned Document ID {doc_id}"
        )
        return document
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        raise


def main() -> None:
    """
    Entry point for processing PDF files. Loads environment/configuration,
    sets up logging, processes PDF files in a given directory, and saves the document metadata.
    """
    load_environment()
    config: Dict[str, Any] = load_config()

    setup_logging(config["ingestion"]["paths"]["log_file"])
    logger.info("Started ingestion process")

    input_dir: Path = Path(config["ingestion"]["paths"]["input_dir"])
    metadata_output: Path = Path(config["ingestion"]["paths"]["metadata_output"])

    # SEQUENTIAL PROCESSING. Change to parallel if needed.
    pdf_files: list[Path] = list(input_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in {input_dir}: {pdf_files}")

    if not pdf_files:
        logger.warning("No PDF files found. Exiting.")
        return

    for pdf in pdf_files:
        try:
            document: Document = process_document(pdf, config)
            document.save(metadata_output)
        except Exception as e:
            logger.error(f"Skipping file {pdf} due to error: {e}")

    logger.info("Ingestion process complete.")


if __name__ == "__main__":
    main()
