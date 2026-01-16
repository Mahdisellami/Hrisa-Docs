# Manual Testing Strategy - Step-by-Step Guide

## 📋 Overview

This guide provides **detailed, step-by-step instructions** for manually testing the Figure Extraction feature.

**Time Required**: ~30-45 minutes
**Prerequisites**: Application setup complete (`.venv` installed)

---

## 🎯 Testing Strategy

We'll test in 6 progressive stages:
1. **Setup & Verification** - Ensure environment is ready
2. **Basic Text Extraction** - Simple test cases
3. **DOCX with Tables** - Complex documents
4. **PDF Extraction** - Real-world documents
5. **Edge Cases** - Unusual formats
6. **Performance Testing** - Large documents

---

## Stage 1: Setup & Verification (5 minutes)

### Step 1.1: Verify Environment

**Open terminal** and navigate to project:
```bash
cd /Users/peng/Documents/mse/private/Document-Processing
```

**Verify virtual environment**:
```bash
ls .venv/
# Expected: Should see bin/, lib/, etc.
```

**Activate virtual environment** (if needed):
```bash
source .venv/bin/activate
# Your prompt should change to show (.venv)
```

### Step 1.2: Verify Dependencies

**Check if python-docx is installed**:
```bash
.venv/bin/python -c "import docx; print('✅ python-docx installed')"
```

**Expected Output**: `✅ python-docx installed`

**If error**: Run `pip install python-docx`

**Check if PyMuPDF is installed**:
```bash
.venv/bin/python -c "import fitz; print('✅ PyMuPDF installed')"
```

**Expected Output**: `✅ PyMuPDF installed`

**If error**: Run `pip install PyMuPDF`

### Step 1.3: Verify Test Script Exists

**Check script is present**:
```bash
ls -lh test_figure_extraction.py
```

**Expected Output**: Shows file with executable permissions (`-rwxr-xr-x`)

**Make executable if needed**:
```bash
chmod +x test_figure_extraction.py
```

### Step 1.4: Run Automated Tests (Baseline)

**Run the automated test suite**:
```bash
.venv/bin/pytest tests/unit/test_figure_extractor.py -v
```

**Expected Output**:
```
==================== 17 passed in 0.XX s ====================
```

**✅ If all 17 tests pass**: Environment is ready, proceed to Stage 2
**❌ If tests fail**: Stop and report which tests failed

---

## Stage 2: Basic Text Extraction (10 minutes)

### Step 2.1: Create Simple Test File

**Create a test directory**:
```bash
mkdir -p test_documents
cd test_documents
```

**Create first test file** (`test_basic.txt`):
```bash
cat > test_basic.txt << 'EOF'
Le budget de l'État en 2025 s'élève à €45.3 milliards.
Le taux de croissance est de 23.4% par rapport à 2024.
Le ministère des Finances emploie 12,456 fonctionnaires.
Les recettes fiscales ont atteint €42.8 milliards en 2024.
EOF
```

**Verify file was created**:
```bash
cat test_basic.txt
# Should display the 4 lines above
```

### Step 2.2: Run Extraction on Simple Text

**Run test script**:
```bash
cd ..  # Back to project root
python test_figure_extraction.py test_documents/test_basic.txt
```

### Step 2.3: Verify Results

**Check the output sections**:

#### ✅ Checkpoint 1: Total Figures
Look for: `Total figures extracted: X`

**Expected**: Should find 6-8 figures
- €45.3 milliards
- 2025
- 23.4%
- 2024
- 12,456
- €42.8 milliards

**Record actual count**: _____________

#### ✅ Checkpoint 2: Breakdown by Type
Look for the "Breakdown by Type:" section

**Expected**:
```
Currency: 2       (€45.3 milliards, €42.8 milliards)
Percentage: 1     (23.4%)
Date: 2           (2025, 2024)
Quantity: 1       (12,456 fonctionnaires)
```

**Record what you see**:
- Currency: ___
- Percentage: ___
- Date: ___
- Quantity: ___

#### ✅ Checkpoint 3: Detailed Figures
Scroll through the "DETAILED FIGURES" section

**For each figure, verify**:

1. **€45.3 milliards**:
   - [ ] Type: CURRENCY
   - [ ] Numeric: 45,300,000,000.00
   - [ ] Currency: EUR
   - [ ] Year: 2025
   - [ ] Context: Contains "budget de l'État"

