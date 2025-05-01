#!/bin/bash
#SBATCH --job-name=pdf_benchmark
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/cluster/users/hlwn057u2/data/logs/slurm/pdf_benchmark_%j.log
#SBATCH --error=/cluster/users/hlwn057u2/data/logs/slurm/pdf_benchmark_%j.err

# Exit immediately on error
set -e

# Load and activate conda environment
module load Anaconda3
eval "$(conda shell.bash hook)"
conda activate "/cluster/users/hlwn057u2/.conda/envs/poetry_env"

# Navigate to working directory
cd /cluster/users/hlwn057u2/data/docai/

# Run python script
poetry run python scripts/pdf_benchmark_conversion.py data/pdfs/dr-vorapptchapter1emissionsources-121120210508-phpapp02_95.pdf \
       --max-pages 190 \
       --step 10 \
       --thread-counts 2 4 8 16 24 \
       --process-counts 2 4 8 16 24 \
       --runs 2 \
       --csv-out dumps/pdf_benchmark_results.csv
