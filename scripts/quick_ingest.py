import os
import argparse
import logging
from pdf2image import convert_from_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest PDFs and convert to JPEG images."
    )
    parser.add_argument(
        "--input-dir", "-i", required=True, help="Directory containing PDF files."
    )
    parser.add_argument(
        "--dpi", type=int, default=200, help="Resolution in DPI for conversion."
    )
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality (1-100).")
    parser.add_argument(
        "--poppler-path", default=None, help="Path to Poppler binaries (if needed)."
    )
    return parser.parse_args()


def convert_pdfs(input_dir: str, dpi: int, quality: int, poppler_path: str = ""):
    """
    Convert all PDFs in a directory to JPEG images.

    Args:
        input_dir (str): Path to directory containing PDFs.
        dpi (int): Resolution in DPI for PDF conversion.
        quality (int): JPEG quality (1-100).
        poppler_path (str, optional): Path to Poppler binaries. Defaults to None.
    """
    if not os.path.isdir(input_dir):
        logging.error(f"Input directory does not exist: {input_dir}")
        return

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        logging.info(f"Converting {filename}...")

        try:
            images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
        except Exception as e:
            logging.error(f"Failed to convert {filename}: {e}")
            continue

        for idx, image in enumerate(images, start=1):
            out_name = f"{base_name}_p{idx}.jpg"
            out_path = os.path.join(input_dir, out_name)
            try:
                image.save(out_path, format="JPEG", quality=quality)
                logging.info(f"Saved image: {out_name}")
            except Exception as e:
                logging.error(f"Failed to save {out_name}: {e}")


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    args = parse_args()
    convert_pdfs(
        input_dir=args.input_dir,
        dpi=args.dpi,
        quality=args.quality,
        poppler_path=args.poppler_path,
    )


if __name__ == "__main__":
    main()
