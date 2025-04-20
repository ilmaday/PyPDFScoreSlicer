"""
Main entry point for PyPDFScoreSlicer.
"""

import argparse
import sys
import logging

from cli import main as cli_main
from gui import run_gui
from logger import setup_logger


def main():
    """Main entry point for the application."""

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description="PyPDFScoreSlicer - Split sheet music PDFs by parts"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run in GUI mode"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments for CLI mode"
    )
    args = parser.parse_args()

    if args.gui:
        # Run in GUI mode
        logger.info("Running in GUI mode")
        run_gui()
    else:
        # Run in CLI mode
        logger.info("Running in CLI mode")
        sys.argv = [sys.argv[0]] + args.args
        cli_main()


if __name__ == "__main__":
    setup_logger()
    main()
