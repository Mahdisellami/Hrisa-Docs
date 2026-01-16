# Customer Requirements Analysis

**Source**: Customer feedback (Law professor, 60+ years old)
**Context**: French legal research and thesis writing
**Date**: 2026-01-06

---

## Executive Summary

Customer requests focus on **4 major capability areas**:

1. **Document Enrichment & Updating** - Enhance existing documents with new sources and data
2. **Automated Research Workflows** - Web scraping and synthesis from legal databases
3. **Document Quality Assurance** - Plagiarism detection and AI detection
4. **Data Freshness** - Automatic updating of figures and statistics

---

## Question 1: Document Enrichment & Evaluation

### Original Request (French)
> "Est-il possible d'actualiser et d'enrichir la thèse (provided input document) à la lumière/en se servant de l'autre article et d'actualiser les indicateurs en se servant du portal finance.gov.tn en conservant le style de l'auteur et conserver le document original (la thèse, ses références etc.). Éventuellement proposer en couleur des pistes d'amélioration quand à la forme et quand au fond. Générer un rapport d'évaluation sur la thèse en question: Points forts, points faibles, suggestions, Éditeur du document etc."

### Translation
"Is it possible to update and enrich the thesis (provided input document) in light of/using the other article and update the indicators using the portal finance.gov.tn while preserving the author's style and keeping the original document (the thesis, its references etc.). Eventually propose in color improvement suggestions regarding form and substance. Generate an evaluation report on the thesis in question: Strengths, weaknesses, suggestions, Document editor etc."

### Task Types

1. **Document Enrichment**
   - Add new information from secondary sources
   - Update statistics/indicators from web portals
   - Preserve original structure and references

2. **Style Preservation**
   - Maintain author's writing style
   - Match tone and vocabulary
   - Keep formatting consistent

3. **Document Evaluation**
   - Generate quality assessment report
   - Identify strengths and weaknesses
   - Provide improvement suggestions

4. **Visual Editing**
   - Highlight suggested changes in color
   - Track changes mode
   - Compare versions

### Features to Implement

#### Feature 1.1: Document Enrichment Engine
**Description**: Enrich existing document with information from new sources

**Capabilities**:
- Load primary document (thesis)
- Load secondary sources (articles, papers)
- Identify relevant sections for enrichment
- Insert new information while maintaining context
- Preserve original references
- Add new citations for added content

**Technical Approach**:
- Use RAG to find relevant information in secondary sources
- Use LLM to rewrite additions in author's style
- Style transfer using few-shot learning from original document
- Track original vs. enriched content

**Inputs**:
- Primary document (thesis/dissertation)
- Secondary sources (articles, papers)
- Web portals for data (finance.gov.tn)

**Outputs**:
- Enriched document (DOCX with track changes)
- Change report (what was added where)
- Citation list for new content

#### Feature 1.2: Web Portal Data Integration
**Description**: Fetch updated statistics from government portals

**Capabilities**:
- Browse finance.gov.tn portal
- Navigate to "Loi de finance" sections
- Extract "rapport sur les articles publiques"
- Extract "activités des fonds..."
- Parse tables and figures
- Map to document sections needing updates

**Technical Approach**:
- WebFetch tool for HTTP requests
- HTML parsing (BeautifulSoup)
- Table extraction (pandas)
- PDF parsing if reports are PDFs
- Named Entity Recognition to match indicators

**Target Portals**:
- https://www.finances.gov.tn/
- https://data.gov.tn/fr/
- http://www.ins.tn/ (Institut National de la Statistique)

#### Feature 1.3: Style-Preserving Text Generation
**Description**: Generate new text matching author's style

**Capabilities**:
- Analyze author's writing style from original document
- Extract style features:
  - Vocabulary level and domain
  - Sentence structure (simple/complex)
  - Paragraph length
  - Tone (formal/academic)
  - Use of citations
- Generate new content in matching style

**Technical Approach**:
- Style analysis using spaCy
- Few-shot prompting with original examples
- Temperature control for formality
- Vocabulary constraints from original document

**Prompt Template**:
```
Original author's writing style:
[3-5 paragraph examples from thesis]

New information to integrate:
[Extracted from secondary source]

Task: Rewrite the new information in the original author's style, maintaining:
- Formal academic tone
- Similar vocabulary level
- Comparable sentence structure
- Proper citations
```

#### Feature 1.4: Document Evaluation & Report Generation
**Description**: Generate comprehensive evaluation report

**Capabilities**:
- Analyze document structure
- Assess argumentation quality
- Check citation completeness
- Evaluate clarity and coherence
- Identify missing elements
- Suggest improvements (form and substance)

**Report Sections**:
1. **Executive Summary**
2. **Strengths** (Points forts)
   - Strong arguments
   - Well-supported claims
   - Clear structure
   - Comprehensive citations
3. **Weaknesses** (Points faibles)
   - Weak arguments
   - Unsupported claims
   - Unclear sections
   - Missing citations
   - Outdated data
4. **Suggestions** (Suggestions)
   - Form (structure, clarity, formatting)
   - Substance (argumentation, evidence, coverage)
5. **Improvement Roadmap**

**Technical Approach**:
- Document structure analysis (headings, sections)
- Citation analysis (completeness, recency)
- Argumentation mining (claims → evidence)
- Coherence analysis (logical flow)
- Comparison with similar documents (benchmarking)