2. **23.4%**:
   - [ ] Type: PERCENTAGE
   - [ ] Numeric: 23.40
   - [ ] Unit: %
   - [ ] Year: 2024 (from context "par rapport à 2024")

3. **12,456**:
   - [ ] Type: QUANTITY
   - [ ] Contains: "fonctionnaires"
   - [ ] Numeric: ~12,456

#### ✅ Checkpoint 4: Summary by Type
Look for "SUMMARY BY TYPE:" section at the end

**Verify**:
- [ ] Currency Figures section shows €45.3 and €42.8
- [ ] Years found: [2024, 2025]

### Step 2.4: Test with Different Number Formats

**Create European format test**:
```bash
cat > test_documents/test_formats.txt << 'EOF'
Montant européen: €1.234.567,89
Montant américain: $1,234,567.89
Pourcentage: 45,3%
Année: 2025
EOF
```

**Run extraction**:
```bash
python test_figure_extraction.py test_documents/test_formats.txt
```

**Verify**:
- [ ] €1.234.567,89 → Numeric: ~1,234,567.89 (European format parsed)
- [ ] $1,234,567.89 → Numeric: ~1,234,567.89 (US format parsed)
- [ ] 45,3% → Numeric: 45.30

**Record actual values**:
- European: _______________
- US: _______________
- Percentage: _______________

---

## Stage 3: DOCX with Tables (10 minutes)

### Step 3.1: Create DOCX Test File

**You have two options**:

**Option A: Use Existing DOCX**
- Use any existing DOCX file you have
- Skip to Step 3.2

**Option B: Create New DOCX**
1. Open Microsoft Word or LibreOffice Writer
2. Create new document
3. Add text paragraph:
   ```
   Le budget prévisionnel pour 2025 est de €45.3 milliards,
   soit une augmentation de 12.5% par rapport à 2024.
   ```
4. Insert a table (3 columns × 4 rows):
   ```
   | Année | Budget (€M) | Croissance (%) |
   |-------|-------------|----------------|
   | 2023  | 40.1        | 15.2           |
   | 2024  | 42.8        | 18.5           |
   | 2025  | 45.3        | 23.4           |
   ```
5. Save as `test_documents/test_table.docx`

### Step 3.2: Run Extraction on DOCX

**Run test script**:
```bash
python test_figure_extraction.py test_documents/test_table.docx
```

### Step 3.3: Verify DOCX Results

#### ✅ Checkpoint 1: Table Detection
Look for: `Tables parsed: X`

**Expected**: Should show 1 or more tables parsed

**Record**: Tables parsed: ___

#### ✅ Checkpoint 2: Table Figures
In the "DETAILED FIGURES" section, look for table locations

**Expected format**:
```
Location: Table 0, Row 1, Col 1 (Column: Budget (€M))
```

**Verify for at least one table figure**:
- [ ] Shows "Table X" in location
- [ ] Shows Row and Column numbers
- [ ] Shows Column header if available

#### ✅ Checkpoint 3: Text vs Table Figures
Count figures from text vs tables

**From text paragraph**: Should find 3-4 figures
- €45.3 milliards
- 12.5%
- 2025, 2024

**From table**: Should find 9 figures
- 3 years (2023, 2024, 2025)
- 3 budget amounts (40.1, 42.8, 45.3)
- 3 percentages (15.2, 18.5, 23.4)

**Record**:
- Text figures: ___
- Table figures: ___
- Total: ___

### Step 3.4: Verify Table Context

**For a table figure, check**:
- [ ] `is_from_table: True` (if you check the code)
- [ ] Location shows table index
- [ ] Column header preserved
- [ ] Context makes sense

---

## Stage 4: PDF Extraction (10 minutes)

### Step 4.1: Prepare PDF Test File

**Option A: Use Existing PDF**
- Use any PDF document you have (thesis, article, report)
- Best if it has clear numbers and dates

**Option B: Create Simple PDF**
1. Open the DOCX from Stage 3
2. Save/Export as PDF: `test_documents/test_table.pdf`

### Step 4.2: Run Extraction on PDF

**Run test script**:
```bash
python test_figure_extraction.py test_documents/test_table.pdf
```

**Note**: This may take longer than TXT/DOCX (3-5 seconds for small PDF)

### Step 4.3: Verify PDF Results

#### ✅ Checkpoint 1: Basic Extraction
**Verify**:
- [ ] Script completes without errors
- [ ] Shows extraction time in seconds
- [ ] Shows total figures found

**Record**:
- Extraction time: ___ seconds
- Total figures: ___

