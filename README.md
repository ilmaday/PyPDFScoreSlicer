# PyPDFScoreSlicer
PyPDFScoreSlicer is a Python tool designed to simplify the management of scanned sheet music PDFs. It automatically extracts the title and instrument or part information from each page, groups pages by musical part, and displays the result to the user. Once verified, the tool suggests filenames and can split the PDF into separate files per instrument or part.

## Features

- **OCR-based Part Detection**: Automatically detects instrument parts and score titles using OCR
- **Intelligent Page Grouping**: Groups pages into logical parts based on detected information
- **Metadata Management**: Captures and stores metadata about the score (title, composer, etc.)
- **Flexible Output Naming**: Configurable filename templates with placeholders
- **Dual Interface**: Available as both a command-line tool and a graphical user interface
- **Session Persistence**: Saves work in progress for later completion

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PyPDFScoreSlicer.git
cd PyPDFScoreSlicer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR (required for text extraction):
   - **Windows**: 
     - Using Chocolatey (recommended): `choco install tesseract`
     - Manual installation: Download and install from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`

## Usage

### Command Line Interface

Basic usage:
```bash
python -m src path/to/score.pdf
```

Options:
```bash
python -m src path/to/score.pdf --output-dir output_folder --title "Score Title" --composer "Composer Name"
```

### Graphical User Interface

Launch the GUI:
```bash
python -m src --gui
```

## Development Setup

This project uses several development tools:
- `black` for code formatting
- `flake8` for linting
- `pytest` for testing

To format your code:
```bash
black .
```

To run tests:
```bash
pytest
```

## Architecture

The application follows a modular architecture:

- **PDF Processor**: Core module for PDF operations
- **OCR Engine**: Handles text extraction and analysis
- **Page Grouper**: Groups pages into logical parts
- **Metadata Manager**: Manages score metadata
- **Naming Engine**: Generates filenames for output
- **GUI**: Provides a graphical user interface

## License

This project is licensed under the terms included in the LICENSE file.
