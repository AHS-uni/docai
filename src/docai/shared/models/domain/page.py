from typing import Any, Dict


class Page:
    """
    Represents a single page of a document.

    Attributes:
        id (str): Unique identifier for the page.
        page_number (int): Page index within the document.
        image_path (str): File path to the JPG image of the page.
    """

    def __init__(self, page_id: str, page_number: int, image_path: str) -> None:
        """
        Initializes a Page object.

        Args:
            page_id (str): Unique identifier for the page.
            page_number (int): The page's number in the document.
            image_path (str): Path to the image file representing this page.
        """
        self.id: str = page_id
        self.page_number: int = page_number
        self.image_path: str = image_path

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Page instance to a dictionary representation.

        Returns:
            dict: Dictionary containing the page image's details.
        """
        return {
            "id": self.id,
            "page_number": self.page_number,
            "image_path": self.image_path,
        }
