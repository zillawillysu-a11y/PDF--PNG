from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .convert import convert_pdf_to_png, default_output_dir
from .resources import icon_path

# Black-to-white only. No chromatic colors.
COLORS = {
    "bg": "#000000",
    "panel": "#141414",
    "panel_alt": "#1e1e1e",
    "border": "#3a3a3a",
    "text": "#f0f0f0",
    "muted": "#a0a0a0",
    "accent": "#ffffff",
    "accent_hover": "#d8d8d8",
    "accent_text": "#000000",
    "entry_bg": "#0a0a0a",
    "progress_bg": "#222222",
    "progress_fill": "#ffffff",
    "button_bg": "#2a2a2a",
    "button_hover": "#3d3d3d",
    "disabled_bg": "#1a1a1a",
    "disabled_text": "#666666",
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
        foreground=COLORS["text"],
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
        background=COLORS["panel"],
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
        arrowcolor=COLORS["text"],
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
        arrowcolor=[("disabled", COLORS["disabled_text"])],
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
            ("disabled", COLORS["disabled_bg"]),
        ],
        foreground=[("disabled", COLORS["disabled_text"])],
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
            ("disabled", "#555555"),
        ],
        foreground=[("disabled", "#111111")],
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
        self.master.title("PDF to PNG")
        self.master.minsize(560, 420)
        self.master.configure(bg=COLORS["bg"])
        self.pack(fill="both", expand=True)

        self.pdf_var = tk.StringVar(value=initial_pdf or "")
        self.output_var = tk.StringVar(value=initial_output or "")
        self.dpi_var = tk.StringVar(value=str(initial_dpi))
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select a PDF file to begin.")
        self.busy = False

        self._build_ui()
        if initial_pdf and not initial_output:
            self.output_var.set(str(default_output_dir(Path(initial_pdf))))

    def _build_ui(self) -> None:
        ttk.Label(self, text="PDF to PNG", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            self,
            text="Convert each page of a PDF into PNG images.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 18))

        card = ttk.Frame(self, style="Card.TFrame", padding=16)
        card.grid(row=2, column=0, columnspan=3, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="PDF file", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(card, textvariable=self.pdf_var).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(4, 0)
        )
        ttk.Button(card, text="Browse…", command=self.choose_pdf).grid(
            row=1, column=2, sticky="ew", pady=(4, 0)
        )

        ttk.Label(card, text="Output folder", style="Muted.TLabel").grid(
            row=2, column=0, sticky="w", pady=(14, 0)
        )
        ttk.Entry(card, textvariable=self.output_var).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=(0, 8), pady=(4, 0)
        )
        ttk.Button(card, text="Browse…", command=self.choose_output).grid(
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
        ttk.Label(options, text="Password (optional)", style="Muted.TLabel").pack(
            side="left"
        )
        ttk.Entry(options, textvariable=self.password_var, show="*", width=18).pack(
            side="left", padx=(8, 0)
        )

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(18, 10))

        self.convert_btn = ttk.Button(
            self,
            text="Convert",
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
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return
        self.pdf_var.set(path)
        if not self.output_var.get().strip():
            self.output_var.set(str(default_output_dir(Path(path))))
        self.status_var.set(f"Selected: {Path(path).name}")

    def choose_output(self) -> None:
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_var.set(path)

    def start_convert(self) -> None:
        if self.busy:
            return

        pdf = self.pdf_var.get().strip()
        if not pdf:
            messagebox.showwarning("Notice", "Please select a PDF file first.")
            return

        try:
            dpi = int(self.dpi_var.get())
        except ValueError:
            messagebox.showerror("Error", "DPI must be a number.")
            return

        output = self.output_var.get().strip() or None
        password = self.password_var.get() or None

        self.busy = True
        self.convert_btn.configure(state="disabled")
        self.progress.configure(value=0, maximum=100)
        self.status_var.set("Converting…")

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
        self.status_var.set(f"Done. Exported {page_count} PNG file(s).\nOutput: {output_dir}")
        messagebox.showinfo("Done", f"Exported {page_count} PNG file(s).\n\n{output_dir}")

    def _on_error(self, message: str) -> None:
        self.busy = False
        self.convert_btn.configure(state="normal")
        self.status_var.set(f"Failed: {message}")
        messagebox.showerror("Conversion failed", message)


def _set_window_icon(root: tk.Tk) -> None:
    png = icon_path("icon.png")
    ico = icon_path("icon.ico")

    if png:
        try:
            image = tk.PhotoImage(file=str(png))
            root.iconphoto(True, image)
            # Keep a reference so Tk does not garbage-collect the image.
            root._app_icon_image = image  # type: ignore[attr-defined]
        except tk.TclError:
            pass

    if ico:
        try:
            root.iconbitmap(default=str(ico))
        except tk.TclError:
            pass


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
    _set_window_icon(root)
    PdfToPngApp(
        root,
        initial_pdf=initial_pdf,
        initial_output=initial_output,
        initial_dpi=initial_dpi,
    )
    root.mainloop()
