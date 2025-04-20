"""
Output Naming Engine for PyPDFScoreSlicer.
Handles filename generation for output files.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class NamingEngine:
    """Handles filename generation for output files."""

    def __init__(self, template: Optional[str] = None):
        """
        Initialize the naming engine.

        Args:
            template (Optional[str]): Filename template with placeholders
        """
        self.template = template or "{title}_{part}"
        self.used_names: Dict[str, int] = {}

    def set_template(self, template: str) -> None:
        """
        Set the filename template.

        Args:
            template (str): Filename template with placeholders
        """
        self.template = template

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to be safe for all operating systems.

        Args:
            filename (str): Filename to sanitize

        Returns:
            str: Sanitized filename
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        # Replace multiple underscores with a single one
        sanitized = re.sub(r'_+', '_', sanitized)
        # Trim underscores from the beginning and end
        sanitized = sanitized.strip('_')
        return sanitized

    def _get_unique_name(self, base_name: str) -> str:
        """
        Get a unique filename by adding a suffix if needed.

        Args:
            base_name (str): Base filename

        Returns:
            str: Unique filename
        """
        if base_name not in self.used_names:
            self.used_names[base_name] = 0
            return base_name
        
        self.used_names[base_name] += 1
        name, ext = os.path.splitext(base_name)
        return f"{name}_{self.used_names[base_name]}{ext}"

    def generate_filename(self, metadata: Dict[str, str], part: str) -> str:
        """
        Generate a filename based on the template and metadata.

        Args:
            metadata (Dict[str, str]): Metadata dictionary
            part (str): Part name

        Returns:
            str: Generated filename
        """
        # Create a copy of metadata to avoid modifying the original
        data = metadata.copy()
        
        # Add part to the data
        data['part'] = part
        
        # Add timestamp if needed
        if '{timestamp}' in self.template:
            data['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Replace placeholders in the template
        filename = self.template
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in filename:
                filename = filename.replace(placeholder, str(value))
        
        # Sanitize the filename
        filename = self._sanitize_filename(filename)
        
        # Add .pdf extension if not present
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Ensure uniqueness
        return self._get_unique_name(filename)

    def generate_output_path(self, output_dir: str, metadata: Dict[str, str], part: str) -> Path:
        """
        Generate a full output path for a file.

        Args:
            output_dir (str): Output directory
            metadata (Dict[str, str]): Metadata dictionary
            part (str): Part name

        Returns:
            Path: Full output path
        """
        filename = self.generate_filename(metadata, part)
        return Path(output_dir) / filename 