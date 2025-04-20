"""
Configuration Manager for PyPDFScoreSlicer.
Handles loading and managing configuration files.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration for the application."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir (Optional[str]): Directory containing configuration files
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to user's home directory
            self.config_dir = Path.home() / ".pypdfscore"
            
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration files
        self.instrument_parts_file = self.config_dir / "instrument_parts.json"
        self.metadata_fields_file = self.config_dir / "metadata_fields.json"
        
        # Load configurations
        self.instrument_parts = self._load_instrument_parts()
        self.metadata_fields = self._load_metadata_fields()
        
    def _load_instrument_parts(self) -> List[str]:
        """
        Load instrument parts from configuration file.

        Returns:
            List[str]: List of instrument parts
        """
        # Default instrument parts
        default_parts = [
            "Violin", "Viola", "Cello", "Bass", "Flute", "Oboe", "Clarinet", 
            "Bassoon", "Horn", "Trumpet", "Trombone", "Tuba", "Timpani", 
            "Percussion", "Harp", "Piano", "Conductor", "Score", "Full Score"
        ]
        
        # Try to load from file
        if self.instrument_parts_file.exists():
            try:
                with open(self.instrument_parts_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading instrument parts: {e}")
                return default_parts
        else:
            # Create default file
            self._save_instrument_parts(default_parts)
            return default_parts
    
    def _load_metadata_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        Load metadata fields from configuration file.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of metadata fields
        """
        # Default metadata fields
        default_fields = {
            "title": {
                "label": "Title",
                "type": "text",
                "required": True
            },
            "composer": {
                "label": "Composer",
                "type": "text",
                "required": False
            },
            "arranger": {
                "label": "Arranger",
                "type": "text",
                "required": False
            },
            "year": {
                "label": "Year",
                "type": "text",
                "required": False
            },
            "notes": {
                "label": "Notes",
                "type": "text",
                "required": False
            }
        }
        
        # Try to load from file
        if self.metadata_fields_file.exists():
            try:
                with open(self.metadata_fields_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading metadata fields: {e}")
                return default_fields
        else:
            # Create default file
            self._save_metadata_fields(default_fields)
            return default_fields
    
    def _save_instrument_parts(self, parts: List[str]) -> None:
        """
        Save instrument parts to configuration file.

        Args:
            parts (List[str]): List of instrument parts
        """
        try:
            with open(self.instrument_parts_file, 'w') as f:
                json.dump(parts, f, indent=2)
        except IOError as e:
            print(f"Error saving instrument parts: {e}")
    
    def _save_metadata_fields(self, fields: Dict[str, Dict[str, Any]]) -> None:
        """
        Save metadata fields to configuration file.

        Args:
            fields (Dict[str, Dict[str, Any]]): Dictionary of metadata fields
        """
        try:
            with open(self.metadata_fields_file, 'w') as f:
                json.dump(fields, f, indent=2)
        except IOError as e:
            print(f"Error saving metadata fields: {e}")
    
    def get_instrument_parts(self) -> List[str]:
        """
        Get the list of instrument parts.

        Returns:
            List[str]: List of instrument parts
        """
        return self.instrument_parts
    
    def get_metadata_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the metadata fields.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of metadata fields
        """
        return self.metadata_fields
    
    def update_instrument_parts(self, parts: List[str]) -> None:
        """
        Update the list of instrument parts.

        Args:
            parts (List[str]): New list of instrument parts
        """
        self.instrument_parts = parts
        self._save_instrument_parts(parts)
    
    def update_metadata_fields(self, fields: Dict[str, Dict[str, Any]]) -> None:
        """
        Update the metadata fields.

        Args:
            fields (Dict[str, Dict[str, Any]]): New dictionary of metadata fields
        """
        self.metadata_fields = fields
        self._save_metadata_fields(fields)
    
    def add_instrument_part(self, part: str) -> None:
        """
        Add a new instrument part.

        Args:
            part (str): New instrument part
        """
        if part not in self.instrument_parts:
            self.instrument_parts.append(part)
            self._save_instrument_parts(self.instrument_parts)
    
    def remove_instrument_part(self, part: str) -> None:
        """
        Remove an instrument part.

        Args:
            part (str): Instrument part to remove
        """
        if part in self.instrument_parts:
            self.instrument_parts.remove(part)
            self._save_instrument_parts(self.instrument_parts)
    
    def add_metadata_field(self, field_name: str, field_config: Dict[str, Any]) -> None:
        """
        Add a new metadata field.

        Args:
            field_name (str): Name of the new field
            field_config (Dict[str, Any]): Configuration for the new field
        """
        self.metadata_fields[field_name] = field_config
        self._save_metadata_fields(self.metadata_fields)
    
    def remove_metadata_field(self, field_name: str) -> None:
        """
        Remove a metadata field.

        Args:
            field_name (str): Name of the field to remove
        """
        if field_name in self.metadata_fields:
            del self.metadata_fields[field_name]
            self._save_metadata_fields(self.metadata_fields) 