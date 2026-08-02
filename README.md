# PDF → PNG

把 PDF 每一頁轉成 PNG 的 Python 程式。

支援：

- **指令列（CLI）**：適合批次處理
- **圖形介面（GUI）**：點選檔案即可轉換

## 安裝

需要 Python 3.10+。

```bash
pip install -r requirements.txt
```

## 使用方式

### 圖形介面

```bash
python pdf2png.py
# 或
python -m pdf_to_png --gui
```

1. 選擇 PDF
2. （可選）改輸出資料夾 / DPI
3. 按「開始轉換」

### 指令列

```bash
# 基本用法：輸出到「原檔名_png」資料夾
python pdf2png.py 你的檔案.pdf

# 指定輸出資料夾
python pdf2png.py 你的檔案.pdf -o ./輸出資料夾

# 指定清晰度（DPI）
python pdf2png.py 你的檔案.pdf --dpi 300

# 有密碼的 PDF
python pdf2png.py 你的檔案.pdf --password 你的密碼
```

### 輸出檔名

例如 `report.pdf` 有 3 頁，會得到：

```text
report_png/
  report-01.png
  report-02.png
  report-03.png
```

## DPI 建議

| DPI | 用途 |
| --- | --- |
| 150 | 檔案較小、預覽用 |
| 200 | 預設，一般使用 |
| 300 | 列印 / 較高清晰度 |
| 400 | 超高清，檔案會較大 |

## 專案結構

```text
pdf2png.py          # 啟動入口
pdf_to_png/
  convert.py        # 核心轉換邏輯
  cli.py            # 指令列
  gui.py            # 圖形介面
requirements.txt
```

## 技術

使用 [PyMuPDF](https://pymupdf.readthedocs.io/) 渲染 PDF 頁面並輸出 PNG。
