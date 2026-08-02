# PDF to PNG

A Python program that converts each page of a PDF into PNG images.

Supports:

- **CLI** for batch conversion
- **GUI** with a black-and-white interface

## Install

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

## DPI guide

| DPI | Use case |
| --- | --- |
| 150 | Smaller files / previews |
| 200 | Default / general use |
| 300 | Print / higher detail |
| 400 | Very high detail / larger files |

## Project layout

```text
pdf2png.py          # Entry point
pdf_to_png/
  convert.py        # Conversion logic
  cli.py            # Command-line interface
  gui.py            # Desktop UI (black / gray / white only)
requirements.txt
```

## Notes

- The GUI uses only black-to-white colors (no accent colors).
- All user-facing text is in English.
- Powered by [PyMuPDF](https://pymupdf.readthedocs.io/).