#### Feature 1.5: Visual Change Tracking
**Description**: Highlight changes and suggestions in color

**Capabilities**:
- Track changes mode (like Word)
- Color-coded suggestions:
  - 🟢 Green: Additions
  - 🔴 Red: Deletions
  - 🟡 Yellow: Style suggestions
  - 🔵 Blue: Substantive improvements
- Accept/reject interface
- Version comparison

**Technical Approach**:
- DOCX track changes API (python-docx)
- Comment insertion for suggestions
- Diff algorithm for version comparison

---

## Question 2: Automated Research Workflow

### Original Request (French)
> "Est-ce qu'on peut concevoir un workflow/une pipeline pareil:
> 1. Aller à droit.cairn.info
> 2. Thème = budget vert (en se servant du moteur de recherche)
> 3. Sélectionner 1 ou plusieurs articles (human-in-the-loop)
> 4. Fournir résumé/synthèse pertinente sur le thème à partir des articles sélectionnés en citant les auteurs/sources en bas de page"

### Translation
"Can we design a workflow/pipeline like this:
1. Go to droit.cairn.info
2. Theme = green budget (using search engine)
3. Select 1 or more articles (human-in-the-loop)
4. Provide relevant summary/synthesis on the theme from selected articles citing authors/sources in footnotes"

### Task Types

1. **Web-Based Research**
   - Access legal databases
   - Search by topic/theme
   - Retrieve article metadata

2. **Human-in-the-Loop Selection**
   - Present results to user
   - Allow selection of relevant articles
   - Download/import selected articles

3. **Targeted Synthesis**
   - Synthesize only selected articles
   - Focus on specific theme
   - Generate proper footnote citations

### Features to Implement

#### Feature 2.1: Legal Database Integration
**Description**: Connect to legal research databases

**Supported Databases**:
- https://shs.cairn.info/ (Cairn - Social Sciences)
- https://droit.cairn.info/ (Cairn - Law)
- https://www.labase-lextenso.fr/ (Lextenso)
- https://www.dalloz.fr/ (Dalloz)
- https://app.dbprofiscal.com/ (DB Pro Fiscal - requires auth)
- https://jibaya.tn/documentation/ (Tunisian legal docs)

**Capabilities**:
- Search by keywords/themes
- Filter by date, author, publication
- Retrieve article metadata (title, authors, abstract, URL)
- Download full-text (if accessible)
- Handle paywalls/authentication

**Technical Approach**:
- WebSearch tool for public databases
- WebFetch tool for specific URLs
- Selenium/Playwright for dynamic sites
- API integration if available
- PDF download and parsing

#### Feature 2.2: Interactive Article Selection UI
**Description**: User interface for selecting articles from search results

**Capabilities**:
- Display search results in table:
  - Title
  - Authors
  - Publication date
  - Abstract/snippet
  - Relevance score
- Checkboxes for selection
- Preview pane for full abstract
- "Select all" / "Select none" options
- Import selected articles

**UI Design**:
```
┌─────────────────────────────────────────────────────────┐
│  Research Workflow: Green Budget (budget vert)          │
├─────────────────────────────────────────────────────────┤
│  Search Results (42 articles found)                     │
│                                                          │
│  [✓] Article 1 Title                                    │
│      Authors: Smith J., Dupont M. | Date: 2024          │
│      Abstract: This article discusses...                │
│                                                          │
│  [ ] Article 2 Title                                    │
│      Authors: Martin L. | Date: 2023                    │
│      Abstract: An analysis of...                        │
│                                                          │
│  [✓] Article 3 Title                                    │
│      Authors: Bernard K., Chen Y. | Date: 2025          │
│      Abstract: Recent developments in...                │
│                                                          │
│  [Select All] [Select None] [Import Selected (2)]      │
└─────────────────────────────────────────────────────────┘
```

**Technical Approach**:
- PyQt6 table widget
- Sortable/filterable columns
- Async download of selected articles
- Progress indicator during import

#### Feature 2.3: Thematic Synthesis with Proper Citations
**Description**: Generate synthesis focused on specific theme with footnotes

**Capabilities**:
- Synthesize only selected articles (not entire corpus)
- Focus on specific research theme
- Generate academic footnote citations (not in-text)
- Support citation styles: Chicago, Bluebook (legal), APA

**Citation Format** (Footnote):
```
1. Jean Dupont, "Le budget vert en France", Revue de droit public, vol. 45, n° 2, 2024, p. 123-145.

2. Marie Martin, "Finances durables et transition écologique", Dalloz, 2023, p. 67.

3. Ibid., p. 68.

4. J. Dupont, op. cit., p. 130.
```

**Technical Approach**:
- Modified synthesis engine for thematic focus
- Citation extraction from article metadata
- Footnote formatter (not bibliography)
- Support for "Ibid." and "op. cit."

#### Feature 2.4: Research Workflow Orchestration
**Description**: End-to-end workflow automation

**Workflow Steps**:
1. **User Input**
   - Research theme/question
   - Target database(s)
   - Date range, language filters

2. **Automated Search**
   - Query databases
   - Aggregate results
   - Rank by relevance

3. **Human Selection**
   - Present results in UI
   - User selects relevant articles
   - Confirm selection

4. **Article Import**
   - Download full-text
   - Parse and chunk
   - Store in vector DB

5. **Thematic Synthesis**
   - Generate synthesis focused on theme
   - Add footnote citations
   - Export to DOCX/PDF

