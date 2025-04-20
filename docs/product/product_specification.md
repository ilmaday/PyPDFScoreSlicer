---
- Version: 1.0  
- Date: 2025-04-20  
- Author: Florian Knierim
---

# Product Specification: PDF Splitter for Scanned Music Scores

## Table of Contents

1. [Overview](#1-overview)  
2. [Target Users](#2-target-users)  
3. [Use Cases](#3-use-cases)  
4. [Features](#4-features)  
5. [Functional Requirements](#5-functional-requirements)  
6. [User Interface Design](#6-user-interface-design)  
7. [Output File Structure](#7-output-file-structure)  
8. [Performance and Constraints](#8-performance-and-constraints)  
9. [Non-functional Requirements](#9-non-functional-requirements)  
10. [Appendices](#10-appendices)

## 1. Overview

The **PyPDFScoreSlicer** is a specialized desktop tool designed to assist orchestra **score keepers** in splitting multi-part scanned music scores into individual PDF files. The tool analyzes each page to detect:
- The **name of the score** (e.g., *Symphony No. 5 in C Minor*)
- The **instrument part** (e.g., *Violin I*, *Trumpet in B♭*)

It then groups and exports the pages belonging to each part into a separate PDF file, named using a user-defined template. Additionally, the tool allows the entry of structured metadata to support cataloging and file management.

## 2. Target Users

### Primary User
- **Orchestra Score Keeper**
  - Responsible for preparing and organizing sheet music for musicians
  - May not have technical expertise but is proficient with PDF and music score terminology

### Environment
- Primarily desktop use (Windows/macOS)
- Typically working with scanned PDF files (not digital music notation)

---

## 3. Use Cases

| Use Case ID | Description |
|-------------|-------------|
| UC01 | Automatically detect and group pages belonging to the same instrument part |
| UC02 | Split a single large PDF into multiple part-specific files |
| UC03 | Allow manual adjustment of detected parts/pages if needed |
| UC04 | Add metadata to each score (e.g., Composer, Title, Opus Number, Notes) |
| UC05 | Configure output file naming patterns (e.g., `[Composer]_[Title]_[Part].pdf`) |
| UC06 | Export all parts to a selected folder with correct names and metadata |

---

## 4. Features

### 4.1 Automatic Page Detection
- Optical recognition (OCR) of headers and page labels
- Score title and part name detection
- Page grouping into instrument parts

### 4.2 Metadata Input
- Composer
- Title
- Opus number or catalog number
- Arrangement (optional)
- Notes (free text)

### 4.3 Naming Template
- User-defined output filename structure using placeholders:
  - `[Composer]`, `[Title]`, `[Part]`, `[PageRange]`, etc.
- Preview of filenames before export

### 4.4 Manual Review & Correction
- UI to review page grouping and detected metadata
- Drag-and-drop page reassignment
- Manual edit of part names if detection is inaccurate

### 4.5 PDF Export
- Export each part as an individual PDF
- Embed metadata in PDF file properties
- Save to custom folder

---

## 5. Functional Requirements

### Detection
- Detect title and part name on each page using OCR or layout rules
- Group contiguous pages by detected part

### Metadata
- Allow manual entry of metadata per score
- Store metadata in a project/session file (optional)

### UI Components
- File upload
- Page thumbnail viewer with detected labels
- Metadata form
- Filename preview and customization
- Export controls

### Output
- One PDF per part
- Filenames based on template
- Embedded metadata (where PDF standards allow)

---

## 6. User Interface Design

### Main Workflow
1. **Load PDF**
2. **Review Page Detection Results**
3. **Edit Metadata**
4. **Configure Filename Pattern**
5. **Preview Output**
6. **Export PDFs**

### Key UI Screens
- **PDF Preview with Page Detection Results**
  - Thumbnails + Detected Score and Part per page
- **Metadata Entry Panel**
- **Filename Template Configuration**
- **Export Summary View**

---

## 7. Output File Structure

### Example
Original PDF: `Mahler_Symphony_1_Scanned.pdf`  
Metadata:
- Composer: Gustav Mahler  
- Title: Symphony No. 1  
- Arrangement: Orchestra  

**Output Files**:
- `Mahler_Symphony_No_1_Violin_I.pdf`
- `Mahler_Symphony_No_1_Violin_II.pdf`
- `Mahler_Symphony_No_1_Clarinet_in_A.pdf`

Each file contains:
- Correct page range
- Embedded metadata:
  - Title: Symphony No. 1 – Violin I
  - Author: Gustav Mahler
  - Subject: Orchestra Score
  - Keywords: score, violin, Mahler

---

## 8. Performance and Constraints

- File sizes up to 500 MB
- PDFs with up to 500 pages
- OCR detection speed: < 5 seconds per page (target)
- Offline usage required (no cloud processing)

---

## 9. Non-functional Requirements

| Category | Requirement |
|----------|-------------|
| Platform | Desktop application (Windows/macOS) |
| Privacy | No external data transmission |
| Accessibility | High-contrast UI, keyboard navigation |
| Localization | English (v1), expandable to other languages |
| Reliability | Recoverable session files and autosave capability |

---

## 10. Appendices

### A. OCR Detection Assumptions
- Score titles and part names are expected near top of page
- Common patterns (e.g., "Violin I", "Clarinet in Bb", "Flute 2") will be preloaded
