#!/bin/bash
#SBATCH --job-name=storage
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=/cluster/users/hlwn057u2/data/logs/slurm/storage_%j.log
#SBATCH --error=/cluster/users/hlwn057u2/data/logs/slurm/storage_%j.err

set -euo pipefail          # <- added -u and -o pipefail for safety

module load Anaconda3
eval "$(conda shell.bash hook)"
conda activate "/cluster/users/hlwn057u2/.conda/envs/dev-env"

cd /cluster/users/hlwn057u2/data/docai/

# Pick a high port and publish the address (FIXED: typo in username)
export STORAGE_PORT=$((7000 + RANDOM % 1000))
export STORAGE_HOST=$(hostname -f)
echo "${STORAGE_HOST}:${STORAGE_PORT}" \
     >  "/cluster/users/hlwn057u2/data/storage.addr"

echo "[storage] starting uvicorn on ${STORAGE_HOST}:${STORAGE_PORT}"
exec poetry run uvicorn docai.storage.api:app \
     --host 0.0.0.0 \
     --port "${STORAGE_PORT}"
