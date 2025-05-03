#!/usr/bin/env bash
#SBATCH --job-name=storage_test
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/cluster/users/hlwn057u2/data/logs/slurm/storage_test_%j.log
#SBATCH --error=/cluster/users/hlwn057u2/data/logs/slurm/storage_test_%j.err

set -euxo pipefail

module load Anaconda3
eval "$(conda shell.bash hook)"
conda activate "/cluster/users/hlwn057u2/.conda/envs/dev-env"

# Define paths
PROJECT_ROOT="/cluster/users/hlwn057u2/data/docai"
SHARED_DIR="/cluster/users/hlwn057u2/data"
ADDR_FILE="${SHARED_DIR}/storage.addr"
PDF_FILE="${PROJECT_ROOT}/tests/resources/sample_1.pdf"

# cd into project
cd "$PROJECT_ROOT"

# Wait up to 5 minutes for storage.addr to appear
echo "[test] waiting for address file $ADDR_FILE"
for i in {1..60}; do
    if [[ -s "$ADDR_FILE" ]]; then
        echo "[test] found address file on attempt $i"
        break
    fi
    echo "[$(date +%T)] still waiting… ($i/60)"
    sleep 5
done
if [[ ! -s "$ADDR_FILE" ]]; then
    echo "[test][ERROR] $ADDR_FILE not found after 5 min" >&2
    exit 1
fi

storage_addr=$(<"$ADDR_FILE")
echo "[test] discovered storage addr = $storage_addr"

# Verify the PDF exists
if [[ ! -f "$PDF_FILE" ]]; then
    echo "[test][ERROR] PDF not found at $PDF_FILE" >&2
    exit 1
fi
size=$(stat -c%s "$PDF_FILE")
echo "[test] PDF size is $size bytes"

# Run the Python client — note ARG BEFORE EOF
echo "[test] launching client against $storage_addr"
set -x
poetry run python scripts/storage_test.py "$storage_addr"
