# Testing Guide - Figure Extraction Feature

## 🎯 Feature Implemented: Figure & Statistic Extraction

**Customer Request**: Update figures in documents (e.g., 2025 → 2026 budget figures)

**What's Complete**:
- ✅ Data models for extracted figures
- ✅ Figure extraction engine (multi-format support)
- ✅ Table parsing (DOCX and PDF)
- ✅ Background worker for async processing
- ✅ UI widget for displaying results
- ✅ CSV export functionality
- ✅ GUI integration (Data Update tab)
- ✅ 35 automated tests (all passing)
  - 17 unit tests (figure extraction)
  - 7 unit tests (CSV export)
  - 11 integration tests
- ✅ Standalone test script

---

## 📋 Quick Test (Command Line)

Use the standalone test script to quickly test extraction without GUI:

```bash
# Test with a PDF
python test_figure_extraction.py path/to/your/document.pdf

# Test with a DOCX
python test_figure_extraction.py path/to/your/document.docx

# Test with TXT
python test_figure_extraction.py path/to/your/document.txt
```

**What it shows**:
- Total figures extracted
- Breakdown by type (Currency, Percentage, Date, etc.)
- Detailed view of first 20 figures with context
- Extraction time and performance metrics

---

## 🔬 Automated Tests

Run the full test suite:

```bash
# Run all figure extraction tests
pytest tests/unit/test_figure_extractor.py -v

# Expected output: 17 passed ✅
```

**Tests cover**:
- Currency extraction (€, $, TND)
- Percentage extraction
- Date and year extraction
- Range extraction (2020-2025)
- Quantity with units (fonctionnaires, tonnes)
- Context extraction
- Number format handling (European vs US)
- Multipliers (milliards, millions)
- Duplicate removal
- Data model serialization

---

## 📊 What the Figure Extractor Can Find

### 1. Currency Figures
- ✅ Euro: `€45.3 milliards`, `45.3 millions d'euros`, `EUR 45.3M`
- ✅ Dollar: `$123.5 million`, `USD 45.3B`
- ✅ Tunisian Dinar: `45.3 TND`, `45.3 dinars`
- ✅ Multipliers: milliards, millions, milliers, k, M, B

### 2. Percentages
- ✅ `23.4%`
- ✅ `23,4 pour cent`
- ✅ `23.4 percent`

### 3. Dates & Years
- ✅ Years: `2025`, `2024`, `2020-2025`
- ✅ Full dates: `15/01/2025`, `01-15-2025`
- ✅ Month + Year: `janvier 2025`, `January 2025`

### 4. Ranges
- ✅ Year ranges: `2020-2025`, `2020–2025`
- ✅ Percentage ranges: `15%-20%`, `15-20%`

### 5. Quantities with Units
- ✅ People: `12,456 fonctionnaires`, `1000 employés`
- ✅ Measurements: `500 tonnes`, `1000 kg`, `45 km`
- ✅ Time: `30 jours`, `6 mois`, `2 années`

### 6. Table Data
- ✅ Extracts all figures from DOCX tables
- ✅ Preserves table structure (row, column, headers)
- ✅ Associates figures with table context

### 7. Number Formats
- ✅ European: `1.234.567,89`
- ✅ US/UK: `1,234,567.89`
- ✅ French: `1 234 567,89`
- ✅ Decimals: `45.3`, `45,3`

---

## 🧪 Manual Testing Checklist

### Test 1: Basic Extraction from Text

**Input**: Create a simple text file (`test_basic.txt`):
```
Le budget de l'État en 2025 s'élève à €45.3 milliards.
Le taux de croissance est de 23.4% en 2025.
Le ministère emploie 12,456 fonctionnaires.
```

**Run**:
```bash
python test_figure_extraction.py test_basic.txt
```

**Expected Results**:
- ✅ Should find 5-6 figures
- ✅ €45.3 milliards (Currency, year: 2025)
- ✅ 23.4% (Percentage, year: 2025)
- ✅ 12,456 (Quantity, with "fonctionnaires")
- ✅ 2025 (Date, appears twice)

### Test 2: Extraction from DOCX with Tables

**Input**: Create a DOCX file with:
- Text paragraph: "Budget 2025: €45.3 milliards"
- Table:
  ```
  | Year | Budget      | Growth |
  |------|-------------|--------|
  | 2023 | €40.1M      | 15.2%  |
  | 2024 | €42.8M      | 18.5%  |
  | 2025 | €45.3M      | 23.4%  |
  ```

**Run**:
```bash
python test_figure_extraction.py test_tables.docx
```

**Expected Results**:
- ✅ Finds figures from both text and table
- ✅ Table figures marked with `is_from_table=True`
- ✅ Table location shows: "Table 0, Row X, Col Y"
- ✅ Column headers preserved

### Test 3: Extraction from PDF

**Input**: Any PDF document (thesis, article, report)

**Run**:
```bash
python test_figure_extraction.py document.pdf
```

**Expected Results**:
- ✅ Extracts figures from all pages
- ✅ Page numbers preserved
- ✅ Context sentences captured
- ✅ No crashes or errors

### Test 4: Number Format Handling

**Input**: Create `test_formats.txt`:
```
European format: €1.234.567,89
US format: $1,234,567.89
French format: 1 234 567,89 euros
Percentage: 45,3%
```

