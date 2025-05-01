from pathlib import Path
from typing import List, Optional
import asyncio
from concurrent.futures import ProcessPoolExecutor
from pypdf import PdfReader

from docai.ingestion.config import (
    CONVERSION_OUTPUT_DIR,
    MAX_FILE_SIZE_MB,
    PAGE_THRESHOLD,
)
from docai.ingestion.workers import (
    _sync_convert_parallel_pages,
    _sync_convert_sequential,
)
from docai.ingestion.exceptions import ConversionError


class Converter:
    """
    Orchestrates PDF-to-image conversion by dispatching
    either a sequential or page-parallel worker in its own process.
    """

    def __init__(
        self,
        output_dir: Path = CONVERSION_OUTPUT_DIR,
        max_file_size_mb: float = MAX_FILE_SIZE_MB,
        max_workers: int = 2,
        parallel_page_threshold: int = PAGE_THRESHOLD,
    ):
        self.output_dir = output_dir
        self.max_file_size_mb = max_file_size_mb
        self.parallel_page_threshold = parallel_page_threshold
        self._executor = ProcessPoolExecutor(max_workers=max_workers)

    async def convert_pdf(
        self,
        pdf_path: Path,
        filename_prefix: Optional[str] = None,
        fmt: str = "JPEG",
    ) -> List[Path]:
        # --- validations ---
        if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
            raise ConversionError(f"Invalid PDF file: {pdf_path}")
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            raise ConversionError(
                f"PDF exceeds max size of {self.max_file_size_mb} MB: {size_mb:.2f} MB"
            )

        # --- page count ---
        reader = PdfReader(str(pdf_path))
        num_pages = len(reader.pages)

        # --- choose worker ---
        worker = (
            _sync_convert_sequential
            if num_pages <= self.parallel_page_threshold
            else _sync_convert_parallel_pages
        )

        # --- prepare output dir ---
        prefix = filename_prefix or pdf_path.stem
        doc_out = self.output_dir / prefix

        # --- dispatch to process ---
        loop = asyncio.get_running_loop()
        str_paths: List[str] = await loop.run_in_executor(
            self._executor,
            worker,
            str(pdf_path),
            str(doc_out),
            fmt,
        )

        return [Path(p) for p in str_paths]
