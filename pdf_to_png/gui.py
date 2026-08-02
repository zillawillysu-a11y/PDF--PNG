from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .convert import convert_pdf_to_png, default_output_dir


class PdfToPngApp(ttk.Frame):
    def __init__(
        self,
        master: tk.Tk,
        initial_pdf: str | None = None,
        initial_output: str | None = None,
        initial_dpi: int = 200,
    ) -> None:
        super().__init__(master, padding=16)
        self.master.title("PDF → PNG 轉換工具")
        self.master.minsize(520, 360)
        self.pack(fill="both", expand=True)

        self.pdf_var = tk.StringVar(value=initial_pdf or "")
        self.output_var = tk.StringVar(value=initial_output or "")
        self.dpi_var = tk.StringVar(value=str(initial_dpi))
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="請選擇一個 PDF 檔案。")
        self.busy = False

        self._build_ui()
        if initial_pdf and not initial_output:
            self.output_var.set(str(default_output_dir(Path(initial_pdf))))

    def _build_ui(self) -> None:
        title = ttk.Label(self, text="PDF → PNG", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))

        subtitle = ttk.Label(
            self,
            text="選擇 PDF，把每一頁轉成 PNG 圖片。",
            foreground="#555555",
        )
        subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 16))

        ttk.Label(self, text="PDF 檔案").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.pdf_var).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=(0, 8)
        )
        ttk.Button(self, text="瀏覽…", command=self.choose_pdf).grid(
            row=3, column=2, sticky="ew"
        )

        ttk.Label(self, text="輸出資料夾").grid(row=4, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(self, textvariable=self.output_var).grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=(0, 8)
        )
        ttk.Button(self, text="瀏覽…", command=self.choose_output).grid(
            row=5, column=2, sticky="ew"
        )

        options = ttk.Frame(self)
        options.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        ttk.Label(options, text="DPI").pack(side="left")
        ttk.Combobox(
            options,
            textvariable=self.dpi_var,
            values=("150", "200", "300", "400"),
            width=8,
            state="readonly",
        ).pack(side="left", padx=(8, 20))
        ttk.Label(options, text="密碼（可選）").pack(side="left")
        ttk.Entry(options, textvariable=self.password_var, show="*", width=18).pack(
            side="left", padx=(8, 0)
        )

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(18, 8))

        self.convert_btn = ttk.Button(self, text="開始轉換", command=self.start_convert)
        self.convert_btn.grid(row=8, column=0, columnspan=3, sticky="ew")

        ttk.Label(self, textvariable=self.status_var, wraplength=480).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(12, 0)
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def choose_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="選擇 PDF",
            filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")],
        )
        if not path:
            return
        self.pdf_var.set(path)
        if not self.output_var.get().strip():
            self.output_var.set(str(default_output_dir(Path(path))))
        self.status_var.set(f"已選擇：{Path(path).name}")

    def choose_output(self) -> None:
        path = filedialog.askdirectory(title="選擇輸出資料夾")
        if path:
            self.output_var.set(path)

    def start_convert(self) -> None:
        if self.busy:
            return

        pdf = self.pdf_var.get().strip()
        if not pdf:
            messagebox.showwarning("提醒", "請先選擇 PDF 檔案。")
            return

        try:
            dpi = int(self.dpi_var.get())
        except ValueError:
            messagebox.showerror("錯誤", "DPI 必須是數字。")
            return

        output = self.output_var.get().strip() or None
        password = self.password_var.get() or None

        self.busy = True
        self.convert_btn.configure(state="disabled")
        self.progress.configure(value=0, maximum=100)
        self.status_var.set("轉換中…")

        thread = threading.Thread(
            target=self._convert_worker,
            args=(pdf, output, dpi, password),
            daemon=True,
        )
        thread.start()

    def _convert_worker(
        self,
        pdf: str,
        output: str | None,
        dpi: int,
        password: str | None,
    ) -> None:
        try:

            def on_progress(current: int, total: int, saved_path: Path) -> None:
                percent = int(current / total * 100) if total else 0
                message = f"[{current}/{total}] {saved_path.name}"
                self.master.after(
                    0,
                    lambda p=percent, m=message: self._update_progress(p, m),
                )

            result = convert_pdf_to_png(
                pdf_path=pdf,
                output_dir=output,
                dpi=dpi,
                password=password,
                on_progress=on_progress,
            )
            page_count = result.page_count
            output_dir = result.output_dir
            self.master.after(
                0,
                lambda pc=page_count, od=output_dir: self._on_success(pc, od),
            )
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            self.master.after(0, lambda msg=message: self._on_error(msg))

    def _update_progress(self, percent: int, message: str) -> None:
        self.progress.configure(value=percent)
        self.status_var.set(message)

    def _on_success(self, page_count: int, output_dir: Path) -> None:
        self.busy = False
        self.convert_btn.configure(state="normal")
        self.progress.configure(value=100)
        self.status_var.set(f"完成！共 {page_count} 張 PNG\n輸出：{output_dir}")
        messagebox.showinfo("完成", f"已輸出 {page_count} 張 PNG\n\n{output_dir}")

    def _on_error(self, message: str) -> None:
        self.busy = False
        self.convert_btn.configure(state="normal")
        self.status_var.set(f"失敗：{message}")
        messagebox.showerror("轉換失敗", message)


def launch_gui(
    initial_pdf: str | None = None,
    initial_output: str | None = None,
    initial_dpi: int = 200,
) -> None:
    root = tk.Tk()
    try:
        root.call("tk", "scaling", 1.2)
    except tk.TclError:
        pass

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    PdfToPngApp(
        root,
        initial_pdf=initial_pdf,
        initial_output=initial_output,
        initial_dpi=initial_dpi,
    )
    root.mainloop()