6. **Review & Export**
   - User reviews synthesis
   - Make edits if needed
   - Export final document

**UI Workflow**:
- New tab: "Research Workflow"
- Wizard-style interface (step-by-step)
- Save/resume workflow state

---

## Question 3: Document Quality Assurance

### Original Request (French)
> "Regardant le workflow de synthèse existant, après la génération de la synthèse, est-ce qu'on peut purger le document de tout risque de plagiat ou bien qu'on détecte s'il est généré par l'IA, un humain ou hybride (AI comme assistant)."

### Translation
"Regarding the existing synthesis workflow, after generating the synthesis, can we purge the document of all plagiarism risk or detect if it's generated by AI, human, or hybrid (AI as assistant)."

### Task Types

1. **Plagiarism Detection**
   - Check against source documents
   - Identify verbatim copying
   - Detect paraphrasing without attribution

2. **AI Detection**
   - Classify text as AI-generated, human-written, or hybrid
   - Provide confidence scores
   - Highlight AI-likely sections

3. **Document Sanitization**
   - Rewrite problematic sections
   - Add missing citations
   - Ensure originality

### Features to Implement

#### Feature 3.1: Plagiarism Detection Engine
**Description**: Detect plagiarism from source documents

**Capabilities**:
- Compare synthesis against source documents
- Identify:
  - Verbatim copying (exact matches)
  - Near-verbatim copying (minor changes)
  - Paraphrasing without citation
- Generate similarity scores per section
- Highlight problematic passages

**Technical Approach**:
- **Exact matching**: String matching algorithms
- **Semantic similarity**: Embedding-based similarity
  - Embed synthesis sentences
  - Embed source document sentences
  - Compute cosine similarity
  - Flag high-similarity pairs (>0.85)
- **N-gram overlap**: Check for phrase-level copying
- **Citation verification**: Check if high-similarity passages are cited

**Output**:
```
Plagiarism Report:
- Overall similarity: 23%
- Sections flagged: 3

Section 1 (Page 2, Paragraph 3):
  "Les finances publiques durables sont..."
  Similarity: 92% with Source Document 2 (Page 45)
  Status: ⚠️ NOT CITED

Section 2 (Page 5, Paragraph 1):
  "Le budget vert constitue un outil..."
  Similarity: 88% with Source Document 1 (Page 12)
  Status: ✅ CITED

Recommendations:
1. Add citation for Section 1
2. Rephrase Section 1 to reduce similarity
```

#### Feature 3.2: AI-Generated Text Detection
**Description**: Detect if text is AI-generated, human-written, or hybrid

**Capabilities**:
- Classify entire document
- Classify individual sections/paragraphs
- Provide confidence scores
- Explain classification (features used)

**Technical Approach**:

**Option 1: Statistical Features**
- Perplexity analysis (AI text is typically lower perplexity)
- Burstiness (human text has more variance)
- N-gram frequency analysis
- Vocabulary diversity
- Sentence structure patterns

**Option 2: ML-Based Detection**
- Use pre-trained AI detectors:
  - GPTZero API
  - OpenAI AI Text Classifier
  - Local model: RoBERTa fine-tuned on AI text
- Ensemble approach (combine multiple detectors)

**Classification**:
- **Human-written**: >80% human score
- **AI-generated**: >80% AI score
- **Hybrid**: Mixed scores, likely AI-assisted

**Output**:
```
AI Detection Report:
- Document classification: Hybrid (AI-assisted)
- Overall AI probability: 65%

Section-by-Section Analysis:
┌────────────────────────┬──────────────┬────────────┐
│ Section                │ AI Prob.     │ Class      │
├────────────────────────┼──────────────┼────────────┤
│ Introduction           │ 45%          │ Human      │
│ Chapter 1              │ 78%          │ Hybrid     │
│ Chapter 2              │ 92%          │ AI         │
│ Conclusion             │ 38%          │ Human      │
└────────────────────────┴──────────────┴────────────┘

Indicators:
- Low perplexity in Chapter 2 (AI-like)
- Consistent sentence structure in Chapter 2
- Higher vocabulary diversity in Introduction (human-like)

Recommendation: Chapter 2 appears heavily AI-generated.
Consider rewriting for authenticity.
```

#### Feature 3.3: Document Sanitization
**Description**: Rewrite sections to reduce plagiarism and AI detection

**Capabilities**:
- Identify problematic sections
- Rewrite to:
  - Reduce similarity to sources
  - Add human-like variations
  - Maintain meaning and accuracy
- Add missing citations
- Preserve factual content

**Sanitization Process**:
1. **Identify issues**:
   - High similarity sections (plagiarism)
   - High AI probability sections
2. **Rewrite**:
   - Use LLM with specific instructions:
     - "Rewrite to increase originality"
     - "Add sentence structure variation"
     - "Use more domain-specific vocabulary"
   - Add citations where needed
3. **Verify**:
   - Re-run plagiarism detection
   - Re-run AI detection
   - Ensure improvement

**UI**:
- Show before/after comparison
- User can accept/reject rewrites
- Iterate until acceptable scores

---

## Question 4: Data Freshness & Auto-Update

### Original Request (French)
> "Ayant un document (input doc) est-ce qu'on peut actualiser les chiffres par des chiffres plus récents en se servant d'internet? (google ou bien un site spécifique que l'utilisateur donne ou aide à choisir ou plusieurs). Par exemple actualiser les chiffres de loi de finance de 2025 en chiffres de 2026."