#### ✅ Checkpoint 2: Page Numbers
In "DETAILED FIGURES", look for Location field

**Expected format**:
```
Location: Page 1, Paragraph 2
Location: Page 2, Paragraph 5
```

**Verify**:
- [ ] Page numbers are present
- [ ] Page numbers seem correct (Page 1, 2, 3, etc.)

#### ✅ Checkpoint 3: Compare with DOCX
If you used the same file converted to PDF:

**Compare results**:
- DOCX total figures: ___ (from Stage 3)
- PDF total figures: ___

**Should be similar** (±10%)

**If very different (>50% difference)**:
- PDF might be scanned (image-based, not text)
- Check if you can select text in PDF viewer
- Report this issue

### Step 4.4: Test with Real Document

**If you have a real thesis/article PDF**:

**Run extraction**:
```bash
python test_figure_extraction.py path/to/your/real_document.pdf
```

**Record**:
- File size: ___ MB
- Total pages: ___
- Extraction time: ___ seconds
- Figures found: ___
- Performance: [ ] Fast (<5s) [ ] Medium (5-15s) [ ] Slow (>15s)

**Check context quality**:
- Pick 3 random figures from output
- Read the context sentence
- [ ] Does context make sense?
- [ ] Is context relevant to figure?

---

## Stage 5: Edge Cases Testing (5 minutes)

### Step 5.1: Test Multiplier Handling

**Create test file**:
```bash
cat > test_documents/test_multipliers.txt << 'EOF'
Budget 2025: 45 milliards d'euros
Coût du projet: 250 millions d'euros
Population: 11 millions d'habitants
Petite somme: 5 milliers d'euros
Grande somme: €3.2B
Moyenne somme: €150M
EOF
```

**Run extraction**:
```bash
python test_figure_extraction.py test_documents/test_multipliers.txt
```

**Verify numeric values**:
- [ ] 45 milliards → ~45,000,000,000
- [ ] 250 millions → ~250,000,000
- [ ] 11 millions → ~11,000,000
- [ ] 5 milliers → ~5,000
- [ ] €3.2B → ~3,200,000,000
- [ ] €150M → ~150,000,000

**Record any incorrect conversions**: ________________

### Step 5.2: Test Year Context Association

**Create test file**:
```bash
cat > test_documents/test_years.txt << 'EOF'
En 2023, le budget était de €40.1 milliards.
Le budget 2024 a atteint €42.8 milliards.
Pour 2025, on prévoit €45.3 milliards.
La période 2020-2025 a vu une croissance de 15%.
EOF
```

**Run extraction**:
```bash
python test_figure_extraction.py test_documents/test_years.txt
```

**Verify year association**:
- [ ] €40.1 milliards has Year: 2023
- [ ] €42.8 milliards has Year: 2024
- [ ] €45.3 milliards has Year: 2025
- [ ] 15% has year information (maybe range)

**Key test**: Years are associated even though not in the figure value itself

### Step 5.3: Test Empty/Invalid Files

**Create empty file**:
```bash
touch test_documents/test_empty.txt
```

**Run extraction**:
```bash
python test_figure_extraction.py test_documents/test_empty.txt
```

**Expected**:
- [ ] No crash
- [ ] Shows "Total figures extracted: 0"
- [ ] Exits gracefully

**Test non-existent file**:
```bash
python test_figure_extraction.py test_documents/does_not_exist.txt
```

**Expected**:
- [ ] Shows error: "Error: File not found"
- [ ] Exits with error code
- [ ] No crash

### Step 5.4: Test Text Without Figures

**Create test file**:
```bash
cat > test_documents/test_no_figures.txt << 'EOF'
Ceci est un document sans aucun chiffre.
Il contient uniquement du texte.
Aucune statistique, aucune date, rien.
EOF
```

**Run extraction**:
```bash
python test_figure_extraction.py test_documents/test_no_figures.txt
```

**Expected**:
- [ ] Total figures: 0 or very low (1-2 false positives acceptable)
- [ ] No crash
- [ ] Completes quickly

---

## Stage 6: Performance Testing (5 minutes)

### Step 6.1: Test with Larger File

**Create large test file** (500 figures):
```bash
python -c "
for i in range(100):
    print(f'En {2020+i%6}, le budget est de €{40+i%10}.{i%10} milliards.')
    print(f'La croissance est de {15+i%10}.{i%10}%.')
    print(f'Le ministère emploie {10000+i*100} fonctionnaires.')
    print(f'Les recettes sont de ${35+i%8}.{i%10}M.')
    print()
" > test_documents/test_large.txt
```

