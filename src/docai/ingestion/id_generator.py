import uuid


def generate_id(prefix: str = "doc") -> str:
    """
    Generate a universally unique identifier with an optional prefix.

    Args:
        prefix (str): A prefix string to easily identify the type (e.g., "doc", "page").

    Returns:
        str: A unique identifier string.
    """
    return f"{prefix}_{uuid.uuid4()}"