### Translation
"Having a document (input doc), can we update the figures with more recent figures using the internet? (Google or a specific site that the user provides or helps choose or several). For example, update the 2025 finance law figures with 2026 figures."

### Task Types

1. **Figure Extraction**
   - Identify numbers, statistics, dates in document
   - Parse tables and charts
   - Extract context (what each figure represents)

2. **Web Search for Updates**
   - Search for recent data
   - From general sources (Google)
   - From specific portals (government sites)

3. **Figure Replacement**
   - Map old figures to new figures
   - Update in-place
   - Track changes
   - Update citations

### Features to Implement

#### Feature 4.1: Figure & Statistic Extraction
**Description**: Identify all figures, statistics, and dates in document

**Capabilities**:
- Extract:
  - Numbers (123, 45.6%, €1.2M)
  - Dates (2025, January 2024)
  - Ranges (2020-2025)
  - Percentages
  - Currency amounts
- Parse tables and extract all cells
- Identify what each figure represents (context)

**Technical Approach**:
- **Named Entity Recognition** (spaCy):
  - DATE entities
  - QUANTITY entities
  - PERCENT entities
  - MONEY entities
- **Regex patterns**:
  - Numbers with units (€, $, %, etc.)
  - Date formats
- **Table parsing**:
  - python-docx for DOCX tables
  - PyMuPDF for PDF tables
- **Context extraction**:
  - Extract sentence/paragraph containing figure
  - Extract table headers/row labels

**Output**:
```
Extracted Figures:
1. Page 12, Para 2: "€45.3 milliards"
   Context: "Le budget de l'État en 2025 s'élève à €45.3 milliards"
   Type: Currency
   Year: 2025

2. Page 15, Table 1, Row 3, Col 2: "23.4%"
   Context: "Taux de croissance - Secteur public"
   Type: Percentage
   Year: 2025

3. Page 18, Para 1: "12,456 fonctionnaires"
   Context: "Le ministère emploie 12,456 fonctionnaires"
   Type: Quantity
   Year: 2025
```

#### Feature 4.2: Intelligent Figure Update Search
**Description**: Search for updated versions of extracted figures

**Capabilities**:
- For each extracted figure:
  - Construct search query from context
  - Search general web (Google) or specific sites
  - Find most recent version of figure
  - Extract new value with source
- User can specify:
  - Specific websites to search
  - Date range (e.g., "2026 only")
  - Preferred sources

**Search Strategy**:

**Example 1: Budget Figure**
- Old: "Le budget de l'État en 2025 s'élève à €45.3 milliards"
- Context: "budget de l'État", "2025"
- Search query: "budget état tunisie 2026"
- Target sites: finances.gov.tn, data.gov.tn
- Extract: New figure from 2026 budget law
- New: "€47.8 milliards"

**Example 2: Growth Rate**
- Old: "Taux de croissance - Secteur public: 23.4% (2025)"
- Context: "taux de croissance", "secteur public"
- Search query: "taux croissance secteur public tunisie 2026"
- Target sites: ins.tn (statistics), finances.gov.tn
- Extract: New percentage from latest report
- New: "25.1%"

**Technical Approach**:
- **Web search**: WebSearch tool with constructed queries
- **Site-specific search**: WebFetch to specific portal pages
- **Figure extraction from results**:
  - Parse HTML tables
  - Extract from PDF reports
  - Use NER on fetched text
- **Validation**:
  - Check figure is from correct context
  - Verify source credibility
  - Confirm date is more recent

#### Feature 4.3: Figure Update Workflow
**Description**: End-to-end figure updating process

**Workflow**:

1. **Extract Figures**
   - User loads document
   - System extracts all figures with context
   - Display in table for review

2. **Configure Search**
   - User selects which figures to update
   - User specifies:
     - Target year (e.g., 2026)
     - Preferred sources (URLs)
     - Search scope (general web or specific sites)

3. **Search & Match**
   - System searches for each figure
   - Finds updated values
   - Presents matches for user review:
     ```
     Old: €45.3 milliards (2025)
     New: €47.8 milliards (2026)
     Source: finances.gov.tn/budget-2026.pdf
     Confidence: High
     [Accept] [Reject] [Search Again]
     ```

4. **Update Document**
   - Replace old figures with new figures
   - Update year references (2025 → 2026)
   - Add/update citation for new source
   - Track changes in document

5. **Review & Export**
   - Show before/after comparison
   - Generate update report
   - Export updated document

**UI Design**:
```
┌─────────────────────────────────────────────────────────┐
│  Figure Update Workflow                                  │
├─────────────────────────────────────────────────────────┤
│  Step 1: Extracted Figures (15 found)                   │
│                                                          │
│  [✓] €45.3 milliards (2025) - Budget de l'État         │
│      Page 12, Para 2                                    │
│                                                          │
│  [✓] 23.4% (2025) - Taux croissance secteur public     │
│      Page 15, Table 1                                   │
│                                                          │
│  [ ] 12,456 (2025) - Nombre de fonctionnaires          │
│      Page 18, Para 1                                    │
│                                                          │
│  Target Year: [2026▼]                                   │
│  Search Sources: [finances.gov.tn] [ins.tn] [Add]      │
│                                                          │
│  [Next: Search for Updates]                             │
└─────────────────────────────────────────────────────────┘
```

