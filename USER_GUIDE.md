# User Guide - Figure Extraction & Data Update Feature

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Using the GUI](#using-the-gui)
4. [Using the Command Line](#using-the-command-line)
5. [Understanding Results](#understanding-results)
6. [Export to CSV](#export-to-csv)
7. [Filters and Search](#filters-and-search)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Introduction

### What is Figure Extraction?

The Figure Extraction feature automatically identifies and extracts **numerical data, statistics, and dates** from your documents. This is particularly useful for:

- **Updating budget figures** (e.g., 2025 → 2026 budget updates)
- **Data analysis** across multiple documents
- **Quick reference** of all figures in a document
- **Fact-checking** and verification
- **Creating data summaries** from text

### What Can Be Extracted?

| Type | Examples | Use Cases |
|------|----------|-----------|
| **Currency** | €45.3 milliards, $1.5M, 100 TND | Budgets, financial data |
| **Percentages** | 23.4%, 15-20% | Growth rates, statistics |
| **Dates** | 2025, 15/01/2025, janvier 2025 | Time periods, deadlines |
| **Ranges** | 2020-2025, 15%-20% | Periods, intervals |
| **Quantities** | 12,456 fonctionnaires, 500 tonnes | Counts, measurements |
| **Numbers** | 45.3, 1.234.567 | General numeric data |

---

## Quick Start

### 5-Minute Quick Start

1. **Open the Application**
   - Launch Document Processing application
   - Go to **📊 Data Update** tab

2. **Select Document**
   - Option A: Go to **📁 Files** tab first, add and select a document
   - Option B: Use "Extract Figures" button to browse for any document

3. **Extract**
   - Click **"Extract Figures from Document"**
   - Wait for progress bar (usually <5 seconds)

4. **View Results**
   - See statistics panel: Total, Currency, Percentage, Dates
   - Browse results table with all extracted figures
   - Use filters to focus on specific types

5. **Export (Optional)**
   - Click **"Export to CSV"** to save results
   - Choose location and filename
   - Open CSV in Excel, LibreOffice, or text editor

---

## Using the GUI

### 1. Opening the Data Update Tab

After launching the application:

```
Main Window → Tabs → 📊 Data Update
```

The Data Update tab contains:
- **Header**: Feature title
- **Extraction Control**: Button to start extraction
- **Progress Bar**: Shows extraction progress
- **Status Label**: Current operation status
- **Statistics Panel**: Counts by figure type
- **Filter Panel**: Type and table filters
- **Results Table**: All extracted figures with details
- **Action Buttons**: Export, Update, Clear

### 2. Extracting Figures

#### Method A: From Project Documents

1. Go to **📁 Files** tab
2. If not already added, click **"Add"** to add documents
3. **Select** a document in the list (single click to highlight)
4. Go to **📊 Data Update** tab
5. Click **"Extract Figures from Document"**
6. The selected document will be processed

#### Method B: From Any Document

1. Go to **📊 Data Update** tab
2. Click **"Extract Figures from Document"**
3. File picker will open
4. Navigate to your document
5. Select PDF, DOCX, or TXT file
6. Click **"Open"**

### 3. During Extraction

You'll see real-time progress:

```
[=====>     ] 50%
Initializing figure extractor...
Loading document...
Extracted 42 figures...
Extraction complete!
```

**Processing Times**:
- Small file (10 KB): <1 second
- Medium file (500 KB): 1-2 seconds
- Large file (2 MB PDF): 3-5 seconds

### 4. Viewing Results

#### Statistics Panel

Shows overview of extraction:
```
Total: 45  Currency: 12  Percentage: 8  Dates: 15
```

- **Total**: All figures found
- **Currency**: Money amounts (€, $, TND, etc.)
- **Percentage**: Rates and percentages
- **Dates**: Years, dates, periods

#### Results Table

Each row shows:

| Column | Description | Example |
|--------|-------------|---------|
| **Select** | Checkbox for selection | ☐ |
| **Type** | Figure category (color-coded) | Currency (green) |
| **Value** | Original text | €45.3 milliards |
| **Numeric** | Parsed number | 45,300,000,000.00 |
| **Unit/Currency** | Unit or currency code | EUR |
| **Year** | Associated year | 2025 |
| **Location** | Where in document | Page 1, Para 3 |
| **Context** | Surrounding text | Le budget... |

**Color Coding**:
- 🟢 **Green** = Currency
- 🟠 **Orange** = Percentage
- 🔵 **Blue** = Date
- ⚪ **White** = Other types

### 5. Using Filters

#### Filter by Type

Use the dropdown to show only:
- **All** (default)
- Currency only
- Percentage only
- Date only
- Range only
- Quantity only
- Number only

#### Tables Only

Check **"Tables only"** to show only figures extracted from document tables.

This is useful when you want to focus on structured data like:
- Budget tables
- Financial statements
- Statistical tables

### 6. Selecting Figures

- Click **checkboxes** in the "Select" column
- Select multiple figures for export or update
- Selection persists when using filters

---

## Using the Command Line

### Standalone Test Script

For quick extraction without GUI:

```bash
# Navigate to project
cd /Users/peng/Documents/mse/private/Document-Processing

# Activate virtual environment
source .venv/bin/activate

# Extract from a document
python test_figure_extraction.py path/to/document.pdf
```

### Output

```
📄 Testing Figure Extraction
================================================================================
Document: document.pdf
File size: 234.56 KB
================================================================================

🔍 Initializing figure extractor...
📊 Extracting figures from document.pdf...

================================================================================
✅ EXTRACTION RESULTS
================================================================================
Total figures extracted: 45
Tables parsed: 2
Extraction time: 2.34 seconds

📈 Breakdown by Type:
  Currency: 12
  Percentage: 8
  Date: 15
  Quantity: 7
  Number: 3

================================================================================
📋 DETAILED FIGURES
================================================================================

[1] CURRENCY
  Value: €45.3 milliards
  Numeric: 45,300,000,000.00
  Currency: EUR
  Year: 2025
  Location: Page 1, Paragraph 3
  Context: Le budget de l'État en 2025 s'élève à €45.3 milliards...

[2] PERCENTAGE
  Value: 23.4%
  Numeric: 23.40
  Unit: %
  Year: 2025
  Location: Page 1, Paragraph 4
  Context: Le taux de croissance est de 23.4%...

... (showing first 20 figures)
```

---

## Understanding Results

### Numeric Value Parsing

The extractor converts various number formats to standard numeric values:

**European Format**:
```
Input:  €1.234.567,89
Output: 1234567.89
```

**US Format**:
```
Input:  $1,234,567.89
Output: 1234567.89
```

**French Format**:
```
Input:  1 234 567,89 euros
Output: 1234567.89
```

### Multipliers

Multipliers are automatically applied:

| Multiplier | Factor | Example |
|------------|--------|---------|
| milliards, B | ×1,000,000,000 | €45.3 milliards → 45,300,000,000 |
| millions, M | ×1,000,000 | $150M → 150,000,000 |
| milliers, k | ×1,000 | 5 milliers → 5,000 |

### Year Context

Years are extracted from context even if not in the figure value:

```
Text: "Le budget en 2025 s'élève à €45.3 milliards"

Extracted:
- Value: €45.3 milliards
- Year: 2025 (from context)
```

### Table Figures

Figures from tables include structure information:

```
Location: Table 0, Row 2, Column 1 (Column: Budget)
```

This tells you:
- Which table (if document has multiple)
- Row and column position
- Column header name

---

## Export to CSV

### How to Export

1. After extraction completes
2. Optionally apply filters to export only specific figures
3. Click **"Export to CSV"** button
4. Choose save location
5. Enter filename (default: `figures_export_YYYYMMDD_HHMMSS.csv`)
6. Click **"Save"**

### CSV Structure

The exported CSV contains these columns:

```csv
Type,Value,Numeric Value,Unit/Currency,Year,Page,Paragraph,Is From Table,Table Index,Table Row,Table Column,Table Row Header,Table Column Header,Context Sentence,Confidence Score
currency,€45.3 milliards,45300000000.0,EUR,2025,1,3,No,,,,,,Le budget de l'État en 2025...,1.0
percentage,23.4%,23.4,%,2025,1,4,No,,,,,,Le taux de croissance est de 23.4%...,1.0
```

### Opening in Excel

1. Open Excel
2. **File → Open** → Select CSV file
3. Excel will auto-detect columns
4. Data is now in spreadsheet format

**Tip**: Use Excel's filter and sort features on the exported data!

### Opening in LibreOffice Calc

1. Open LibreOffice Calc
2. **File → Open** → Select CSV file
3. Text Import dialog appears
4. Settings:
   - Separator: **Comma**
   - Text delimiter: **"** (quote)
   - Character set: **UTF-8**
5. Click **OK**

### CSV Use Cases

**Data Analysis**:
- Import into Python/R for statistical analysis
- Create pivot tables in Excel
- Generate charts and visualizations

**Data Migration**:
- Update figures in batch
- Transfer data to databases
- Integrate with other systems

**Documentation**:
- Create figure inventories
- Track data sources
- Audit numerical data

---

## Filters and Search

### Filtering by Type

**Example Workflows**:

**Find all budget amounts**:
1. Set filter to **"Currency"**
2. All monetary figures shown
3. Sort by numeric value to find largest/smallest

**Find all growth rates**:
1. Set filter to **"Percentage"**
2. All percentages shown
3. Check year column to compare periods

**Find specific years**:
1. Set filter to **"Date"**
2. Look at the Year column
3. Find all references to specific year

### Table-Only Filter

**When to use**:
- You only need structured data
- Filtering out narrative text figures
- Comparing tabular data across documents

**Example**:
```
Document has:
- Text: "Budget 2025 is €45.3M" ← Excluded
- Table: Budget | 45.3 ← Included
```

### Multi-Level Filtering

Combine filter types:

1. **Filter by "Currency"** → Only money figures
2. **Check "Tables only"** → Only from tables
3. **Select specific rows** → For export

Result: CSV with only currency figures from tables

---

## Tips and Best Practices

### Document Preparation

**Best Results**:
- ✅ Text-based PDFs (not scanned images)
- ✅ Clean DOCX files from Word/LibreOffice
- ✅ Well-structured tables with headers
- ✅ Consistent number formats

**May Have Issues**:
- ⚠️ Scanned PDFs (OCR not yet supported)
- ⚠️ Complex merged table cells
- ⚠️ Hand-written numbers in images
- ⚠️ Unusual number formats

### Performance Tips

**For Large Documents**:
1. Extract figures once, save CSV
2. Use CSV for repeated analysis
3. Process documents in batches
4. Close other applications if slow

**Processing Speed**:
- 50-page PDF: ~5-10 seconds
- 100-page PDF: ~10-20 seconds
- Very slow? Check if PDF is scanned

### Accuracy Tips

**Improve Accuracy**:
1. Use original documents (not photocopies)
2. Ensure proper encoding (UTF-8)
3. Check extracted figures against source
4. Report patterns that are missed

**Verify Results**:
- Spot-check 10-20 random figures
- Compare totals with expected ranges
- Review context sentences for relevance

### Workflow Recommendations

**Research Workflow**:
1. Add all research documents to project
2. Extract figures from each
3. Export all to separate CSVs
4. Merge CSVs for analysis

**Update Workflow**:
1. Extract figures from old document
2. Note years and values
3. Search for updated figures (future feature)
4. Update document with new values

**Verification Workflow**:
1. Extract figures from document
2. Export to CSV
3. Share CSV with team
4. Team verifies accuracy
5. Use verified figures in final document

---

## Troubleshooting

### Issue: "No figures found"

**Possible Causes**:
- Document is scanned (image-based PDF)
- Unusual number formats
- Figures embedded in images

**Solutions**:
1. Check if text is selectable in PDF viewer
2. Try converting to DOCX first
3. Use a different PDF export tool
4. Enable OCR if available (future feature)

### Issue: Wrong numeric values

**Example**: "1.234" extracted as "1.234" instead of "1234"

**Cause**: Number format ambiguity

**Current Logic**:
- **1.23** → decimal (1.23)
- **1.234** → may be ambiguous
- **1.234.567** → thousands (1234567)

**What to do**:
- Check context to verify
- Report if consistently wrong
- Edit CSV if needed

### Issue: Year not detected

**Example**: Figure shows Year: (empty)

**Cause**: Year not mentioned near figure

**Solution**:
- This is expected behavior
- Manually add year in CSV if needed
- Or add year to document text

### Issue: Slow extraction

**Symptoms**: Takes >30 seconds for small file

**Possible Causes**:
- Very large document
- Complex tables
- System resource issues

**Solutions**:
1. Close other applications
2. Check CPU/memory usage
3. Process smaller sections
4. Restart application

### Issue: Table figures missing

**Symptoms**: Tables in DOCX but figures not extracted

**Check**:
- Are cells merged? (may cause issues)
- Are numbers in separate cells or combined with text?
- Is it actually a table or just aligned text?

**Solution**:
- Simplify table structure
- Separate numbers from text
- Report complex table patterns

### Issue: Export fails

**Error**: "Failed to export CSV"

**Solutions**:
1. Check file permissions (can you write to that folder?)
2. Try different save location
3. Close file if already open
4. Check disk space

### Issue: Unicode/special characters

**Symptoms**: € or è characters look wrong in CSV

**Solution**:
- CSV is saved with UTF-8 encoding
- When opening in Excel: **Data → Get Data → From Text/CSV** → Set encoding to UTF-8
- LibreOffice: Select UTF-8 in import dialog

---

## FAQ

### General Questions

**Q: How accurate is the extraction?**

A: For well-formatted documents with clear numbers, accuracy is typically 95%+. Always spot-check results, especially for critical data.

**Q: Can I extract from multiple documents at once?**

A: Currently, you must extract one document at a time. Export each to CSV, then merge CSVs using Excel or a script.

**Q: Is my data sent anywhere?**

A: No. All processing happens locally on your computer. No data is sent to external servers.

**Q: Can I modify figures in the application?**

A: Not directly in the application. Export to CSV, edit in spreadsheet software, then use the updated CSV.

### Technical Questions

**Q: What file formats are supported?**

A:
- ✅ **PDF** (text-based only, not scanned)
- ✅ **DOCX** (Microsoft Word, LibreOffice)
- ✅ **TXT** (plain text)
- ❌ **ODT, RTF, HTML** (not yet supported)
- ❌ **Scanned PDFs** (OCR not yet implemented)

**Q: Are tables in PDFs extracted?**

A: Not yet. Currently, only tables in DOCX files are parsed. PDF table extraction is planned for a future version.

**Q: What number formats are supported?**

A:
- European: `1.234.567,89`
- US/UK: `1,234,567.89`
- French: `1 234 567,89`
- Mixed formats in same document are handled

**Q: Can I add custom figure patterns?**

A: Not through the GUI currently. This is a planned feature. Advanced users can modify `figure_extractor.py`.

### Usage Questions

**Q: How do I find the largest budget item?**

A:
1. Extract figures
2. Filter by "Currency"
3. Export to CSV
4. Open in Excel
5. Sort by "Numeric Value" column (descending)

**Q: Can I compare figures across years?**

A:
1. Extract from all documents
2. Export each to CSV
3. In Excel, open all CSVs
4. Use VLOOKUP or pivot tables to compare

**Q: How do I update figures in my document?**

A: Currently manual:
1. Extract figures → CSV
2. Find figures to update
3. Manually edit document
4. Future: Automated update feature planned

**Q: Can I search for specific figures?**

A: Use CSV export:
1. Export to CSV
2. Open in Excel
3. Use Ctrl+F (Find) to search
4. Or use Excel filters

---

## Next Steps

### After Extracting Figures

**For Analysis**:
1. Export to CSV
2. Use Excel/Python/R for analysis
3. Create visualizations
4. Generate reports

**For Updates** (Future Feature):
1. Note figures to update
2. Search for updated values online
3. Review and approve changes
4. Update document automatically

### Getting Help

**Documentation**:
- This User Guide
- `TESTING_GUIDE.md` - Feature details
- `MANUAL_TESTING_STEPS.md` - Detailed testing
- `GUI_INTEGRATION.md` - Technical details

**Reporting Issues**:
1. Note the issue details
2. Save problem document (if shareable)
3. Export extraction results (if any)
4. Report to project maintainer

**Feature Requests**:
- Additional figure types
- New export formats
- Custom patterns
- Automation features

---

## Appendix: Example Use Cases

### Use Case 1: Budget Update Project

**Scenario**: Law researcher needs to update all 2025 budget figures to 2026 in a 100-page thesis.

**Workflow**:
1. Extract figures from thesis PDF
2. Filter by "Currency" type
3. Filter by "Year: 2025"
4. Export matching figures to CSV
5. Create update list
6. Manually update in document (automated update coming soon)

### Use Case 2: Multi-Document Analysis

**Scenario**: Compare employment statistics across 10 government reports.

**Workflow**:
1. Add all reports to project
2. For each report:
   - Extract figures
   - Filter by "Quantity"
   - Export to CSV (e.g., `report1_figures.csv`)
3. Merge all CSVs
4. Analyze in Excel with pivot tables

### Use Case 3: Data Verification

**Scenario**: Verify accuracy of figures cited in a research paper.

**Workflow**:
1. Extract figures from paper
2. Export to CSV
3. Share CSV with research team
4. Team checks each figure against sources
5. Add verification column in CSV
6. Identify and correct errors

### Use Case 4: Figure Inventory

**Scenario**: Create inventory of all statistical claims in a document.

**Workflow**:
1. Extract all figures
2. Review "Context" column
3. Categorize by topic
4. Create summary table
5. Use for fact-checking

---

**Version**: 1.0
**Last Updated**: 2026-01-06
**For Application**: Document Processing - Figure Extraction Feature
