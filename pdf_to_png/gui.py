from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .convert import convert_pdf_to_png, default_output_dir

# CuePlayer 風格：全黑背景、低干擾深色介面
COLORS = {
    "bg": "#000000",
    "panel": "#111111",
    "panel_alt": "#1a1a1a",
    "border": "#333333",
    "text": "#e8e8e8",
    "muted": "#9a9a9a",
    "accent": "#ffb000",
    "accent_hover": "#ffc933",
    "accent_text": "#111111",
    "entry_bg": "#0d0d0d",
    "progress_bg": "#222222",
    "progress_fill": "#ffb000",
    "button_bg": "#222222",
    "button_hover": "#333333",
    "danger": "#ff5c5c",
    "ok": "#6dffb0",
}


def apply_black_theme(root: tk.Tk) -> ttk.Style:
    root.configure(bg=COLORS["bg"])
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        ".",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["entry_bg"],
        bordercolor=COLORS["border"],
        darkcolor=COLORS["bg"],
        lightcolor=COLORS["border"],
        troughcolor=COLORS["progress_bg"],
        focuscolor=COLORS["accent"],
        font=("Segoe UI", 10),
    )
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["panel"], relief="flat")
    style.configure(
        "Title.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["accent"],
        font=("Segoe UI", 22, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Status.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "TEntry",
        fieldbackground=COLORS["entry_bg"],
        foreground=COLORS["text"],
        insertcolor=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        padding=8,
    )
    style.map(
        "TEntry",
        fieldbackground=[("focus", COLORS["panel_alt"])],
        bordercolor=[("focus", COLORS["accent"])],
    )
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["entry_bg"],
        background=COLORS["button_bg"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["accent"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLORS["entry_bg"]), ("focus", COLORS["panel_alt"])],
        foreground=[("readonly", COLORS["text"])],
        bordercolor=[("focus", COLORS["accent"])],
    )
    root.option_add("*TCombobox*Listbox.background", COLORS["panel"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent"])
    root.option_add("*TCombobox*Listbox.selectForeground", COLORS["accent_text"])

    style.configure(
        "TButton",
        background=COLORS["button_bg"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["button_bg"],
        darkcolor=COLORS["button_bg"],
        focuscolor=COLORS["border"],
        padding=(14, 8),
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "TButton",
        background=[
            ("active", COLORS["button_hover"]),
            ("disabled", COLORS["panel"]),
        ],
        foreground=[("disabled", "#666666")],
    )
    style.configure(
        "Accent.TButton",
        background=COLORS["accent"],
        foreground=COLORS["accent_text"],
        bordercolor=COLORS["accent"],
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
        focuscolor=COLORS["accent"],
        padding=(14, 10),
        font=("Segoe UI", 11, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", COLORS["accent_hover"]),
            ("disabled", "#5a4500"),
        ],
        foreground=[("disabled", "#222222")],
    )
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=COLORS["progress_bg"],
        background=COLORS["progress_fill"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["progress_fill"],
        darkcolor=COLORS["progress_fill"],
        thickness=14,
    )
    return style


class PdfToPngApp(ttk.Frame):
    def __init__(
        self,
        master: tk.Tk,
        initial_pdf: str | None = None,
        initial_output: str | None = None,
        initial_dpi: int = 200,
    ) -> None:
        super().__init__(master, padding=20)
        self.master.title("PDF → PNG")
        self.master.minsize(560, 420)
        self.master.configure(bg=COLORS["bg"])
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
        ttk.Label(self, text="PDF → PNG", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            self,
            text="黑色介面 · 選擇 PDF，把每一頁轉成 PNG",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 18))

        card = ttk.Frame(self, style="Card.TFrame", padding=16)
        card.grid(row=2, column=0, columnspan=3, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        # 讓 Card 看起來更像面板：外層用 tk.Frame 畫邊線
        # ttk 難以畫邊框，改用外層容器
        ttk.Label(card, text="PDF 檔案", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(card, textvariable=self.pdf_var).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(4, 0)
        )
        ttk.Button(card, text="瀏覽…", command=self.choose_pdf).grid(
            row=1, column=2, sticky="ew", pady=(4, 0)
        )

        ttk.Label(card, text="輸出資料夾", style="Muted.TLabel").grid(
            row=2, column=0, sticky="w", pady=(14, 0)
        )
        ttk.Entry(card, textvariable=self.output_var).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(4, 0)
        )
        ttk.Button(card, text="瀏覽…", command=self.choose_output).grid(
            row=3, column=2, sticky="ew", pady=(4, 0)
        )

        options = ttk.Frame(card, style="Card.TFrame")
        options.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(16, 0))
        ttk.Label(options, text="DPI", style="Muted.TLabel").pack(side="left")
        ttk.Combobox(
            options,
            textvariable=self.dpi_var,
            values=("150", "200", "300", "400"),
            width=8,
            state="readonly",
        ).pack(side="left", padx=(8, 20))
        ttk.Label(options, text="密碼（可選）", style="Muted.TLabel").pack(side="left")
        ttk.Entry(options, textvariable=self.password_var, show="*", width=18).pack(
            side="left", padx=(8, 0)
        )

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(18, 10))

        self.convert_btn = ttk.Button(
            self,
            text="開始轉換",
            style="Accent.TButton",
            command=self.start_convert,
        )
        self.convert_btn.grid(row=4, column=0, columnspan=3, sticky="ew")

        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=500,
        )
        self.status_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=(14, 0))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

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

    apply_black_theme(root)
    PdfToPngApp(
        root,
        initial_pdf=initial_pdf,
        initial_output=initial_output,
        initial_dpi=initial_dpi,
    )
    root.mainloop()
