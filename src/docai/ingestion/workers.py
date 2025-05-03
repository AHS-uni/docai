"""
PDF conversion workers for ingestion.

This module defines functions for converting PDFs to image sequences, either
sequentially or using parallel page-level processing.
"""

from pathlib import Path
from typing import List

from pdf2image import convert_from_path

from docai.ingestion.config import (
    CONVERSION_DPI,
    CONVERSION_QUALITY,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
)
from docai.ingestion.exceptions import ConversionError


def _sync_convert_sequential(
    pdf_path: str,
    output_dir: str,
    dpi: int = CONVERSION_DPI,
    quality: int = CONVERSION_QUALITY,
    width: int = IMAGE_WIDTH,
    height: int = IMAGE_HEIGHT,
    fmt: str = "JPEG",
) -> List[str]:
    """Convert a PDF into image files sequentially using pdf2image.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory to save the output images.
        dpi (int): Resolution for conversion (dots per inch).
        quality (int): JPEG quality (0–100).
        width (int): Output image width in pixels.
        height (int): Output image height in pixels.
        fmt (str): Image format (e.g., "JPEG").

    Returns:
        List[str]: Paths to the converted image files.

    Raises:
        ConversionError: If the conversion fails.
    """

    pdf = Path(pdf_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        images = convert_from_path(str(pdf), dpi=dpi, fmt=fmt)
    except Exception as e:
        raise ConversionError(f"Failed to convert PDF: {e}")

    paths: List[str] = []
    for i, img in enumerate(images, start=1):
        dest = out / f"{pdf.stem}_p{i}.{fmt.lower()}"
        img = img.resize((width, height))
        img.save(dest, fmt, quality=quality)
        paths.append(str(dest))
    return paths


def _sync_convert_parallel_pages(
    pdf_path: str,
    output_dir: str,
    dpi: int = CONVERSION_DPI,
    quality: int = CONVERSION_QUALITY,
    width: int = IMAGE_WIDTH,
    height: int = IMAGE_HEIGHT,
    fmt: str = "JPEG",
) -> List[str]:
    """
    Placeholder for page-level parallel conversion logic.
    To be implemented: fan-out each page conversion into its own task.
    """
    raise NotImplementedError("Page-level parallel conversion is not implemented yet.")
