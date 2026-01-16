# Figure Extraction - Quick Reference Card

## 🚀 Quick Start

### GUI Method
```
1. Open application
2. Go to 📊 Data Update tab
3. Click "Extract Figures from Document"
4. Select document (PDF/DOCX/TXT)
5. View results → Export to CSV
```

### Command Line
```bash
python test_figure_extraction.py document.pdf
```

---

## 📊 What Gets Extracted

| Type | Examples |
|------|----------|
| 💰 Currency | €45.3M, $1.5B, 100 TND |
| 📈 Percentage | 23.4%, 15-20% |
| 📅 Date | 2025, 15/01/2025, Jan 2025 |
| 🔢 Quantity | 12,456 people, 500 kg |
| 📏 Range | 2020-2025, 15%-20% |
| #️⃣ Number | 45.3, 1.234.567 |

---

## 🎛️ GUI Controls

### Statistics Panel
```
Total: 45  Currency: 12  Percentage: 8  Dates: 15
```

### Filters
- **Type Filter**: All | Currency | Percentage | Date | Range | Quantity | Number
- **Tables Only**: ☐ Show only table figures

### Actions
- **Export to CSV**: Save results to file
- **Update Selected**: Future feature for updating figures
- **Clear Results**: Remove current results

---

## 📋 Results Table

| Column | Description |
|--------|-------------|
| **Select** | ☐ Checkbox |
| **Type** | 🟢 Currency 🟠 % 🔵 Date |
| **Value** | Original text |
| **Numeric** | Parsed number |
| **Unit/Currency** | EUR, %, kg, etc. |
| **Year** | From context |
| **Location** | Page, Para, or Table |
| **Context** | Sentence |

---

## 💡 Tips

### Best Results
✅ Text-based PDFs (not scanned)
✅ Clean DOCX files
✅ Well-structured tables
✅ Consistent formats

### May Have Issues
⚠️ Scanned PDFs (OCR not supported yet)
⚠️ Complex merged cells
⚠️ Numbers in images
⚠️ Very unusual formats

---

## 🔢 Number Formats

### Automatically Parsed
```
European:  1.234.567,89  → 1234567.89
US:        1,234,567.89  → 1234567.89
French:    1 234 567,89  → 1234567.89
```

### Multipliers
```
milliards, B  → ×1,000,000,000
millions, M   → ×1,000,000
milliers, k   → ×1,000
```

---

## 📤 CSV Export

### Export Steps
```
1. Extract figures (optionally filter)
2. Click "Export to CSV"
3. Choose location & filename
4. Open in Excel/LibreOffice
```

### CSV Columns
```csv
Type | Value | Numeric Value | Unit/Currency | Year |
Page | Paragraph | Is From Table | Context | ...
```

### Open in Excel
```
File → Open → Select CSV
(Auto-detects UTF-8 encoding)
```

### Open in LibreOffice
```
File → Open → Select CSV
Settings:
- Separator: Comma
- Delimiter: " (quote)
- Charset: UTF-8
```

---

## ⚡ Performance

| Document Size | Expected Time |
|---------------|---------------|
| 10 KB (TXT) | <1 second |
| 100 KB (DOCX) | <1 second |
| 500 KB (DOCX with tables) | 1-2 seconds |
| 2 MB (50-page PDF) | 3-5 seconds |
| 4 MB (100-page PDF) | 10-20 seconds |

---

## 🐛 Troubleshooting

### No Figures Found
- Check if PDF is scanned (text should be selectable)
- Try converting to DOCX
- Document may genuinely have no figures

### Wrong Numeric Values
- Check context to verify
- European/US format ambiguity
- Report persistent issues

### Slow Extraction
- Close other applications
- Check file size
- Try smaller sections

### Export Fails
- Check file permissions
- Try different location
- Close file if open
- Check disk space

---

## 🔍 Common Workflows

### Find All Budget Items
```
1. Extract figures
2. Filter: Currency
3. Export to CSV
4. Sort by "Numeric Value"
```

### Update 2025 → 2026 Figures
```
1. Extract figures
2. Filter: Currency + Year: 2025
3. Export to CSV
4. Identify figures to update
5. Update manually (automated coming soon)
```

### Compare Across Documents
```
1. Extract from each document
2. Export to separate CSVs
3. Merge in Excel
4. Analyze with pivot tables
```

### Verify Data
```
1. Extract figures
2. Export to CSV
3. Share with team
4. Team checks against sources
5. Mark verified in CSV
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `USER_GUIDE.md` | Complete user manual |
| `TESTING_GUIDE.md` | Feature overview & test cases |
| `MANUAL_TESTING_STEPS.md` | Step-by-step testing |
| `GUI_INTEGRATION.md` | Technical integration details |
| `QUICK_REFERENCE.md` | This card |

---

## 🆘 Need Help?

### Check These First
1. Is text selectable? (not scanned)
2. Is file format supported? (PDF, DOCX, TXT)
3. Are figures in standard format?
4. Is extraction complete? (not still processing)

### Still Having Issues?
- Review USER_GUIDE.md Troubleshooting section
- Check logs for error messages
- Save problem document (if shareable)
- Report issue to project maintainer

---

## 🎯 Supported vs. Planned

### ✅ Currently Supported
- PDF, DOCX, TXT extraction
- 6 figure types (currency, %, date, range, quantity, number)
- Table extraction (DOCX only)
- European & US number formats
- CSV export
- Type and table filtering
- Year context detection

### 🔜 Planned Features
- PDF table extraction
- OCR for scanned documents
- Web search for updated figures
- Automated figure updates
- Batch processing
- Custom patterns
- More export formats (JSON, Excel)

---

## 🔑 Keyboard Shortcuts

(GUI keyboard shortcuts - to be implemented)

```
Ctrl+E    Extract figures
Ctrl+S    Export to CSV
Ctrl+F    Filter
Ctrl+A    Select all figures
Ctrl+D    Deselect all
Delete    Clear results
```

---

## 📊 Example Output

```
📄 Document: budget_2025.pdf
================================================================================
Total figures: 45
Currency: 12 | Percentage: 8 | Dates: 15 | Quantity: 7 | Other: 3
Tables parsed: 2
Time: 2.3s
================================================================================

Top Figures:
[1] €45.3 milliards (2025) - Le budget de l'État...
[2] 23.4% (2025) - Le taux de croissance...
[3] 12,456 fonctionnaires - Le ministère emploie...

Export: ✅ budget_2025_figures.csv (45 rows)
```

---

**Version**: 1.0 | **Date**: 2026-01-06 | **Feature**: Figure Extraction
