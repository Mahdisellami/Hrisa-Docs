# Customer Meeting Demo Checklist

**Date**: January 11, 2026
**Purpose**: Gather feedback for final v0.1.0 release

---

## ✅ Pre-Meeting Preparation

### 1. Application Ready
- [ ] Latest build installed: `dist/Hrisa Docs.app`
- [ ] Ollama running: `ollama serve` (check with `curl http://localhost:11434/api/version`)
- [ ] LLM model downloaded: `ollama pull llama3.1:latest`
- [ ] Test project ready: "AI Governance Research" with 8 documents

### 2. Demo Materials
- [ ] Screenshots available in `docs/screenshots/`
- [ ] Test documents in `test_documents/` (8 legal research papers)
- [ ] README.md with screenshots section ready to show

### 3. Technical Setup
- [ ] Stable internet connection (for any questions/lookups)
- [ ] Laptop charged or plugged in
- [ ] Display settings optimized (brightness, resolution)
- [ ] Notifications disabled to avoid interruptions

---

## 🎯 Demo Flow (15-20 minutes)

### Part 1: Introduction (2 minutes)
**Show**: README.md with screenshots

**Key Points**:
- "Hrisa Docs consolidates research papers into synthesized books"
- "Uses local AI - all your data stays private on your machine"
- "Multi-language support: French, English, Arabic"

### Part 2: Project Management (2 minutes)
**Show**: Project dashboard

**Demonstrate**:
1. Click "Manage Projects" → Show project list
2. Point out project statistics (docs, themes, tasks)
3. Show right-click context menu (Duplicate, Rename, Delete)

**Key Points**:
- "Manage multiple research projects easily"
- "Quick statistics at a glance"

### Part 3: Document Import (3 minutes)
**Show**: Empty project → Import flow

**Demonstrate**:
1. Create new project or use existing "AI Governance Research"
2. Go to "Documents source" tab
3. Click "Add" → Select multiple .txt files from `test_documents/`
4. Show document list with file sizes

**Key Points**:
- "Supports PDF, DOCX, TXT formats"
- "Import multiple files at once"
- "Automatic text extraction"

### Part 4: Processing (3 minutes)
**Show**: Processing workflow

**Demonstrate**:
1. Click "Process Documents"
2. Show progress indicator
3. Wait for completion dialog (~30 seconds for 8 docs)
4. Show success message with statistics

**Key Points**:
- "Chunks documents into meaningful segments"
- "Creates embeddings for semantic search"
- "Fast: ~30 seconds per 100 pages"

### Part 5: Theme Discovery (4 minutes)
**Show**: Theme analysis

**Demonstrate**:
1. Go to "Themes" tab
2. Click "Discover Themes"
3. Show discovered themes with percentages:
   - Technology Governance
   - Algorithmic Accountability
   - AI and Surveillance Risks
   - Algorithmic Transparency Challenges
   - Worker Interests
   - Liability for AI Harms
   - (and more)

**Key Points**:
- "AI automatically identifies major themes"
- "Clustering based on semantic similarity"
- "Percentage shows theme importance"
- "Can rename, merge, or delete themes"

### Part 6: Synthesis (4 minutes)
**Show**: Book generation

**Demonstrate**:
1. Go to "Synthesis" tab
2. Show configuration options:
   - Number of themes
   - Detail level (Normal, High)
   - Output format (Markdown, DOCX)
3. Click "Start Synthesis"
4. Show progress with chapter names
5. Show generated output location

**Key Points**:
- "Generates coherent chapters from themes"
- "Includes citations to source documents"
- "Export to Markdown or Word"
- "Takes ~1-2 minutes per chapter"

### Part 7: Bonus Features (2 minutes)
**Show**: Additional capabilities

**Demonstrate**:
1. **Figure Extraction**: Show figure extraction tab with tables
2. **Settings**: Show language, theme, LLM model options
3. **URL Import**: Mention web article import capability

---

## 💬 Questions to Ask Customer

### Feature Feedback
1. **Workflow**: Does the workflow (Import → Process → Discover → Synthesize) make sense?
2. **UI/UX**: Is the interface intuitive? Any confusing elements?
3. **Speed**: Are processing times acceptable?
4. **Themes**: Do the discovered themes seem meaningful and accurate?
5. **Output**: Is the synthesized content quality satisfactory?

### Missing Features
6. **Formats**: What other document formats would you like to import?
7. **Export**: What other export formats do you need? (LaTeX, EPUB, PDF?)
8. **Citations**: Do you need BibTeX or other citation formats?
9. **Languages**: Do you need additional language support?
10. **Collaboration**: Would multi-user/cloud sync be valuable?

### Pain Points
11. **Installation**: Any difficulties installing or first-time setup?
12. **Errors**: Have you encountered any bugs or crashes?
13. **Documentation**: Is anything unclear in the guides?
14. **Performance**: Any slowness or memory issues?

### Priority Ranking
15. Which features would you prioritize for the next release?
16. What would make this tool indispensable for your work?

---

## 📝 Feedback Collection Template

```markdown
## Customer Feedback - [Customer Name]
**Date**: January 11, 2026
**Version Shown**: v0.1.0-pre

### What They Liked
-
-

### What They Found Confusing
-
-

### Feature Requests
1.
2.
3.

### Bug Reports
-
-

### Priority Features for v0.2.0
1.
2.
3.

### Overall Impression
[1-5 stars]: ⭐⭐⭐⭐⭐

### Would They Use It?
[ ] Yes, immediately
[ ] Yes, after [specific feature]
[ ] Maybe
[ ] No

### Notes
```

---

## 🐛 Known Issues to Mention (If Asked)

**Addressed**:
- ✅ Translation keys fixed
- ✅ Theme labels cleaned up (no markdown formatting)

**Limitations**:
- Requires Ollama to be running locally
- Processing time depends on document size
- PDF export requires pandoc + XeLaTeX installation (optional)
- Windows installer not yet tested (coming via GitHub Actions)

**Not Bugs, By Design**:
- All processing local (privacy-first means no cloud)
- Requires decent RAM (8GB min, 16GB recommended)
- LLM quality depends on model used (llama3.1 recommended)

---

## ✅ Post-Meeting Actions

After the meeting:

1. **Document Feedback**
   - Save notes to `CUSTOMER_FEEDBACK_[DATE].md`
   - Categorize: bugs, feature requests, UI improvements

2. **Prioritize Fixes**
   - Critical bugs → Fix immediately
   - Quick wins → Include in v0.1.0
   - Larger features → Plan for v0.2.0

3. **Update Roadmap**
   - Add requested features to `FUTURE_WORK.md`
   - Update priority based on customer needs

4. **Implement Fixes**
   - Make necessary changes
   - Test thoroughly
   - Document in CHANGELOG.md

5. **Prepare Final Release**
   - Squash commits again
   - Create v0.1.0 tag
   - Prepare release notes
   - Make repository public

---

## 🎉 Success Criteria

Meeting is successful if:
- [ ] Customer understands the value proposition
- [ ] Customer can see themselves using it
- [ ] We identify 2-3 critical improvements for v0.1.0
- [ ] We have clear direction for v0.2.0
- [ ] Customer is willing to test the final release

Good luck! 🚀