#### Feature 4.4: Source Priority & Credibility
**Description**: Rank sources by credibility and recency

**Source Types** (Priority order):
1. **Official Government Portals** (Highest credibility)
   - finances.gov.tn
   - ins.tn (statistics)
   - data.gov.tn
   - pm.gov.tn
   - arp.tn (parliament)

2. **International Organizations**
   - IMF reports
   - World Bank data
   - OECD statistics

3. **Professional Legal Databases**
   - dalloz.fr
   - lextenso.fr
   - cairn.info

4. **General Web** (Lowest priority)
   - News articles
   - Blog posts
   - Wikipedia

**Credibility Scoring**:
- Source domain (gov.tn = high)
- Publication date (more recent = better)
- Data provenance (primary source > secondary)
- Consistency (multiple sources agree)

---

## Additional Customer Context

### Customer Quote (LinkedIn Chat)
> "J'ai voulu savoir si sa capacité est telle qu'il peut détecter seul les éléments à actualiser à partir du net (journal officiel, conventions internationales, rapports FMI, Banque mondiale, OCDE, rapports nationaux) que sa capacité d'actualisation du contenu pourrait aller jusqu'à l'aspect substantiel en proposant que telle idée ou idées est à révérifier."

**Translation**:
"I wanted to know if it has the capacity to detect on its own the elements to update from the web (official journal, international conventions, IMF reports, World Bank, OECD, national reports) and if its content updating capacity could go as far as the substantive aspect by proposing that such idea or ideas need to be re-verified."

### Interpretation
Customer wants **proactive content updating**, including:
1. **Automatic detection** of outdated elements
2. **Multi-source checking** (official journals, international reports)
3. **Substantive updating** - not just figures, but ideas/concepts
4. **Verification suggestions** - flag ideas that need re-checking

### Additional Feature: Proactive Content Analysis

#### Feature 4.5: Outdated Content Detection
**Description**: Automatically detect document sections that may be outdated

**Capabilities**:
- Identify sections with dates (2020, 2022, etc.)
- Check if cited sources have newer versions
- Detect references to:
  - Laws that may have been amended
  - Statistics that are >2 years old
  - Conventions that may have been updated
  - Reports that have newer editions

**Detection Logic**:
1. **Date-based**:
   - Flag any figure >2 years old
   - Flag any law citation >5 years old

2. **Source-based**:
   - Check if cited report has newer edition
   - Example: "IMF Report 2020" → check for 2023, 2024, 2025 versions

3. **Concept-based**:
   - Identify emerging concepts not in document
   - Example: Document from 2016 doesn't mention:
     - Blue economy
     - Green economy
     - Circular economy
     - Sustainable finance
     - BEPS (Base Erosion and Profit Shifting)
     - Transfer pricing control
     - Automatic exchange of information

**Output**:
```
Outdated Content Analysis:
⚠️ 12 sections may be outdated

1. Page 15: Budget figures from 2023
   Recommendation: Update with 2025/2026 figures
   Source: finances.gov.tn

2. Page 23: Reference to "Loi de Finance 2020"
   Recommendation: Check if amendments made in 2021-2025
   Source: Check official journal

3. Page 45: Discussion of tax policy
   Missing: No mention of BEPS, transfer pricing control
   Recommendation: Add section on recent international developments
   Source: OECD BEPS reports, IMF publications

4. Page 67: Economic indicators from 2021
   Recommendation: Update with 2025 data
   Source: ins.tn, World Bank
```

#### Feature 4.6: Emerging Concept Detection
**Description**: Identify missing modern concepts that should be included

**Customer Example**:
> "En 2016 par exemple on ne parlait encore de l'économie bleu verte et circulaires et des finances durables... est-il capable de proposer des pistes dans ce sens. Également concernant les BEPS, le contrôle des prix de transfert et l'échange automatique d'informations."

**Translation**:
"In 2016 for example we didn't yet talk about blue green and circular economy and sustainable finance... is it capable of proposing directions in this sense. Also regarding BEPS, transfer pricing control and automatic exchange of information."

**Emerging Concepts by Domain**:

**Environmental Finance**:
- Blue economy (économie bleue)
- Green economy (économie verte)
- Circular economy (économie circulaire)
- Sustainable finance (finances durables)
- Green budget (budget vert)
- Climate finance

