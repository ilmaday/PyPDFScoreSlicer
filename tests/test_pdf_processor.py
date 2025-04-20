"""
Test module for PDFProcessor class.
"""

import pytest
from pathlib import Path
from src.pdf_processor import PDFProcessor


def test_pdf_processor_initialization():
    """Test PDFProcessor initialization with invalid file."""
    with pytest.raises(FileNotFoundError):
        PDFProcessor("nonexistent.pdf")


def test_get_page_count(tmp_path):
    """Test getting page count from a PDF."""
    # Create a dummy PDF file for testing
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF\n")  # Minimal valid PDF
    
    processor = PDFProcessor(str(pdf_path))
    assert processor.get_page_count() == 0  # Empty PDF has 0 pages


def test_extract_page_as_image(tmp_path):
    """Test extracting a page as an image."""
    # Create a dummy PDF file for testing
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF\n")  # Minimal valid PDF
    
    processor = PDFProcessor(str(pdf_path))
    with pytest.raises(ValueError):
        processor.extract_page_as_image(1)  # Should raise error for invalid page number 