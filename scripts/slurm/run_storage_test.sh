#!/bin/bash
#SBATCH --job-name=storage_test
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=/cluster/users/hlwn057u2/data/logs/slurm/storage_test_%j.log
#SBATCH --error=/cluster/users/hlwn057u2/data/logs/slurm/storage_test_%j.err

set -euo pipefail

module load Anaconda3
eval "$(conda shell.bash hook)"
conda activate "/cluster/users/hlwn057u2/.conda/envs/dev-env"

cd /cluster/users/hlwn057u2/data/docai/

ADDR_FILE="/cluster/users/hlwn057u2/data/storage.addr"   # typo fixed

for i in {1..60}; do
    [[ -f "$ADDR_FILE" ]] && break
    echo "[$(date +%T)] waiting for storage.addr …"
    sleep 5
done

if [[ ! -f "$ADDR_FILE" ]]; then      # <nice-to-have graceful abort>
    echo "ERROR: storage.addr not found after 5 min" >&2
    exit 1
fi

storage_addr=$(cat "$ADDR_FILE")
echo "[test] discovered storage addr = $storage_addr"

poetry run python - <<'PY' "$storage_addr"
import asyncio, tempfile, pathlib, sys
from docai.storage.client import StorageClient

async def smoke(endpoint: str):
    pdf = pathlib.Path(tempfile.gettempdir()) / "dummy.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj<>endobj\nxref\n0 1\n0000000000 65535 f\n%%EOF")
    async with StorageClient(f"http://{endpoint}") as client:
        await client.save_pdf("smoke_doc", pdf)
        print("✓ uploaded PDF")
        await client.delete_document("smoke_doc")
        print("✓ deleted PDF")

asyncio.run(smoke(sys.argv[1]))
PY
