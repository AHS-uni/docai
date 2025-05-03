#!/usr/bin/env python
import asyncio, pathlib, sys, traceback
from docai.storage.client import StorageClient


def main():
    if len(sys.argv) != 2:
        print("Usage: smoke_storage_test.py <host:port>", file=sys.stderr)
        sys.exit(1)
    endpoint = sys.argv[1]
    pdf = pathlib.Path("tests/resources/sample_1.pdf")  # or your real path
    print("[py] sys.argv:", sys.argv)
    print(f"[py] PDF exists? {pdf.exists()}, size={pdf.stat().st_size}")

    async def smoke():
        print(f"[py] uploading to http://{endpoint}")
        async with StorageClient(f"http://{endpoint}") as client:
            await client.save_pdf("real_doc", pdf)
            print("✓ uploaded real PDF")
            await client.delete_document("real_doc")
            print("✓ deleted real PDF")

    try:
        asyncio.run(smoke())
    except Exception:
        print("[py][ERROR] exception in smoke()", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
