# PDF to PNG

A Python program that converts each page of a PDF into PNG images.

Supports:

- **CLI** for batch conversion
- **GUI** with a black-and-white interface
- **Packaged app** (`PDF2PNG.exe` on Windows)

## Install (run from source)

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

## Usage

### GUI

```bash
python pdf2png.py
# or
python -m pdf_to_png --gui
```

1. Select a PDF
2. Optionally change the output folder / DPI
3. Click **Convert**

### CLI

```bash
# Basic usage: writes to "<filename>_png"
python pdf2png.py your-file.pdf

# Custom output folder
python pdf2png.py your-file.pdf -o ./output

# Custom DPI
python pdf2png.py your-file.pdf --dpi 300

# Password-protected PDF
python pdf2png.py your-file.pdf --password your-password
```

### Output names

For a 3-page `report.pdf`:

```text
report_png/
  report-01.png
  report-02.png
  report-03.png
```

## Package as a standalone app

### Windows (recommended)

1. Install [Python](https://www.python.org/downloads/) and check **Add python.exe to PATH**
2. Open the project folder
3. Double-click `build.bat`

When it finishes, you will get:

```text
dist\PDF2PNG.exe
```

You can copy `PDF2PNG.exe` anywhere and double-click to open the GUI.  
No Python install is needed on other PCs to run the `.exe`.

### macOS / Linux

```bash
chmod +x build.sh
./build.sh
```

Output:

```text
dist/PDF2PNG
```

## DPI guide

| DPI | Use case |
| --- | --- |
| 150 | Smaller files / previews |
| 200 | Default / general use |
| 300 | Print / higher detail |
| 400 | Very high detail / larger files |

## Project layout

```text
pdf2png.py              # Entry point
pdf_to_png/
  convert.py            # Conversion logic
  cli.py                # Command-line interface
  gui.py                # Desktop UI (black / gray / white only)
pdf2png.spec            # PyInstaller config
build.bat               # Windows one-click build
build.sh                # macOS / Linux build
requirements.txt
requirements-build.txt
```

## Notes

- The GUI uses only black-to-white colors (no accent colors).
- All user-facing text is in English.
- Powered by [PyMuPDF](https://pymupdf.readthedocs.io/).
