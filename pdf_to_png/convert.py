from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import fitz  # PyMuPDF


ProgressCallback = Callable[[int, int, Path], None]


@dataclass(frozen=True)
class ConvertResult:
    pdf_path: Path
    output_dir: Path
    image_paths: list[Path]

    @property
    def page_count(self) -> int:
        return len(self.image_paths)


def _sanitize_stem(name: str) -> str:
    cleaned = "".join("_" if ch in '\\/:*?"<>|' else ch for ch in name).strip()
    return cleaned or "pdf"


def default_output_dir(pdf_path: Path) -> Path:
    return pdf_path.with_name(f"{pdf_path.stem}_png")


def iter_page_filenames(stem: str, page_count: int) -> Iterable[str]:
    width = max(2, len(str(page_count)))
    for index in range(1, page_count + 1):
        yield f"{stem}-{index:0{width}d}.png"


def convert_pdf_to_png(
    pdf_path: str | Path,
    output_dir: str | Path | None = None,
    dpi: int = 200,
    password: str | None = None,
    on_progress: ProgressCallback | None = None,
) -> ConvertResult:
    """把 PDF 的每一頁轉成 PNG。

    Args:
        pdf_path: 輸入 PDF 路徑。
        output_dir: 輸出資料夾；預設為「原檔名_png」。
        dpi: 輸出清晰度，常用 150 / 200 / 300。
        password: PDF 密碼（若有加密）。
        on_progress: 進度回呼 ``(current, total, saved_path)``。
    """
    source = Path(pdf_path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"找不到檔案：{source}")
    if not source.is_file():
        raise ValueError(f"不是檔案：{source}")
    if source.suffix.lower() != ".pdf":
        raise ValueError(f"請提供 PDF 檔案：{source}")
    if dpi <= 0:
        raise ValueError("dpi 必須大於 0")

    out_dir = (
        Path(output_dir).expanduser().resolve()
        if output_dir
        else default_output_dir(source)
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    open_args: dict = {}
    if password:
        open_args["password"] = password

    try:
        doc = fitz.open(source, **open_args)
    except Exception as exc:  # noqa: BLE001 - 轉成較清楚錯誤
        raise RuntimeError(f"無法開啟 PDF：{exc}") from exc

    try:
        if doc.needs_pass:
            if not password or not doc.authenticate(password):
                raise PermissionError("此 PDF 有密碼保護，請提供正確密碼。")

        page_count = doc.page_count
        if page_count == 0:
            raise ValueError("這個 PDF 沒有頁面。")

        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        stem = _sanitize_stem(source.stem)
        saved: list[Path] = []

        for index, filename in enumerate(iter_page_filenames(stem, page_count), start=1):
            page = doc.load_page(index - 1)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            target = out_dir / filename
            pix.save(target.as_posix())
            saved.append(target)
            if on_progress:
                on_progress(index, page_count, target)
    finally:
        doc.close()

    return ConvertResult(pdf_path=source, output_dir=out_dir, image_paths=saved)
