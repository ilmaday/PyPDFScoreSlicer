"""
PDF processing module for PyPDFScoreSlicer.
Handles PDF file operations and page extraction.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional

import PyPDF2
from pdf2image import convert_from_path
from PIL import Image

from ocr_engine import OCREngine
from page_grouper import PageGrouper, PageInfo
from metadata_manager import MetadataManager
from naming_engine import NamingEngine
from config_manager import ConfigManager

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF processing operations for sheet music."""

    def __init__(self, pdf_path: Optional[str] = None, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the PDF processor.

        Args:
            pdf_path (Optional[str]): Path to the PDF file
            config_manager (Optional[ConfigManager]): Configuration manager instance
        """
        logger.debug("Initializing PDFProcessor")

        self.config_manager = config_manager or ConfigManager()
        self.ocr_engine = OCREngine(config_manager=self.config_manager)
        self.page_grouper = PageGrouper()
        self.metadata_manager = MetadataManager()
        self.naming_engine = NamingEngine()

        # Initialize pdf_path
        self.pdf_path = Path(pdf_path) if pdf_path else None

        # Set current file in metadata manager if pdf_path is provided
        if self.pdf_path:
            if not self.pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            logger.info(f"Loading PDF file: {pdf_path}")
            self.metadata_manager.set_current_file(str(self.pdf_path))

        # Set up Poppler path
        self.poppler_path = self._get_poppler_path()
        logger.debug(f"Using Poppler path: {self.poppler_path}")

    def _get_poppler_path(self) -> str:
        """
        Get the path to the bundled Poppler binaries.

        Returns:
            str: Path to the Poppler binaries
        """
        # Get the base directory of the project
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Path to poppler binaries in the project
        poppler_path = os.path.join(base_dir, 'libs', 'poppler-24.08.0', 'Library', 'bin')

        # Verify the path exists
        if not os.path.exists(poppler_path):
            self.logger.warning(f"Poppler path not found: {poppler_path}")
            # Fall back to empty string which will use system PATH
            return ""

        return poppler_path

    def set_pdf_path(self, pdf_path: str) -> None:
        """
        Set or update the PDF path.

        Args:
            pdf_path (str): Path to the PDF file

        Raises:
            FileNotFoundError: If the PDF file does not exist
        """
        logger.debug(f"Setting PDF path: {pdf_path}")
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        logger.info(f"Loading PDF file: {pdf_path}")
        self.metadata_manager.set_current_file(str(self.pdf_path))

    def get_page_count(self) -> int:
        """
        Get the total number of pages in the PDF.

        Returns:
            int: Number of pages

        Raises:
            ValueError: If no PDF file has been set
        """
        if not self.pdf_path:
            logger.error("No PDF file has been set")
            raise ValueError("No PDF file has been set. Call set_pdf_path() first.")

        with open(self.pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            page_count = len(pdf.pages)
            logger.debug(f"PDF has {page_count} pages")
            return page_count

    def extract_page_as_image(self, page_number: int) -> Image.Image:
        """
        Extract a page from the current PDF as a PIL Image.

        Args:
            page_number (int): Page number to extract (1-based)

        Returns:
            Image.Image: Extracted page as PIL Image

        Raises:
            ValueError: If no PDF file has been set
        """
        if not self.pdf_path:
            logger.error("No PDF file has been set")
            raise ValueError("No PDF file has been set. Call set_pdf_path() first.")
  
        logger.debug(f"Extracting page {page_number} as image")
        try:
            return convert_from_path(
                str(self.pdf_path), 
                first_page=page_number, 
                last_page=page_number,
                poppler_path=self.poppler_path
            )[0]
        except Exception as e:
            self.logger.error(f"Error extracting page {page_number}: {e}")
            raise

    def get_page_metadata(self, page_number: int) -> Dict[str, str]:
        """
        Get metadata for a specific page using OCR.

        Args:
            page_number (int): Page number to analyze (1-based)

        Returns:
            Dict[str, str]: Dictionary containing page metadata
        """
        logger.debug(f"Getting metadata for page {page_number}")
        image = self.extract_page_as_image(page_number)
        metadata = self.ocr_engine.analyze_page(image, page_number)
        logger.debug(f"Page {page_number} metadata: {metadata}")
        return metadata

    def analyze_page(self, page_number: int) -> Dict[str, str]:
        """
        Analyze a page to extract title and part information.

        Args:
            page_number (int): Page number to analyze (1-based indexing)

        Returns:
            Dict[str, str]: Dictionary with analysis results
        """
        logger.debug(f"Analyzing page {page_number}")
        image = self.extract_page_as_image(page_number)
        analysis = self.ocr_engine.analyze_page(image, page_number)
        logger.debug(f"Page {page_number} analysis: {analysis}")
        return analysis

    def analyze_all_pages(self) -> Dict[str, List[int]]:
        """
        Analyze all pages in the PDF and group them by part.

        Returns:
            Dict[str, List[int]]: Dictionary mapping part names to page numbers
        """
        logger.info("Starting analysis of all pages")
        total_pages = self.get_page_count()
        
        # Analyze each page
        for page_num in range(1, total_pages + 1):
            logger.debug(f"Analyzing page {page_num}/{total_pages}")
            analysis = self.analyze_page(page_num)
            
            # Create page info
            page_info = PageInfo(
                page_number=page_num,
                title=analysis['title'],
                part=analysis['part'],
                raw_text=analysis['raw_text']
            )
            
            # Add to page grouper
            self.page_grouper.add_page(page_info)
            
            # Update metadata if this is the first page
            if page_num == 1 and analysis['title']:
                logger.info(f"Found title: {analysis['title']}")
                self.metadata_manager.update_metadata(
                    str(self.pdf_path),
                    title=analysis['title']
                )
        
        # Group pages
        groups = self.page_grouper.group_pages()
        logger.info(f"Found {len(groups)} parts: {list(groups.keys())}")
        
        # Update metadata with detected parts
        if groups:
            self.metadata_manager.update_metadata(
                str(self.pdf_path),
                detected_parts=list(groups.keys())
            )
        
        return groups

    def split_pdf_by_part(self, output_dir: str) -> Dict[str, List[int]]:
        """
        Split the current PDF into separate files by instrument part.

        Args:
            output_dir (str): Directory to save split PDFs

        Returns:
            Dict[str, List[int]]: Dictionary mapping part names to lists of page numbers

        Raises:
            ValueError: If no PDF file has been set
        """
        if not self.pdf_path:
            logger.error("No PDF file has been set")
            raise ValueError("No PDF file has been set. Call set_pdf_path() first.")

        logger.info(f"Splitting PDF into parts in directory: {output_dir}")
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Initialize PDF reader
        reader = PyPDF2.PdfReader(str(self.pdf_path))
        part_pages: Dict[str, List[int]] = {}
        current_part = None

        # Process each page
        for page_num in range(len(reader.pages)):
            logger.debug(f"Processing page {page_num + 1}")
            metadata = self.get_page_metadata(page_num + 1)
            part = metadata['part']
            
            if part:
                current_part = part
                if part not in part_pages:
                    part_pages[part] = []
                part_pages[part].append(page_num)
                logger.debug(f"Added page {page_num + 1} to part: {part}")

        # Create separate PDFs for each part
        for part, pages in part_pages.items():
            logger.info(f"Creating PDF for part: {part} with {len(pages)} pages")
            writer = PyPDF2.PdfWriter()
            for page_num in pages:
                writer.add_page(reader.pages[page_num])

            # Save the new PDF
            output_path = os.path.join(output_dir, f"{part}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            logger.info(f"Saved part PDF: {output_path}")

        return part_pages

    def get_pdf_metadata(self) -> Dict[str, str]:
        """
        Get metadata for the current PDF.

        Returns:
            Dict[str, str]: Dictionary containing PDF metadata

        Raises:
            ValueError: If no PDF file has been set
        """
        if not self.pdf_path:
            logger.error("No PDF file has been set")
            raise ValueError("No PDF file has been set. Call set_pdf_path() first.")

        logger.debug("Getting PDF metadata")
        # Get metadata fields from config
        metadata_fields = self.config_manager.get_metadata_fields()
        
        # Initialize metadata dictionary with configured fields
        metadata = {field: "" for field in metadata_fields}
        
        # Get title from first page
        first_page_metadata = self.get_page_metadata(1)
        if first_page_metadata['title']:
            metadata['title'] = first_page_metadata['title']
            logger.debug(f"Found title: {first_page_metadata['title']}")
        
        return metadata

    def split_pdf_by_parts(self, output_dir: str) -> Dict[str, Path]:
        """
        Split the PDF into separate files based on detected parts.

        Args:
            output_dir (str): Directory to save the output files

        Returns:
            Dict[str, Path]: Dictionary mapping part names to output file paths

        Raises:
            ValueError: If no PDF file has been set
        """
        if not self.pdf_path:
            logger.error("No PDF file has been set")
            raise ValueError("No PDF file has been set. Call set_pdf_path() first.")

        logger.info(f"Splitting PDF into parts in directory: {output_dir}")
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get the groups if not already analyzed
        if not self.page_grouper.groups:
            logger.debug("No groups found, analyzing all pages")
            self.analyze_all_pages()
        
        groups = self.page_grouper.groups
        output_files = {}
        
        # Get metadata for filename generation
        metadata = self.metadata_manager.get_metadata(str(self.pdf_path))
        metadata_dict = {
            'title': metadata.title,
            'composer': metadata.composer,
            'arranger': metadata.arranger,
            'year': metadata.year
        }
        
        # Split PDF for each group
        for part_name, pages in groups.items():
            logger.info(f"Processing part: {part_name} with {len(pages)} pages")
            # Generate output path
            output_file = self.naming_engine.generate_output_path(
                output_dir, metadata_dict, part_name
            )
            
            # Create PDF writer
            writer = PyPDF2.PdfWriter()
            
            # Add pages to the writer
            with open(self.pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                for page_num in pages:
                    if 1 <= page_num <= len(pdf.pages):
                        writer.add_page(pdf.pages[page_num - 1])
            
            # Write the output file
            with open(output_file, 'wb') as output_file_handle:
                writer.write(output_file_handle)
            
            output_files[part_name] = output_file
            logger.info(f"Saved part PDF: {output_file}")
        
        return output_files 