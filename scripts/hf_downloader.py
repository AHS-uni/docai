import argparse
import os
import time

from huggingface_hub import HfApi, hf_hub_download


def download_files_individually(repo_id, local_dir, repo_type="dataset", max_retries=3):
    """
    Downloads files from Hugging Face one by one, bypassing snapshot integrity checks.

    Args:
        repo_id (str): Hugging Face repository ID.
        local_dir (str): Local directory to save files.
        repo_type (str): "dataset" or "model".
        max_retries (int): Number of retry attempts.

    Returns:
        None
    """
    api = HfApi()
    print(f"\n🔍 Fetching file list for {repo_type.upper()} '{repo_id}'...")

    # Get the list of all files in the repository
    files = api.list_repo_files(repo_id=repo_id, repo_type=repo_type)

    print(f"📄 Found {len(files)} files. Starting download...\n")

    # Ensure the local directory exists
    os.makedirs(local_dir, exist_ok=True)

    for file in files:
        file_path = os.path.join(local_dir, file)
        attempt = 0

        while attempt < max_retries:
            try:
                print(f"⬇️ Downloading: {file} (Attempt {attempt+1}/{max_retries})")
                hf_hub_download(
                    repo_id=repo_id,
                    filename=file,
                    repo_type=repo_type,
                    local_dir=local_dir,
                    force_download=True,  # Ensures we don't rely on metadata
                )
                print(f"✅ Successfully downloaded: {file}")
                break  # Stop retrying if successful

            except Exception as e:
                attempt += 1
                print(f"❌ Failed to download {file}. Error: {e}")
                if attempt < max_retries:
                    print(f"Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    print(
                        f"🚨 Skipping file after {max_retries} failed attempts: {file}"
                    )

    print("\n🎉 Download process completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a dataset or model from Hugging Face Hub manually."
    )
    parser.add_argument(
        "--repo_id",
        type=str,
        required=True,
        help="Hugging Face repository ID (e.g., 'yubo2333/MMLongBench-Doc')",
    )
    parser.add_argument(
        "--local_dir",
        type=str,
        required=True,
        help="Directory to save the downloaded files",
    )
    parser.add_argument(
        "--repo_type",
        type=str,
        choices=["dataset", "model"],
        default="dataset",
        help="Specify 'dataset' or 'model' (default: dataset)",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=3,
        help="Number of retries on failed downloads",
    )

    args = parser.parse_args()

    # Run the manual file downloader
    download_files_individually(
        repo_id=args.repo_id,
        local_dir=args.local_dir,
        repo_type=args.repo_type,
        max_retries=args.max_retries,
    )
