import logging
from typing import Tuple, List
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image

from docai.ingestion.id_generator import generate_id

# Disable image size limits to handle large PDFs
Image.MAX_IMAGE_PIXELS = None

logger = logging.getLogger(__name__)


def convert_pdf_to_images(
    pdf_path: Path, output_dir: Path, quality: int = 95, dpi: int = 300
) -> Tuple[str, List[str]]:
    """
    Convert a single PDF document into JPG images.

    Args:
        pdf_path (Path): Absolute path to the PDF file.
        output_dir (Path): Directory where JPG images will be saved.
        quality (int): JPEG quality (1-100). Default is 95.
        dpi (int): Resolution in DPI for the conversion. Default is 300.

    Returns:
        tuple: A tuple (doc_id, image_paths) where:
            - doc_id (str): The document identifier (derived from the PDF filename).
            - image_paths (List[str]): A list of absolute paths to the generated image files.
    """
    doc_id: str = generate_id("doc")
    output_dir.mkdir(parents=True, exist_ok=True)

    pages = []

    try:
        logger.info(
            f"Converting PDF: {pdf_path} with DPI: {dpi} and Quality: {quality}"
        )
        # Convert PDF pages to a list of PIL Image objects
        pages = convert_from_path(str(pdf_path), dpi=dpi)
    except Exception as e:
        logger.error(f"Error converting PDF '{pdf_path}' to images: {e}")

    image_paths: List[str] = []
    for i, page_img in enumerate(pages):
        output_filename: str = f"{doc_id}_p{i}.jpg"
        output_path: Path = output_dir / output_filename
        page_img.save(str(output_path), "JPEG", quality=quality)
        image_paths.append(str(output_path))

    return doc_id, image_paths


if __name__ == "__main__":
    import argparse

    def parse_arguments() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Convert a PDF to JPG images.")
        parser.add_argument(
            "--pdf_path", required=True, help="Path to the PDF file to be processed."
        )
        parser.add_argument(
            "--output_dir",
            required=True,
            help="Directory to store the output JPG images.",
        )
        parser.add_argument(
            "--quality",
            type=int,
            default=95,
            help="JPEG quality (1-100). Default is 95.",
        )
        parser.add_argument(
            "--dpi",
            type=int,
            default=300,
            help="Resolution in DPI for the conversion. Default is 300.",
        )
        return parser.parse_args()

    args = parse_arguments()
    doc_id, images = convert_pdf_to_images(
        Path(args.pdf_path), Path(args.output_dir), quality=args.quality, dpi=args.dpi
    )
    print(f"Document {doc_id} processed with {len(images)} pages.")
