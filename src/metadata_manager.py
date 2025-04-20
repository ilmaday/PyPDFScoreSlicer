"""
Metadata Manager for PyPDFScoreSlicer.
Handles metadata for PDF files and session persistence.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ScoreMetadata:
    """Metadata for a score."""
    title: str = ""
    composer: str = ""
    arranger: str = ""
    year: str = ""
    notes: str = ""
    detected_parts: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for lists."""
        if self.detected_parts is None:
            self.detected_parts = []


class MetadataManager:
    """Manages metadata for PDF files and session persistence."""

    def __init__(self, session_file: Optional[str] = None):
        """
        Initialize the metadata manager.

        Args:
            session_file (Optional[str]): Path to session file for persistence
        """
        self.session_file = session_file
        self.metadata: Dict[str, ScoreMetadata] = {}
        self.current_file: Optional[str] = None
        
        if session_file and Path(session_file).exists():
            self.load_session()

    def set_current_file(self, file_path: str) -> None:
        """
        Set the current file being processed.

        Args:
            file_path (str): Path to the current file
        """
        self.current_file = file_path
        if file_path not in self.metadata:
            self.metadata[file_path] = ScoreMetadata()

    def update_metadata(self, file_path: str, **kwargs) -> None:
        """
        Update metadata for a specific file.

        Args:
            file_path (str): Path to the file
            **kwargs: Metadata fields to update
        """
        if file_path not in self.metadata:
            self.metadata[file_path] = ScoreMetadata()
            
        for key, value in kwargs.items():
            if hasattr(self.metadata[file_path], key):
                setattr(self.metadata[file_path], key, value)

    def get_metadata(self, file_path: str) -> ScoreMetadata:
        """
        Get metadata for a specific file.

        Args:
            file_path (str): Path to the file

        Returns:
            ScoreMetadata: Metadata for the file
        """
        if file_path not in self.metadata:
            self.metadata[file_path] = ScoreMetadata()
        return self.metadata[file_path]

    def save_session(self) -> None:
        """Save the current session to file."""
        if not self.session_file:
            return
            
        session_data = {
            file_path: asdict(metadata)
            for file_path, metadata in self.metadata.items()
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self) -> None:
        """Load session data from file."""
        if not self.session_file or not Path(self.session_file).exists():
            return
            
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
                
            for file_path, metadata_dict in session_data.items():
                self.metadata[file_path] = ScoreMetadata(**metadata_dict)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session: {e}")

    def export_metadata_to_pdf(self, file_path: str, output_path: str) -> None:
        """
        Export metadata to a PDF file.

        Args:
            file_path (str): Path to the source file
            output_path (str): Path to save the PDF with metadata
        """
        # This is a placeholder for actual PDF metadata embedding
        # In a real implementation, this would use PyPDF2 or similar to embed metadata
        print(f"Exporting metadata for {file_path} to {output_path}")
        # TODO: Implement actual PDF metadata embedding 