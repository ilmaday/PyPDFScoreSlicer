"""
PDF processing module for PyPDFScoreSlicer.
Handles PDF file operations and page extraction.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import PyPDF2
from pdf2image import convert_from_path
from PIL import Image

from .ocr_engine import OCREngine
from .page_grouper import PageGrouper, PageInfo
from .metadata_manager import MetadataManager
from .naming_engine import NamingEngine
from .config_manager import ConfigManager


class PDFProcessor:
    """Handles PDF processing operations for sheet music."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the PDF processor.

        Args:
            config_manager (Optional[ConfigManager]): Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.ocr_engine = OCREngine(config_manager=self.config_manager)
        self.page_grouper = PageGrouper()
        self.metadata_manager = MetadataManager()
        self.naming_engine = NamingEngine()
        
        # Set current file in metadata manager
        self.metadata_manager.set_current_file(str(self.pdf_path))

    def get_page_count(self) -> int:
        """
        Get the total number of pages in the PDF.

        Returns:
            int: Number of pages
        """
        with open(self.pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            return len(pdf.pages)

    def extract_page_as_image(self, pdf_path: str, page_number: int) -> Image.Image:
        """
        Extract a page from a PDF as a PIL Image.

        Args:
            pdf_path (str): Path to the PDF file
            page_number (int): Page number to extract (1-based)

        Returns:
            Image.Image: Extracted page as PIL Image
        """
        return convert_from_path(pdf_path, first_page=page_number, last_page=page_number)[0]

    def get_page_metadata(self, pdf_path: str, page_number: int) -> Dict[str, str]:
        """
        Get metadata for a specific page using OCR.

        Args:
            pdf_path (str): Path to the PDF file
            page_number (int): Page number to analyze (1-based)

        Returns:
            Dict[str, str]: Dictionary containing page metadata
        """
        image = self.extract_page_as_image(pdf_path, page_number)
        return self.ocr_engine.analyze_page(image, page_number)

    def analyze_page(self, page_number: int) -> Dict[str, str]:
        """
        Analyze a page to extract title and part information.

        Args:
            page_number (int): Page number to analyze (1-based indexing)

        Returns:
            Dict[str, str]: Dictionary with analysis results
        """
        image = self.extract_page_as_image(self.pdf_path, page_number)
        return self.ocr_engine.analyze_page(image, page_number)

    def analyze_all_pages(self) -> Dict[str, List[int]]:
        """
        Analyze all pages in the PDF and group them by part.

        Returns:
            Dict[str, List[int]]: Dictionary mapping part names to page numbers
        """
        total_pages = self.get_page_count()
        
        # Analyze each page
        for page_num in range(1, total_pages + 1):
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
                self.metadata_manager.update_metadata(
                    str(self.pdf_path),
                    title=analysis['title']
                )
        
        # Group pages
        groups = self.page_grouper.group_pages()
        
        # Update metadata with detected parts
        if groups:
            self.metadata_manager.update_metadata(
                str(self.pdf_path),
                detected_parts=list(groups.keys())
            )
        
        return groups

    def split_pdf_by_part(self, input_path: str, output_dir: str) -> Dict[str, List[int]]:
        """
        Split a PDF into separate files by instrument part.

        Args:
            input_path (str): Path to input PDF file
            output_dir (str): Directory to save split PDFs

        Returns:
            Dict[str, List[int]]: Dictionary mapping part names to lists of page numbers
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Initialize PDF reader
        reader = PyPDF2.PdfReader(input_path)
        part_pages: Dict[str, List[int]] = {}
        current_part = None

        # Process each page
        for page_num in range(len(reader.pages)):
            metadata = self.get_page_metadata(input_path, page_num + 1)
            part = metadata['part']
            
            if part:
                current_part = part
                if part not in part_pages:
                    part_pages[part] = []
                part_pages[part].append(page_num)

        # Create separate PDFs for each part
        for part, pages in part_pages.items():
            writer = PyPDF2.PdfWriter()
            for page_num in pages:
                writer.add_page(reader.pages[page_num - 1])

            # Save the new PDF
            output_path = os.path.join(output_dir, f"{part}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

        return part_pages

    def get_pdf_metadata(self, pdf_path: str) -> Dict[str, str]:
        """
        Get metadata for the entire PDF.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            Dict[str, str]: Dictionary containing PDF metadata
        """
        # Get metadata fields from config
        metadata_fields = self.config_manager.get_metadata_fields()
        
        # Initialize metadata dictionary with configured fields
        metadata = {field: "" for field in metadata_fields}
        
        # Get title from first page
        first_page_metadata = self.get_page_metadata(pdf_path, 1)
        if first_page_metadata['title']:
            metadata['title'] = first_page_metadata['title']
        
        return metadata

    def split_pdf_by_parts(self, output_dir: str) -> Dict[str, Path]:
        """
        Split the PDF into separate files based on detected parts.

        Args:
            output_dir (str): Directory to save the output files

        Returns:
            Dict[str, Path]: Dictionary mapping part names to output file paths
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get the groups if not already analyzed
        if not self.page_grouper.groups:
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
        
        return output_files 