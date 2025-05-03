#!/usr/bin/env python3
import argparse
import csv
import logging
import shutil
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm


# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ───────── Utility Functions ─────────


def subset_pdf(input_pdf: Path, num_pages: int, output_pdf: Path):
    """Extract the first `num_pages` pages into output_pdf."""
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    for page in reader.pages[:num_pages]:
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)


def clear_dir(dirpath: Path):
    """Remove and recreate a directory."""
    if dirpath.exists():
        shutil.rmtree(dirpath)
        dirpath.mkdir(parents=True, exist_ok=True)


# ───────── Conversion Functions ─────────


def convert_baseline(pdf_path: Path, dpi: int, fmt: str, out_dir: Path) -> float:
    start = time.perf_counter()
    convert_from_path(
        str(pdf_path),
        dpi=dpi,
        fmt=fmt,
        output_folder=str(out_dir),
        thread_count=1,
        paths_only=True,
    )
    return time.perf_counter() - start


def convert_threaded(
    pdf_path: Path, dpi: int, fmt: str, out_dir: Path, thread_count: int
) -> float:
    start = time.perf_counter()
    convert_from_path(
        str(pdf_path),
        dpi=dpi,
        fmt=fmt,
        output_folder=str(out_dir),
        thread_count=thread_count,
        paths_only=True,
    )
    return time.perf_counter() - start


# ───────── Process Pool Worker ─────────


def _convert_single_page(page_pdf: Path, dpi: int, fmt: str, out_dir: Path):
    convert_from_path(
        str(page_pdf),
        dpi=dpi,
        fmt=fmt,
        output_folder=str(out_dir),
        thread_count=1,
        paths_only=True,
    )


def convert_process_pool(
    pdf_path: Path, dpi: int, fmt: str, out_dir: Path, max_workers: int
) -> float:
    # Split into one-page PDFs
    temp_dir = Path(tempfile.mkdtemp())
    reader = PdfReader(str(pdf_path))
    page_files = []
    for idx, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        page_pdf = temp_dir / f"page_{idx}.pdf"
        with open(page_pdf, "wb") as f:
            writer.write(f)
            page_files.append(page_pdf)

    # Parallel conversion via top-level worker
    worker = partial(_convert_single_page, dpi=dpi, fmt=fmt, out_dir=out_dir)
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        list(exe.map(worker, page_files))
        duration = time.perf_counter() - start

    # Clean up
    shutil.rmtree(temp_dir)
    return duration


# ───────── Main Benchmark Logic ─────────


def main():
    configure_logging()
    parser = argparse.ArgumentParser(description="Benchmark PDF→image conversion modes")
    parser.add_argument("pdf", type=Path, help="Source PDF file")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Max pages to test (default=full length)",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=None,
        help="Page-count increment (default=total_pages//10)",
    )
    parser.add_argument(
        "--thread-counts",
        type=int,
        nargs="+",
        default=[2, 4, 8],
        help="Thread counts to try",
    )
    parser.add_argument(
        "--process-counts",
        type=int,
        nargs="+",
        default=[2, 4, 8],
        help="Process counts to try",
    )
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--fmt", type=str, default="jpg")
    parser.add_argument("--runs", type=int, default=3, help="Repetitions per test")
    parser.add_argument(
        "--csv-out", type=Path, default=Path("results.csv"), help="CSV output path"
    )
    args = parser.parse_args()

    # Determine page count settings
    reader = PdfReader(str(args.pdf))
    total_pages = len(reader.pages)
    max_pages = args.max_pages or total_pages
    step = args.step or max(1, max_pages // 10)
    page_counts = list(range(step, max_pages + 1, step))

    # Open CSV for writing
    with open(args.csv_out, "w", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(["pages", "mode", "workers", "run_index", "time_s"])

        # Iterate with progress bar
        for pages in tqdm(page_counts, desc="Page subsets", unit="batch"):
            # Create subset PDF
            with tempfile.TemporaryDirectory() as td:
                subset = Path(td) / f"{args.pdf.stem}_{pages}.pdf"
                subset_pdf(args.pdf, pages, subset)
                out_dir = Path(td) / "out"
                out_dir.mkdir()

                # Baseline
                for run in range(1, args.runs + 1):
                    clear_dir(out_dir)
                    logging.info(f"[BASELINE] pages={pages}, run={run}")
                    t = convert_baseline(subset, args.dpi, args.fmt, out_dir)
                    writer.writerow([pages, "baseline", 1, run, f"{t:.4f}"])

                # Threaded
                for tc in args.thread_counts:
                    for run in range(1, args.runs + 1):
                        clear_dir(out_dir)
                        logging.info(
                            f"[THREADED] pages={pages}, threads={tc}, run={run}"
                        )
                        t = convert_threaded(subset, args.dpi, args.fmt, out_dir, tc)
                        writer.writerow([pages, "threaded", tc, run, f"{t:.4f}"])

                # Process pool
                for pc in args.process_counts:
                    for run in range(1, args.runs + 1):
                        clear_dir(out_dir)
                        logging.info(f"[PROCESS] pages={pages}, procs={pc}, run={run}")
                        t = convert_process_pool(
                            subset, args.dpi, args.fmt, out_dir, pc
                        )
                        writer.writerow([pages, "process", pc, run, f"{t:.4f}"])

    logging.info(f"Benchmark complete — results written to {args.csv_out}")


if __name__ == "__main__":
    main()