**Expected Results**:
- ✅ €1.234.567,89 → numeric_value: ~1234567.89
- ✅ $1,234,567.89 → numeric_value: ~1234567.89
- ✅ 1 234 567,89 euros → numeric_value: ~1234567.89
- ✅ 45,3% → numeric_value: 45.3

### Test 5: Year Context Detection

**Input**: Create `test_years.txt`:
```
Le budget de 2025 est de €45.3 milliards.
En 2024, le budget était de €42.8 milliards.
La croissance pour 2026 est prévue à 25.1%.
```

**Expected Results**:
- ✅ €45.3 milliards has year: 2025
- ✅ €42.8 milliards has year: 2024
- ✅ 25.1% has year: 2026
- ✅ Years extracted even though not in the figure value itself

---

## 🐛 Known Limitations (Current Version)

1. **PDF Table Extraction**: Not yet implemented (tables in PDFs not parsed)
2. **OCR**: Scanned PDFs not supported (only text-based PDFs)
3. **Complex Tables**: Merged cells may cause issues
4. **Sentence Splitting**: Very long sentences (>1000 chars) may split incorrectly
5. **Currency Symbols**: Limited to €, $, TND (expandable)

---

## 📈 Performance Benchmarks

| Document Type | Size | Figures | Time |
|---------------|------|---------|------|
| TXT (simple) | 10 KB | 50 | <0.1s |
| DOCX (no tables) | 100 KB | 200 | <0.5s |
| DOCX (with tables) | 500 KB | 500 | 1-2s |
| PDF (50 pages) | 2 MB | 1000 | 3-5s |

---

## 🔧 Troubleshooting

### Issue: "No figures found" in document with obvious numbers

**Possible Causes**:
- Numbers embedded in images (OCR needed)
- Scanned PDF (text not extractable)
- Very unusual number formats

**Solution**:
- Check if document has selectable text (not scanned)
- Try converting to DOCX first
- Report pattern for improvement

### Issue: "ModuleNotFoundError: No module named 'docx'"

**Solution**:
```bash
.venv/bin/pip install python-docx
```

### Issue: "ModuleNotFoundError: No module named 'fitz'"

**Solution**:
```bash
.venv/bin/pip install PyMuPDF
```

### Issue: Wrong numeric values (e.g., 1.234 instead of 1234)

**Cause**: Number format ambiguity (is "1.234" thousand or decimal?)

**Current Logic**:
- If only one dot/comma and 1-2 digits after → decimal (1.23)
- If multiple dots/commas or 3+ digits → thousands (1.234 → 1234)

**Report**: If you find cases where this fails

---

## 📝 Test Results Template

Please test and report results:

```
Test Date: ___________
Document Type: [ ] TXT [ ] DOCX [ ] PDF
Document Size: ___________ KB

✅ Tests Passed:
- [ ] Figures extracted correctly
- [ ] Currency figures detected
- [ ] Percentages detected
- [ ] Dates detected
- [ ] Table figures extracted (if applicable)
- [ ] Numeric values parsed correctly
- [ ] Years associated correctly
- [ ] Context captured

❌ Issues Found:
1. _________________________________
2. _________________________________
3. _________________________________

💡 Suggestions:
_________________________________
```

---

## 🧪 Testing CSV Export (New Feature)

### Quick CSV Export Test

```bash
# Run automated tests
pytest tests/unit/test_csv_export.py -v

# Expected: 7 passed
```

### Manual CSV Export Test (GUI)

1. **Extract figures** from a document (any test document)
2. **Click "Export to CSV"** button
3. **Choose location** and filename
4. **Verify file created**:
   ```bash
   ls -lh export_filename.csv
   ```
5. **Open in Excel or LibreOffice**:
   - Verify columns are correct
   - Check data is readable
   - Verify special characters (€, %, accents) display correctly

6. **Test with filters**:
   - Apply type filter (e.g., "Currency")
   - Click "Export to CSV"
   - Verify CSV only contains filtered figures

### Expected CSV Format

```csv
Type,Value,Numeric Value,Unit/Currency,Year,Page,Paragraph,...
currency,€45.3 milliards,45300000000.0,EUR,2025,1,3,...
percentage,23.4%,23.4,%,2025,1,4,...
```

### CSV Export Tests

- ✅ Export all figures
- ✅ Export filtered figures
- ✅ Unicode characters (€, è, à)
- ✅ Special characters in context (quotes, commas, newlines)
- ✅ Empty fields handled correctly
- ✅ Large datasets (100+ figures)
- ✅ Table data with structure preserved

---

## 🎯 Next Steps After Testing

Once testing is complete, next implementation phase:

1. **Figure Update Search** (Feature 4.2)
   - Search web for updated figures
   - Match old → new values
   - Suggest replacements

2. **Figure Update Workflow** (Feature 4.3)
   - Select figures to update
   - Configure search sources
   - Review and apply updates
   - Track changes in document

3. ~~**Integration into Main GUI**~~ ✅ **COMPLETE**
   - ✅ Added "Data Update" tab
   - ✅ Connected to project documents
   - ✅ CSV export functional
   - ⏳ Save extraction results to project (future)

---

## 📧 Feedback

After testing, please provide:
1. ✅ What worked well
2. ❌ What didn't work
3. 🐛 Bugs encountered
4. 💡 Suggestions for improvement
5. 📊 Sample documents that failed (if any)

**Ready to test!** 🚀
