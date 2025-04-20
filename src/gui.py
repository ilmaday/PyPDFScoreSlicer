"""
GUI module for PyPDFScoreSlicer.
Provides a graphical user interface for the application.
"""

import sys
import logging


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
    QTabWidget, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QMessageBox, QProgressBar, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

from pdf_processor import PDFProcessor
from metadata_manager import MetadataManager
from page_grouper import PageInfo

logger = logging.getLogger(__name__)

class ProcessingThread(QThread):
    """Thread for processing PDF files."""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(dict)  # groups
    error = pyqtSignal(str)  # error message
    
    def __init__(self, processor, parent=None):
        """Initialize the processing thread."""
        super().__init__(parent)
        self.processor = processor
        
    def run(self):
        """Run the processing thread."""
        try:
            total_pages = self.processor.get_page_count()
            
            # Analyze each page
            for page_num in range(1, total_pages + 1):
                self.progress.emit(page_num, total_pages)
                
                # Analyze the page
                analysis = self.processor.analyze_page(page_num)
                
                # Create page info
                page_info = PageInfo(
                    page_number=page_num,
                    title=analysis['title'],
                    part=analysis['part'],
                    raw_text=analysis['raw_text']
                )
                
                # Add to page grouper
                self.processor.page_grouper.add_page(page_info)
                
                # Update metadata if this is the first page
                if page_num == 1 and analysis['title']:
                    self.processor.metadata_manager.update_metadata(
                        str(self.processor.pdf_path),
                        title=analysis['title']
                    )
            
            # Group pages
            groups = self.processor.page_grouper.group_pages()
            
            # Update metadata with detected parts
            if groups:
                self.processor.metadata_manager.update_metadata(
                    str(self.processor.pdf_path),
                    detected_parts=list(groups.keys())
                )
            
            self.finished.emit(groups)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main window for the application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.processor = None
        self.groups = {}
        self.current_page = 1
        self.page_images = {}
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PyPDFScoreSlicer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel for file selection and metadata
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        self.file_path_label = QLabel("No file selected")
        file_layout.addWidget(self.file_path_label)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_button)
        
        left_layout.addWidget(file_group)
        
        # Metadata
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        self.title_edit = QLineEdit()
        metadata_layout.addRow("Title:", self.title_edit)
        
        self.composer_edit = QLineEdit()
        metadata_layout.addRow("Composer:", self.composer_edit)
        
        self.arranger_edit = QLineEdit()
        metadata_layout.addRow("Arranger:", self.arranger_edit)
        
        self.year_edit = QLineEdit()
        metadata_layout.addRow("Year:", self.year_edit)
        
        left_layout.addWidget(metadata_group)
        
        # Add left panel to main layout
        main_layout.addWidget(left_panel, 1)
        
        # Create center panel for page preview
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Page preview
        preview_group = QGroupBox("Page Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.page_label = QLabel("No page selected")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.page_label)
        
        # Page navigation
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_button)
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self.page_changed)
        nav_layout.addWidget(self.page_spin)
        
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_button)
        
        preview_layout.addLayout(nav_layout)
        
        center_layout.addWidget(preview_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        center_layout.addWidget(self.progress_bar)
        
        # Add center panel to main layout
        main_layout.addWidget(center_panel, 2)
        
        # Create right panel for part list and actions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Part list
        parts_group = QGroupBox("Parts")
        parts_layout = QVBoxLayout(parts_group)
        
        self.parts_list = QListWidget()
        self.parts_list.itemClicked.connect(self.part_selected)
        parts_layout.addWidget(self.parts_list)
        
        right_layout.addWidget(parts_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        analyze_button = QPushButton("Analyze PDF")
        analyze_button.clicked.connect(self.analyze_pdf)
        actions_layout.addWidget(analyze_button)
        
        split_button = QPushButton("Split PDF")
        split_button.clicked.connect(self.split_pdf)
        actions_layout.addWidget(split_button)
        
        right_layout.addWidget(actions_group)
        
        # Add right panel to main layout
        main_layout.addWidget(right_panel, 1)
        
    def browse_file(self):
        """Open file dialog to select a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.file_path_label.setText(file_path)
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        """Load a PDF file."""
        try:
            self.processor = PDFProcessor(file_path)
            total_pages = self.processor.get_page_count()
            
            self.page_spin.setMaximum(total_pages)
            self.page_spin.setValue(1)
            
            # Load first page
            self.load_page(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {e}")
    
    def load_page(self, page_number):
        """Load a page from the PDF."""
        if not self.processor:
            return
            
        try:
            # Extract page as image
            image = self.processor.extract_page_as_image(page_number)
            
            # Convert to QPixmap
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale to fit
            scaled_pixmap = pixmap.scaled(
                self.page_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display
            self.page_label.setPixmap(scaled_pixmap)
            
            # Store for later use
            self.page_images[page_number] = image
            
            # Update current page
            self.current_page = page_number
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load page {page_number}: {e}")
    
    def prev_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.page_spin.setValue(self.current_page - 1)
    
    def next_page(self):
        """Go to the next page."""
        if self.processor and self.current_page < self.processor.get_page_count():
            self.page_spin.setValue(self.current_page + 1)
    
    def page_changed(self, value):
        """Handle page number change."""
        self.load_page(value)
    
    def analyze_pdf(self):
        """Analyze the PDF file."""
        if not self.processor:
            QMessageBox.warning(self, "Warning", "No PDF file loaded")
            return
            
        # Update metadata
        self.processor.metadata_manager.update_metadata(
            str(self.processor.pdf_path),
            title=self.title_edit.text(),
            composer=self.composer_edit.text(),
            arranger=self.arranger_edit.text(),
            year=self.year_edit.text()
        )
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create and start processing thread
        self.thread = ProcessingThread(self.processor)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.analysis_finished)
        self.thread.error.connect(self.processing_error)
        self.thread.start()
    
    def update_progress(self, current, total):
        """Update progress bar."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def analysis_finished(self, groups):
        """Handle analysis completion."""
        self.groups = groups
        self.progress_bar.setVisible(False)
        
        # Update parts list
        self.parts_list.clear()
        for part, pages in groups.items():
            item = QListWidgetItem(f"{part} ({len(pages)} pages)")
            item.setData(Qt.ItemDataRole.UserRole, part)
            self.parts_list.addItem(item)
        
        QMessageBox.information(self, "Analysis Complete", f"Found {len(groups)} parts")
    
    def processing_error(self, error_message):
        """Handle processing error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Processing failed: {error_message}")
    
    def part_selected(self, item):
        """Handle part selection."""
        part = item.data(Qt.ItemDataRole.UserRole)
        if part in self.groups:
            pages = self.groups[part]
            if pages:
                self.page_spin.setValue(pages[0])
    
    def split_pdf(self):
        """Split the PDF file."""
        if not self.processor or not self.groups:
            QMessageBox.warning(self, "Warning", "No PDF analyzed")
            return
            
        # Select output directory
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        
        if not output_dir:
            return
            
        try:
            # Split PDF
            output_files = self.processor.split_pdf_by_parts(output_dir)
            
            # Show results
            message = "Files created:\n\n"
            for part, file_path in output_files.items():
                message += f"{part}: {file_path}\n"
                
            QMessageBox.information(self, "Split Complete", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to split PDF: {e}")


def run_gui():
    """Run the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 