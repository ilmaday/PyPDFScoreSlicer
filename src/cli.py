"""
Command-line interface for PyPDFScoreSlicer.
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional

from .pdf_processor import PDFProcessor
from .metadata_manager import MetadataManager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PyPDFScoreSlicer - Split sheet music PDFs by parts"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to the PDF file to process"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory to save split PDFs (default: output)"
    )
    parser.add_argument(
        "--tesseract-path",
        type=str,
        help="Path to tesseract executable if not in PATH"
    )
    parser.add_argument(
        "--session-file",
        type=str,
        help="Path to session file for persistence"
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Override detected title"
    )
    parser.add_argument(
        "--composer",
        type=str,
        help="Set composer name"
    )
    parser.add_argument(
        "--arranger",
        type=str,
        help="Set arranger name"
    )
    parser.add_argument(
        "--year",
        type=str,
        help="Set year"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze the PDF without splitting"
    )
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize processor
        processor = PDFProcessor(args.pdf_path, args.tesseract_path)
        print(f"Processing PDF: {args.pdf_path}")
        print(f"Total pages: {processor.get_page_count()}")
        
        # Update metadata if provided
        if args.title or args.composer or args.arranger or args.year:
            metadata_updates = {}
            if args.title:
                metadata_updates['title'] = args.title
            if args.composer:
                metadata_updates['composer'] = args.composer
            if args.arranger:
                metadata_updates['arranger'] = args.arranger
            if args.year:
                metadata_updates['year'] = args.year
                
            processor.metadata_manager.update_metadata(
                args.pdf_path, **metadata_updates
            )
        
        # Analyze pages
        print("Analyzing pages...")
        groups = processor.analyze_all_pages()
        
        # Display results
        print("\nDetected parts:")
        for part, pages in groups.items():
            print(f"  {part}: {len(pages)} pages ({', '.join(map(str, pages))})")
        
        # Save session if requested
        if args.session_file:
            processor.metadata_manager.session_file = args.session_file
            processor.metadata_manager.save_session()
            print(f"\nSession saved to {args.session_file}")
        
        # Split PDF if not analyze-only
        if not args.analyze_only:
            print("\nSplitting PDF...")
            output_files = processor.split_pdf_by_parts(args.output_dir)
            
            print("\nOutput files:")
            for part, file_path in output_files.items():
                print(f"  {part}: {file_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
