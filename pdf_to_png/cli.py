from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .convert import convert_pdf_to_png, default_output_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-to-png",
        description="Convert each page of a PDF into PNG images.",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="Path to the PDF file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output folder (default: <filename>_png)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Output resolution in DPI (default: 200)",
    )
    parser.add_argument(
        "--password",
        help="PDF password if the file is encrypted",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open the graphical interface",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # No PDF path, or --gui explicitly requested: open the GUI.
    if args.gui or not args.pdf:
        from .gui import launch_gui

        launch_gui(
            initial_pdf=args.pdf,
            initial_output=args.output,
            initial_dpi=args.dpi,
        )
        return 0

    pdf_path = Path(args.pdf)
    output = args.output or default_output_dir(pdf_path)

    def on_progress(current: int, total: int, saved_path: Path) -> None:
        print(f"[{current}/{total}] {saved_path.name}")

    try:
        result = convert_pdf_to_png(
            pdf_path=pdf_path,
            output_dir=output,
            dpi=args.dpi,
            password=args.password,
            on_progress=on_progress,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"\nDone. Exported {result.page_count} PNG file(s).")
    print(f"Output folder: {result.output_dir}")
    return 0


def main() -> None:
    raise SystemExit(run_cli())
