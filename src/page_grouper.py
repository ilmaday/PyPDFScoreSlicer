"""
Page Grouping Module for PyPDFScoreSlicer.
Handles grouping pages into logical parts based on detected information.
"""
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

@dataclass
class PageInfo:
    """Information about a single page."""
    page_number: int
    title: str
    part: str
    raw_text: str


class PageGrouper:
    """Handles grouping pages into logical parts."""

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize the page grouper.

        Args:
            similarity_threshold (float): Threshold for fuzzy matching (0.0 to 1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.pages: List[PageInfo] = []
        self.groups: Dict[str, List[int]] = {}

    def add_page(self, page_info: PageInfo) -> None:
        """
        Add a page to the collection for grouping.

        Args:
            page_info (PageInfo): Information about the page
        """
        self.pages.append(page_info)

    def _similarity(self, a: str, b: str) -> float:
        """
        Calculate similarity between two strings.

        Args:
            a (str): First string
            b (str): Second string

        Returns:
            float: Similarity score between 0.0 and 1.0
        """
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _find_matching_group(self, part: str) -> Optional[str]:
        """
        Find a matching group for a part name.

        Args:
            part (str): Part name to match

        Returns:
            Optional[str]: Matching group name or None if no match
        """
        if not part:
            return None

        for group_name in self.groups:
            if self._similarity(part, group_name) >= self.similarity_threshold:
                return group_name
        
        return None

    def group_pages(self) -> Dict[str, List[int]]:
        """
        Group pages into logical parts.

        Returns:
            Dict[str, List[int]]: Dictionary mapping part names to page numbers
        """
        self.groups = {}
        
        for page in self.pages:
            if not page.part:
                continue
                
            group_name = self._find_matching_group(page.part)
            
            if group_name:
                # Add to existing group
                self.groups[group_name].append(page.page_number)
            else:
                # Create new group
                self.groups[page.part] = [page.page_number]
        
        return self.groups

    def get_group_for_page(self, page_number: int) -> Optional[str]:
        """
        Get the group name for a specific page.

        Args:
            page_number (int): Page number to look up

        Returns:
            Optional[str]: Group name or None if not found
        """
        for group_name, pages in self.groups.items():
            if page_number in pages:
                return group_name
        return None

    def reorder_group(self, group_name: str, new_order: List[int]) -> None:
        """
        Reorder pages within a group.

        Args:
            group_name (str): Name of the group to reorder
            new_order (List[int]): New order of page numbers
        """
        if group_name in self.groups:
            # Validate that all pages in new_order belong to this group
            current_pages = set(self.groups[group_name])
            new_pages = set(new_order)
            
            if current_pages == new_pages:
                self.groups[group_name] = new_order
            else:
                raise ValueError("New order must contain exactly the same pages as the current group") 