**Run extraction and time it**:
```bash
time python test_figure_extraction.py test_documents/test_large.txt
```

**Record**:
- File size: `ls -lh test_documents/test_large.txt` → ___ KB
- Total figures found: ___
- Extraction time (real): ___ seconds
- Performance rating:
  - [ ] Excellent (<1s)
  - [ ] Good (1-3s)
  - [ ] Acceptable (3-5s)
  - [ ] Slow (>5s)

### Step 6.2: Test with Real Large Document

**If you have a large PDF/DOCX** (50+ pages):

**Run extraction**:
```bash
time python test_figure_extraction.py path/to/large_document.pdf
```

**Record**:
- Document: _____________
- Pages: ___
- File size: ___ MB
- Figures found: ___
- Extraction time: ___ seconds
- Memory usage: `ps aux | grep python` during extraction

**Performance expectations**:
- 50 pages PDF: ~5-10 seconds
- 100 pages PDF: ~10-20 seconds
- 200 pages PDF: ~20-40 seconds

**If much slower**: Report for optimization

---

## 📊 Testing Results Summary

After completing all stages, fill out:

### Summary Checklist

**Stage 1: Setup**
- [ ] Environment verified
- [ ] All dependencies installed
- [ ] Automated tests pass (17/17)

**Stage 2: Basic Text**
- [ ] Simple extraction works
- [ ] Currency detected correctly
- [ ] Percentages detected
- [ ] Dates/years detected
- [ ] Number formats handled (European/US)

**Stage 3: DOCX with Tables**
- [ ] DOCX files load
- [ ] Text figures extracted
- [ ] Table figures extracted
- [ ] Table structure preserved
- [ ] Column headers captured

**Stage 4: PDF**
- [ ] PDF files load
- [ ] Figures extracted
- [ ] Page numbers correct
- [ ] Performance acceptable

**Stage 5: Edge Cases**
- [ ] Multipliers work (milliards, millions)
- [ ] Year context association works
- [ ] Empty files handled gracefully
- [ ] Invalid files handled gracefully

**Stage 6: Performance**
- [ ] Large files process successfully
- [ ] Performance is acceptable
- [ ] No memory leaks observed

### Overall Assessment

**Total Tests Passed**: ___ / 20

**Overall Rating**:
- [ ] 🟢 Excellent (18-20 passed)
- [ ] 🟡 Good (15-17 passed)
- [ ] 🟠 Acceptable (12-14 passed)
- [ ] 🔴 Needs Work (<12 passed)

---

## 🐛 Issues Found

**List any issues encountered**:

1. **Issue**: ______________________________
   - **Test**: Stage ___, Step ___
   - **Expected**: ______________________________
   - **Actual**: ______________________________
   - **Severity**: [ ] Critical [ ] Major [ ] Minor

2. **Issue**: ______________________________
   - **Test**: Stage ___, Step ___
   - **Expected**: ______________________________
   - **Actual**: ______________________________
   - **Severity**: [ ] Critical [ ] Major [ ] Minor

3. **Issue**: ______________________________
   - **Test**: Stage ___, Step ___
   - **Expected**: ______________________________
   - **Actual**: ______________________________
   - **Severity**: [ ] Critical [ ] Major [ ] Minor

---

## 💡 Suggestions for Improvement

1. ______________________________
2. ______________________________
3. ______________________________

---

## 📁 Test Artifacts

**Save for reference**:
- [ ] All test documents created (test_documents/)
- [ ] Screenshots of successful runs (optional)
- [ ] Output logs (copy terminal output)
- [ ] This completed checklist

**Package test results**:
```bash
# Create archive of test documents
tar -czf test_results_$(date +%Y%m%d).tar.gz test_documents/ MANUAL_TESTING_STEPS.md

# Shows archive was created
ls -lh test_results_*.tar.gz
```

---

## ✅ Sign-Off

**Tester**: ___________________
**Date**: ___________________
**Time Spent**: ___ minutes
**Result**: [ ] PASS [ ] FAIL [ ] PASS WITH ISSUES

**Ready for next phase**: [ ] YES [ ] NO

**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________

---

## 🚀 Next Steps

**If all tests pass**:
→ Ready to proceed with **Feature 4.2: Figure Update Search**

**If issues found**:
→ Report issues for fixing before proceeding

**Questions?**
→ Document questions and we'll address them

---

**Good luck with testing!** 🎉