**International Tax**:
- BEPS (Base Erosion and Profit Shifting)
- Transfer pricing control (contrôle des prix de transfert)
- Automatic exchange of information (échange automatique d'informations)
- CRS (Common Reporting Standard)
- MLI (Multilateral Instrument)

**Digital Economy**:
- Digital services tax
- Platform economy
- Cryptocurrency regulation
- Digital transformation

**Capabilities**:
1. **Concept Gap Analysis**:
   - Compare document against knowledge base of modern concepts
   - Identify relevant missing concepts
   - Suggest where to add them

2. **Contextual Suggestions**:
   - Not just "add BEPS" but "In your discussion of international taxation (p. 45), consider adding section on BEPS framework"

3. **Source Recommendations**:
   - Suggest specific reports to reference:
     - OECD BEPS Action Plans
     - IMF Sustainable Finance reports
     - World Bank Green Economy publications

**Output**:
```
Emerging Concept Analysis:
📊 Document appears to be from 2016 era
🆕 5 modern concepts missing

1. Sustainable Finance (Finances Durables)
   Relevance: HIGH - directly related to your topic
   Suggested location: Chapter 3 (after discussion of traditional finance)
   Key sources:
   - IMF "Sustainable Finance Report 2024"
   - World Bank "Green Finance Framework"
   - EU Taxonomy Regulation

2. BEPS Framework
   Relevance: HIGH - modern international tax policy
   Suggested location: Chapter 5, Section 2 (international taxation)
   Key sources:
   - OECD BEPS Action Plans (15 actions)
   - OECD Transfer Pricing Guidelines 2022

3. Circular Economy
   Relevance: MEDIUM - emerging economic model
   Suggested location: Chapter 2 (economic models)
   Key sources:
   - European Commission Circular Economy Action Plan
   - OECD Circular Economy reports

Would you like to:
[Generate draft sections] [Show detailed sources] [Skip]
```

---

## Prioritized Source Portals

Customer provided extensive list of important portals:

### Tier 1: Official Tunisian Government
1. **https://www.finances.gov.tn/** - Ministry of Finance
2. **https://www.ins.tn/** - National Statistics Institute
3. **https://data.gov.tn/fr/** - Open Data Tunisia
4. **https://pm.gov.tn** - Prime Minister's Office
5. **https://arp.tn/ar_SY/loi/project/lp** - Parliament (laws in progress)
6. **http://www.gbo.tn/** - Government Budget Office

### Tier 2: Legal Databases
1. **https://shs.cairn.info/** - Cairn Social Sciences
2. **https://www.dalloz.fr/** - Dalloz Legal Database
3. **https://www.labase-lextenso.fr/** - Lextenso Database
4. **https://jibaya.tn/documentation/** - Tunisian Legal Docs

### Tier 3: Professional Tools
1. **https://app.dbprofiscal.com/** - Tax Professional Database (requires auth)

### Tier 4: International Organizations (mentioned)
- IMF (International Monetary Fund)
- World Bank
- OECD (Organisation for Economic Co-operation and Development)

---

## Module Organization

Based on the 4 question categories, organize into modules:

### Module 1: Document Enrichment Module
**Features**:
- Feature 1.1: Document Enrichment Engine
- Feature 1.2: Web Portal Data Integration
- Feature 1.3: Style-Preserving Text Generation
- Feature 1.4: Document Evaluation & Report Generation
- Feature 1.5: Visual Change Tracking

**GUI Tab**: "Document Enrichment"

### Module 2: Research Workflow Module
**Features**:
- Feature 2.1: Legal Database Integration
- Feature 2.2: Interactive Article Selection UI
- Feature 2.3: Thematic Synthesis with Proper Citations
- Feature 2.4: Research Workflow Orchestration

**GUI Tab**: "Research Workflow"

### Module 3: Quality Assurance Module
**Features**:
- Feature 3.1: Plagiarism Detection Engine
- Feature 3.2: AI-Generated Text Detection
- Feature 3.3: Document Sanitization

**GUI Tab**: "Quality Check"

### Module 4: Data Update Module
**Features**:
- Feature 4.1: Figure & Statistic Extraction
- Feature 4.2: Intelligent Figure Update Search
- Feature 4.3: Figure Update Workflow
- Feature 4.4: Source Priority & Credibility
- Feature 4.5: Outdated Content Detection
- Feature 4.6: Emerging Concept Detection

**GUI Tab**: "Data Update"

---

## Use Cases

### Use Case 1: Enrich Thesis with New Article
**Actor**: Law professor
**Goal**: Update 2016 thesis with 2024 article on sustainable finance
**Preconditions**: Thesis and article both in system

**Steps**:
1. Open thesis document
2. Go to "Document Enrichment" tab
3. Select "Add Secondary Source"
4. Choose the 2024 article
5. System analyzes thesis and article
6. System identifies 8 sections where article is relevant
7. System proposes additions (shown in track changes)
8. User reviews suggestions:
   - Accept Section 2 addition (sustainable finance)
   - Modify Section 5 addition (green budget)
   - Reject Section 8 (not relevant)
9. System updates document with track changes
10. User exports enriched thesis as DOCX

**Success Criteria**:
- Additions match author's style
- All additions properly cited
- Original structure preserved
- Track changes visible

### Use Case 2: Research Workflow - Green Budget
**Actor**: Law professor
**Goal**: Create synthesis on "green budget" from Cairn articles
**Preconditions**: None

**Steps**:
1. Go to "Research Workflow" tab
2. Click "New Research Workflow"
3. Enter research question: "Le budget vert en Tunisie"
4. Select database: "Cairn (droit)"
5. Click "Search"
6. System finds 42 articles
7. System displays results with abstracts
8. User selects 5 most relevant articles
9. Click "Import Selected"
10. System downloads and processes articles
11. Click "Generate Synthesis"
12. System creates thematic synthesis with footnotes
13. User reviews and exports

**Success Criteria**:
- Found relevant articles
- Synthesis focused on theme
- Proper footnote citations
- Academic writing quality

### Use Case 3: Update Budget Figures 2025→2026
**Actor**: Law professor
**Goal**: Update all 2025 budget figures to 2026 in document
**Preconditions**: Document with 2025 figures loaded

**Steps**:
1. Open document
2. Go to "Data Update" tab
3. Click "Extract Figures"
4. System finds 23 figures from 2025
5. User selects "Update all"
6. Set target year: 2026
7. Add search sources:
   - finances.gov.tn
   - ins.tn
   - data.gov.tn
8. Click "Search for Updates"
9. System searches each figure
10. System presents matches:
    - Budget: €45.3B → €47.8B (confidence: high)
    - Growth: 23.4% → 25.1% (confidence: medium)
    - etc.
11. User reviews and accepts most matches
12. For 3 figures, no match found → user manually searches
13. System updates document with track changes
14. System updates citations
15. User exports updated document

**Success Criteria**:
- All 2025 figures updated to 2026
- Sources cited
- Track changes visible
- High confidence in matches

### Use Case 4: Quality Check Before Submission
**Actor**: Law professor
**Goal**: Check thesis for plagiarism and AI detection before publication
**Preconditions**: Final thesis draft ready

**Steps**:
1. Open thesis
2. Go to "Quality Check" tab
3. Select "Run Full Quality Check"
4. System runs:
   - Plagiarism detection
   - AI detection
5. Results shown:
   - Plagiarism: 8% overall (2 sections flagged)
   - AI detection: Hybrid (65% AI probability in Chapter 2)
6. User clicks "View Details"
7. System highlights:
   - Chapter 2, Para 3: 92% similarity to Source Doc 2 (NOT CITED)
   - Chapter 2: 92% AI probability (consistent structure, low perplexity)
8. User clicks "Sanitize Document"
9. System rewrites problematic sections
10. Re-runs quality check:
    - Plagiarism: 3% (acceptable)
    - AI detection: 45% (human-like)
11. User reviews changes and accepts
12. Export clean version

**Success Criteria**:
- Plagiarism <5%
- All high-similarity sections cited
- AI detection <50% (human-like)
- Document maintains quality

### Use Case 5: Proactive Content Update Alert
**Actor**: Law professor
**Goal**: Get notified of outdated content in old thesis
**Preconditions**: 2016 thesis loaded

**Steps**:
1. Open 2016 thesis
2. System automatically analyzes for outdated content
3. Alert banner shown:
   "⚠️ This document may contain outdated content. Run analysis?"
4. User clicks "Analyze"
5. System generates Outdated Content Report:
   - 12 sections with old dates
   - 5 emerging concepts missing
   - 3 laws may have been amended
6. User reviews suggestions:
   - Accept: Add section on sustainable finance
   - Accept: Update 2014 budget figures
   - Accept: Add BEPS discussion
   - Reject: Blue economy (not relevant)
7. System generates draft sections for new concepts
8. User reviews and edits drafts
9. System integrates into document
10. Export updated thesis

**Success Criteria**:
- Document updated with modern concepts
- Old data refreshed
- Style consistent
- Properly cited

---

## Test Plan

### Test Suite 1: Document Enrichment

#### Test 1.1: Style Preservation
**Setup**: Load thesis with distinct academic style
**Action**: Enrich with casual-style article
**Expected**: Additions match thesis style, not article style
**Metrics**:
- Style similarity score >0.85
- Vocabulary overlap >80%
- Human evaluation: "Seamless integration"

#### Test 1.2: Citation Integrity
**Setup**: Load thesis with 50 references
**Action**: Enrich with 2 new articles
**Expected**:
- Original 50 references unchanged
- New references added (2)
- Total references: 52
- All references properly formatted

#### Test 1.3: Evaluation Report Accuracy
**Setup**: Load thesis with known weaknesses (missing chapter, weak argument in Section 3)
**Expected Report**:
- Identifies missing chapter
- Flags weak argument in Section 3
- Suggests improvements

### Test Suite 2: Research Workflow

#### Test 2.1: Database Search
**Setup**: None
**Action**: Search Cairn for "budget vert"
**Expected**:
- Finds >10 articles
- All titles contain "budget" or "vert" or related terms
- Results sorted by relevance

#### Test 2.2: Article Import
**Setup**: Search results loaded
**Action**: Select 5 articles, import
**Expected**:
- All 5 articles downloaded
- Full text extracted
- Added to vector database
- Success message shown

#### Test 2.3: Footnote Citation Format
**Setup**: 3 articles imported
**Action**: Generate synthesis
**Expected**:
- Footnotes in Chicago/Bluebook format
- Sequential numbering (1, 2, 3...)
- Correct use of "Ibid." for repeated citations
- No in-text citations (all in footnotes)

### Test Suite 3: Quality Assurance

#### Test 3.1: Plagiarism Detection - Exact Match
**Setup**:
- Source doc: "Les finances publiques durables sont essentielles."
- Synthesis doc: "Les finances publiques durables sont essentielles." (exact copy)
**Expected**:
- Flagged as plagiarism (100% similarity)
- Status: NOT CITED
- Recommendation: Add citation or rephrase

#### Test 3.2: AI Detection - Known AI Text
**Setup**: Load synthesis known to be 100% AI-generated (from ChatGPT)
**Expected**:
- Classification: AI-generated
- Confidence: >85%
- Sections highlighted

#### Test 3.3: Document Sanitization
**Setup**: Document with 3 plagiarized sections (>90% similarity)
**Action**: Run sanitization
**Expected**:
- All 3 sections rewritten
- New similarity <70%
- Meaning preserved
- Citations added

### Test Suite 4: Data Update

#### Test 4.1: Figure Extraction
**Setup**: Document with 20 figures, 5 tables, 10 dates
**Expected**:
- All 20 figures extracted
- All table cells extracted
- All 10 dates extracted
- Context captured for each

#### Test 4.2: Figure Update - Budget
**Setup**:
- Document: "Budget 2025: €45.3 milliards"
- Search source: finances.gov.tn with 2026 budget: €47.8 milliards
**Action**: Run figure update for 2026
**Expected**:
- Match found with high confidence
- Proposed update: €45.3B → €47.8B
- Source: finances.gov.tn
- User accepts → document updated

#### Test 4.3: Outdated Content Detection
**Setup**: Load 2016 document
**Expected**:
- Flags all dates >5 years old
- Identifies missing concepts (BEPS, sustainable finance, etc.)
- Suggests sections for updates
- Provides source recommendations

---

## Technical Requirements

### New Dependencies

```toml
[project.dependencies]
# Web scraping
"selenium>=4.15.0",
"beautifulsoup4>=4.12.0",
"playwright>=1.40.0",  # For dynamic sites

# NLP & Text Analysis
"spacy>=3.7.0",
"nltk>=3.8.0",

# Plagiarism & Text Similarity
"difflib",  # Built-in
"scikit-learn>=1.3.0",  # For similarity metrics

# AI Detection
"transformers>=4.35.0",  # For RoBERTa AI detector
"torch>=2.1.0",  # For model inference

# Table Extraction
"pandas>=2.1.0",
"openpyxl>=3.1.0",  # For Excel

# Citation Management
"bibtexparser>=1.4.0",
"pybtex>=0.24.0",

# Style Analysis
"textstat>=0.7.3",  # Readability metrics
"language-tool-python>=2.7.0",  # Grammar/style
```

### Infrastructure Needs

1. **Web Scraping Infrastructure**
   - Headless browser setup (Playwright)
   - Proxy support for rate limiting
   - Cookie/session management

2. **AI Models**
   - AI text detector (RoBERTa-based, ~500MB)
   - Style transfer model (optional)
   - Paraphrase generator

3. **External APIs** (Optional)
   - GPTZero API (AI detection)
   - Copyscape API (plagiarism)
   - Crossref API (citation metadata)

4. **Storage**
   - Cache for web search results
   - Downloaded articles storage
   - Version control for documents

---

## Priority Ranking

Based on customer emphasis and implementation complexity:

### Phase 1: Quick Wins (Weeks 1-2)
1. **Feature 4.1-4.3**: Figure Update Workflow
   - High value, moderate complexity
   - Clear use case (2025→2026 updates)

2. **Feature 1.4**: Document Evaluation Report
   - High value, moderate complexity
   - Uses existing RAG infrastructure

### Phase 2: Core Features (Weeks 3-5)
3. **Feature 2.1-2.4**: Research Workflow
   - Very high value
   - Complex but builds on synthesis engine

4. **Feature 1.1-1.3**: Document Enrichment
   - High value
   - Style preservation is challenging

### Phase 3: Quality Features (Weeks 6-7)
5. **Feature 3.1**: Plagiarism Detection
   - Medium-high value
   - Moderate complexity

6. **Feature 3.2**: AI Detection
   - Medium value
   - Requires new models

### Phase 4: Advanced Features (Weeks 8-10)
7. **Feature 4.5-4.6**: Proactive Content Analysis
   - High strategic value
   - Complex (emerging concept detection)

8. **Feature 3.3**: Document Sanitization
   - Medium value
   - Builds on 3.1 and 3.2

---

## Customer Engagement Plan

### Immediate Questions for Customer

1. **Priority Confirmation**:
   - "Which feature is most urgent for your work?"
   - Options: Figure update, Research workflow, Document enrichment

2. **Authentication Access**:
   - "Do you have login credentials for dbprofiscal.com and other paid databases?"
   - Needed for full database integration

3. **Citation Style Preference**:
   - "Which citation style do you prefer?"
   - Chicago, Bluebook (legal), APA, MLA

4. **Style Examples**:
   - "Can you provide 2-3 sample paragraphs in your preferred writing style?"
   - Needed for style transfer training

5. **Portal Priorities**:
   - "Which 3 government portals are most important?"
   - Focus initial integration efforts

### Iterative Feedback Loop

1. **Week 1**: Implement Feature 4.1 (Figure Extraction)
   - Show customer extracted figures from their thesis
   - Validate accuracy
   - Get feedback on UI

2. **Week 2**: Implement Feature 4.2-4.3 (Figure Update)
   - Demo with customer's real document
   - Validate search results
   - Refine confidence scoring

3. **Week 3**: Implement Feature 2.1 (Database Integration)
   - Test search with customer's themes
   - Validate relevance ranking
   - Adjust filters

4. **Continue iteratively** for each feature

---

## Summary

This analysis organizes customer feedback into:
- ✅ **4 major modules** (Enrichment, Research, Quality, Update)
- ✅ **16 distinct features** with technical specs
- ✅ **5 detailed use cases** from customer perspective
- ✅ **12 test suites** with success criteria
- ✅ **Implementation roadmap** (4 phases, 10 weeks)
- ✅ **Customer engagement plan** for validation

**Next Steps**:
1. Review priorities with customer
2. Confirm technical approach
3. Start with Phase 1 (Figure Update Workflow)
4. Iterate based on customer feedback

The customer has provided extremely rich, specific requirements that demonstrate deep domain knowledge and clear vision for the tool's evolution. This is an excellent foundation for a production-ready legal research assistant.
