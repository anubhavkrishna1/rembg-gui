# rembg-gui

**RemBG-GUI** is a graphical user interface for the [rembg](https://github.com/danielgatis/rembg) library, allowing users to easily remove backgrounds from images with just a few clicks.

## Features
- Load and preview input images.
- Remove backgrounds using various models provided by rembg.
- Save the processed images with transparent backgrounds.
- User-friendly interface with scalable image previews.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/anubhavkrishna1/rembg-gui.git
   cd rembg-gui
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   This will install all necessary packages including:
   - PyQt6 - The GUI framework
   - Pillow - Python Imaging Library
   - rembg - Background removal library

3. If you encounter issues with PyQt6 installation:
   
   On Ubuntu/Debian:
   ```bash
   sudo apt-get install python3-pyqt6
   ```

   On Fedora:
   ```bash
   sudo dnf install python3-qt6
   ```

   On macOS:
   ```bash
   brew install pyqt@6
   ```

   On Windows:
   ```bash
   pip install PyQt6
   ```

4. Run the application:
   ```bash
   python rembg_gui.py
   ```

## Usage

1. Launch the application:
   ```bash
   python rembg_gui.py
   ```

2. Use the "Select Image" button to load an image.

3. Choose a model from the "Select Model" dropdown.

4. Click "Remove Background" to process the image.

5. Save the result using the "Save Result" button.

## Supported Models
- `u2net`
- `u2netp`
- `u2net_human_seg`
- `silueta`
- `isnet-general-use`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push to your fork:
   ```bash
   git commit -m "Description of changes"
   git push origin feature-name
   ```
4. Open a pull request on the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
