import logging
from pathlib import Path
from typing import Union


def setup_logging(log_path: Union[str, Path], level: int = logging.INFO) -> None:
    """
    Configure logging for the application.

    Args:
        log_path (str or Path): The file system path where the log file should be created.
        level (int, optional): The logging level threshold. Defaults to logging.INFO.

    Returns:
        None
    """
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_path),
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger().addHandler(logging.StreamHandler())
