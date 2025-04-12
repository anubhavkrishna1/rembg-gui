import sys
import os
import io
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, 
                            QLabel, QWidget)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
import rembg

class ScalableLabel(QLabel):
    """Custom QLabel that scales its pixmap to fit the widget size while maintaining aspect ratio"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pixmap = None
        
    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._updatePixmap()
        
    def _updatePixmap(self):
        if self._pixmap and not self._pixmap.isNull():
            # Scale pixmap to fit label while maintaining aspect ratio
            scaled = self._pixmap.scaled(self.width(), self.height(), 
                                        Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation)
            super().setPixmap(scaled)
        
    def resizeEvent(self, event):
        """Override resize event to update the pixmap scale when the label is resized"""
        super().resizeEvent(event)
        self._updatePixmap()


class BackgroundRemovalThread(QThread):
    """Thread for background removal processing"""
    finished = pyqtSignal(object)
    
    def __init__(self, input_image, model_name):
        super().__init__()
        self.input_image = input_image
        self.model_name = model_name
        
    def run(self):
        # Process image with rembg
        result = rembg.remove(
            self.input_image,
            session=rembg.new_session(self.model_name)
        )
        self.finished.emit(result)

class RemBGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load UI file
        uic.loadUi('rembg_gui.ui', self)

        # Replace standard labels with scalable labels
        self.setup_scalable_labels()
        
        # Store instance variables
        self.input_image = None
        self.output_image = None
        
        # Connect signals and slots
        self.selectBtn.clicked.connect(self.open_file_dialog)
        self.processBtn.clicked.connect(self.remove_background)
        self.saveBtn.clicked.connect(self.save_result)
        
        # Status bar initialization
        self.statusBar().showMessage("Ready")

    def setup_scalable_labels(self):
        """Replace standard QLabels with ScalableLabels for better image display"""
        # Create scalable image viewers
        self.inputScalableViewer = ScalableLabel(self.inputFrame)
        self.outputScalableViewer = ScalableLabel(self.outputFrame)
        
        # Copy properties from existing labels
        for attr in ['minimumSize', 'sizePolicy']:
            value = getattr(self.inputViewer, attr)()
            getattr(self.inputScalableViewer, f'set{attr[0].upper()}{attr[1:]}')(value)
            value = getattr(self.outputViewer, attr)()
            getattr(self.outputScalableViewer, f'set{attr[0].upper()}{attr[1:]}')(value)
            
        # Set alignment and text
        self.inputScalableViewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.outputScalableViewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.inputScalableViewer.setText("No image loaded")
        self.outputScalableViewer.setText("No image processed")
        
        # Replace in layout
        self.inputFrameLayout.replaceWidget(self.inputViewer, self.inputScalableViewer)
        self.outputFrameLayout.replaceWidget(self.outputViewer, self.outputScalableViewer)
        
        # Hide old widgets
        self.inputViewer.hide()
        self.outputViewer.hide()
        
        # Use new widgets
        self.inputViewer = self.inputScalableViewer
        self.outputViewer = self.outputScalableViewer
        
    def open_file_dialog(self):
        """Open file dialog to select an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        
        if file_path:
            try:
                # Load the image with PIL
                self.input_image = Image.open(file_path)
                
                # Convert PIL Image to QPixmap via raw bytes
                img_byte_arr = io.BytesIO()
                self.input_image.save(img_byte_arr, format=self.input_image.format or 'PNG')
                pixmap = QPixmap()
                success = pixmap.loadFromData(img_byte_arr.getvalue())
                
                if not success:
                    # Fallback method
                    self.input_image = self.input_image.convert("RGBA")
                    data = self.input_image.tobytes("raw", "RGBA")
                    qim = QImage(data, self.input_image.size[0], self.input_image.size[1], 
                                QImage.Format.Format_RGBA8888)  # Changed enum format
                    pixmap = QPixmap.fromImage(qim)
                
                # Display in the input viewer
                self.inputViewer.setPixmap(pixmap)
                self.inputViewer.setScaledContents(False)
                self.inputViewer.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Changed enum
                
                # Enable the process button
                self.processBtn.setEnabled(True)
                
                # Clear the output viewer
                self.outputViewer.setText("Press 'Remove Background' to process")
                self.saveBtn.setEnabled(False)
                
                self.statusBar().showMessage(f"Loaded image: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load image: {str(e)}")
    
    def remove_background(self):
        """Process the image to remove background"""
        if self.input_image is None:
            return
            
        # Disable buttons during processing
        self.processBtn.setEnabled(False)
        self.selectBtn.setEnabled(False)
        
        # Show processing message
        self.statusBar().showMessage("Processing image... Please wait")
        self.outputViewer.setText("Processing...")
        
        # Get selected model
        model_name = self.modelCombo.currentText()
        
        # Convert PIL Image to bytes for rembg
        img_byte_arr = io.BytesIO()
        self.input_image.save(img_byte_arr, format=self.input_image.format or 'PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Process in a separate thread
        self.bg_thread = BackgroundRemovalThread(img_bytes, model_name)
        self.bg_thread.finished.connect(self.display_result)
        self.bg_thread.start()
    
    def display_result(self, result_bytes):
        """Display the processed result"""
        try:
            # Convert result bytes to PIL Image
            self.output_image = Image.open(io.BytesIO(result_bytes))
            
            # Convert to QPixmap and display
            img_byte_arr = io.BytesIO()
            self.output_image.save(img_byte_arr, format='PNG')
            pixmap = QPixmap()
            success = pixmap.loadFromData(img_byte_arr.getvalue())
            
            if not success:
                # Fallback method
                self.output_image = self.output_image.convert("RGBA")
                data = self.output_image.tobytes("raw", "RGBA")
                qim = QImage(data, self.output_image.size[0], self.output_image.size[1], 
                            QImage.Format.Format_RGBA8888)  # Changed enum format
                pixmap = QPixmap.fromImage(qim)
                
            self.outputViewer.setPixmap(pixmap)
            self.outputViewer.setScaledContents(False)
            self.outputViewer.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Changed enum
            
            # Re-enable buttons
            self.processBtn.setEnabled(True)
            self.selectBtn.setEnabled(True)
            self.saveBtn.setEnabled(True)
            
            self.statusBar().showMessage("Background removed successfully")
            
        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
            # Re-enable buttons
            self.processBtn.setEnabled(True)
            self.selectBtn.setEnabled(True)
    
    def save_result(self):
        """Save the processed image"""
        if self.output_image is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
                
            try:
                self.output_image.save(file_path, "PNG")
                self.statusBar().showMessage(f"Image saved as {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save image: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    
    window = RemBGUI()
    window.show()
    sys.exit(app.exec())  # Changed from app.exec_() to app.exec()

if __name__ == "__main__":
    main()