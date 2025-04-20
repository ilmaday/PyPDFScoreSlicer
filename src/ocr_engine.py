"""
OCR & Page Analysis Engine for PyPDFScoreSlicer.
Handles text extraction and analysis from PDF pages.
"""

import logging
import pytesseract
from typing import Dict, Optional
from PIL import Image

from config_manager import ConfigManager

logger = logging.getLogger(__name__)


class OCREngine:
    """Handles OCR operations and text analysis for sheet music pages."""

    def __init__(self, tesseract_cmd: Optional[str] = None, config_manager: Optional[ConfigManager] = None):
        """Initialize the OCR engine.

        Args:
            tesseract_cmd (Optional[str]): Path to tesseract executable if not in PATH
            config_manager (Optional[ConfigManager]): Configuration manager instance
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # Use provided config manager or create a new one
        self.config_manager = config_manager or ConfigManager()

        # Get instrument parts from config
        self.instrument_parts = self.config_manager.get_instrument_parts()

    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from an image using OCR.

        Args:
            image (Image.Image): PIL Image to extract text from

        Returns:
            str: Extracted text
        """
        return pytesseract.image_to_string(image)

    def detect_title(self, text: str, page_number: int = 1) -> str:
        """
        Detect the score title from extracted text.

        Args:
            text (str): Extracted text from the page
            page_number (int): Page number (default: 1)

        Returns:
            str: Detected title or empty string if not found
        """
        # Simple heuristic: assume title is in the first few lines
        # and is not an instrument part
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not any(part.lower() in line.lower() for part in self.instrument_parts):
                return line
        return ""

    def detect_part_name(self, text: str) -> str:
        """
        Detect the instrument part name from extracted text.

        Args:
            text (str): Extracted text from the page

        Returns:
            str: Detected part name or empty string if not found
        """
        # Check for instrument parts in the text
        lines = text.strip().split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            for part in self.instrument_parts:
                if part.lower() in line.lower():
                    return part
        return ""

    def analyze_page(self, image: Image.Image, page_number: int = 1) -> Dict[str, str]:
        """
        Analyze a page to extract title and part information.

        Args:
            image (Image.Image): PIL Image to analyze
            page_number (int): Page number (default: 1)

        Returns:
            Dict[str, str]: Dictionary with 'title' and 'part' keys
        """
        text = self.extract_text_from_image(image)
        title = self.detect_title(text, page_number)
        part = self.detect_part_name(text)

        return {
            'title': title,
            'part': part,
            'raw_text': text
        }
