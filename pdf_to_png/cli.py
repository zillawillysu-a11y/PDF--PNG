from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .convert import convert_pdf_to_png, default_output_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-to-png",
        description="把 PDF 每一頁轉成 PNG 圖片。",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="要轉換的 PDF 檔案路徑",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="輸出資料夾（預設：原檔名_png）",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="輸出清晰度，預設 200（常用 150/200/300）",
    )
    parser.add_argument(
        "--password",
        help="PDF 密碼（若有加密）",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="開啟圖形介面",
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

    # 沒參數，或明確指定 --gui：開啟圖形介面
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
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1

    print(f"\n完成！共輸出 {result.page_count} 張 PNG")
    print(f"輸出資料夾：{result.output_dir}")
    return 0


def main() -> None:
    raise SystemExit(run_cli())
