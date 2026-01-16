# Synthesis Caching System

## Overview

The caching system stores generated synthesis results to avoid expensive LLM regeneration when only formatting changes are needed.

**Note**: This document describes the **synthesis-specific** implementation of task-level caching. For the general caching architecture that applies to all tasks (synthesis, theme discovery, document processing, etc.) at multiple levels (task/workflow/pipeline/step), see **[TASK_CACHING_ARCHITECTURE.md](TASK_CACHING_ARCHITECTURE.md)**.

**SynthesisCache** is a specialized implementation of **TaskCache** for synthesis operations.

---

## Architecture

### Data Model (✅ Complete)

#### `SynthesisCache` Class
Located in: `src/docprocessor/models/project.py`

```python
@dataclass
class SynthesisCache:
    chapters: List[Dict[str, Any]]     # Generated chapter content
    generated_at: datetime              # When generated
    synthesis_level: str                # short/normal/comprehensive
    theme_ids: List[str]                # Which themes were used
    total_words: int                    # Total word count
    total_citations: int                # Total citations
    config_used: Dict[str, Any]         # Synthesis configuration
```

**Storage**: Saved in project JSON file under `synthesis_cache` field

---

## Use Cases

### 1. Export to Different Formats (Primary Use Case)
**Scenario**: Generate once, export multiple times

```
1. User runs synthesis → Generates chapters (10 minutes)
2. Chapters cached in project
3. User exports to DOCX → Uses cached chapters (instant)
4. User exports to PDF → Uses cached chapters (instant)
5. User changes PDF template → Uses cached chapters (instant)
```

**Benefits**:
- No LLM regeneration needed
- Instant format conversion
- Try different styling without waiting

### 2. Configuration Changes
**Scenario**: Change non-content settings

```
1. User generates synthesis with APA citations
2. User wants to try MLA citations → Regenerate needed
3. User changes PDF template only → Use cache
4. User changes font/styling → Use cache
```

### 3. Incremental Updates
**Scenario**: Add more documents later

```
1. User processes 5 documents → Generates synthesis
2. User adds 3 more documents
3. Cache invalidated (new content)
4. Regenerate synthesis with all 8 documents
```

---

## Cache Invalidation

Cache should be invalidated when:

❌ **Content Changes** (Regeneration Required):
- Documents added/removed
- Themes changed (merged, renamed, deleted)
- Synthesis level changed (short → normal)
- Different themes selected

✅ **Format Changes** (Use Cache):
- Output format changed (MD → DOCX → PDF)
- PDF template changed
- Citation style changed (APA → MLA)
- Font/styling changed

---

## Implementation Status

### ✅ Phase 1: Data Model (Complete)
- [x] `SynthesisCache` dataclass created
- [x] Added to `Project` model
- [x] Serialization/deserialization implemented
- [x] Project JSON includes `synthesis_cache` field

### 🚧 Phase 2: Worker Integration (TODO)

**File**: `src/docprocessor/gui/workers.py`

```python
class SynthesisWorker:
    def run(self):
        # After generating chapters
        chapters = synthesis_engine.generate_book(...)

        # Create cache
        cache = SynthesisCache(
            chapters=chapters,
            generated_at=datetime.now(),
            synthesis_level=self.synthesis_level,
            theme_ids=[t['id'] for t in themes],
            total_words=sum(c.word_count for c in chapters),
            total_citations=sum(c.citation_count for c in chapters),
            config_used={
                'synthesis_level': self.synthesis_level,
                'chunks_per_chapter': self.chunks_per_chapter,
                # ...
            }
        )

        # Emit cache with chapters
        self.finished.emit(chapters, cache)
```

### 🚧 Phase 3: UI Integration (TODO)

**File**: `src/docprocessor/gui/main_window.py`

#### A. Check for Cached Synthesis

```python
def generate_book(self):
    # Check if cached synthesis exists
    if self.current_project.synthesis_cache:
        cache = self.current_project.synthesis_cache

        # Check if cache is still valid
        if self._is_cache_valid(cache):
            # Offer to use cache
            reply = QMessageBox.question(
                self,
                "Use Cached Synthesis?",
                f"Found existing synthesis from {cache.generated_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"Level: {cache.synthesis_level}\n"
                f"Chapters: {len(cache.chapters)}\n"
                f"Total words: {cache.total_words}\n\n"
                "Use cached synthesis or regenerate?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Use cached chapters
                self._export_from_cache(cache)
                return

    # Proceed with normal synthesis
    self._start_synthesis_worker()
```

#### B. Cache Validation

```python
def _is_cache_valid(self, cache: SynthesisCache) -> bool:
    """Check if cached synthesis is still valid."""
    # Get current theme IDs
    current_theme_ids = [t.get('id') for t in self.themes]

    # Check if themes changed
    if set(cache.theme_ids) != set(current_theme_ids):
        return False

    # Check if synthesis level changed
    config = self.synthesis_config.get_config()
    if cache.synthesis_level != config['synthesis_level']:
        return False

    # Cache is valid
    return True
```

#### C. Export from Cache

```python
def _export_from_cache(self, cache: SynthesisCache):
    """Export cached chapters to selected format without regeneration."""
    config = self.synthesis_config.get_config()

    # Create output formatter
    output_formatter = OutputFormatter()

    # Export to selected format(s)
    if config['output_format'] in ['markdown', 'both', 'all']:
        output_formatter.export_markdown(cache.chapters, ...)

    if config['output_format'] in ['docx', 'both', 'all']:
        output_formatter.export_docx(cache.chapters, ...)

    if config['output_format'] in ['pdf', 'all']:
        output_formatter.export_pdf(cache.chapters, ...)

    # Refresh output files list
    self.files_widget.refresh_output_files()

    # Show success message
    QMessageBox.information(
        self,
        "Export Complete",
        f"Exported cached synthesis to {config['output_format']}\n"
        "No regeneration needed!"
    )
```

#### D. Save Cache After Synthesis

```python
def on_synthesis_finished(self, chapters, cache):
    """Handle synthesis completion."""
    # ... existing code ...

    # Save cache to project
    if self.current_project:
        self.current_project.synthesis_cache = cache
        self.project_manager.save_project(self.current_project)

    # ... rest of existing code ...
```

### 🚧 Phase 4: UI Indicators (TODO)

**File**: `src/docprocessor/gui/widgets/synthesis_config.py`

Add visual indicators:

```python
def update_cache_status(self, cache: Optional[SynthesisCache]):
    """Show cache status in UI."""
    if cache:
        self.cache_status_label.setText(
            f"✅ Cached synthesis available ({cache.total_words} words, "
            f"{cache.generated_at.strftime('%Y-%m-%d %H:%M')})"
        )
        self.cache_status_label.setStyleSheet("color: green;")

        # Add "Export from Cache" button
        self.export_cached_btn.setVisible(True)
    else:
        self.cache_status_label.setText("No cached synthesis")
        self.cache_status_label.setStyleSheet("color: gray;")
        self.export_cached_btn.setVisible(False)
```

---

## Benefits

### Time Savings
- **Initial synthesis**: 10-15 minutes (LLM generation)
- **Export from cache**: < 1 second
- **Multiple formats**: Export to 3 formats instantly

### Resource Efficiency
- No repeated LLM calls
- No repeated embedding lookups
- Reduced CPU/GPU usage

### User Experience
- Try different formats quickly
- Experiment with styling
- Immediate results

---

## Testing Checklist

### Unit Tests
- [ ] `SynthesisCache` serialization/deserialization
- [ ] Cache validation logic
- [ ] Cache invalidation conditions

### Integration Tests
- [ ] Generate synthesis → Save cache
- [ ] Load project → Restore cache
- [ ] Export from cache → Correct output
- [ ] Invalidate cache on content change

### Manual Tests
1. Generate synthesis for project A
2. Export to DOCX (should use LLM)
3. Export to PDF (should use cache - instant)
4. Close and reopen project
5. Export to Markdown (should use cache - instant)
6. Add new document
7. Export again (should regenerate - cache invalid)

---

## Future Enhancements

### Cache Management
- Show cache age in UI
- Manual cache invalidation button
- Cache statistics (hit rate, storage size)

### Multiple Caches
- Store multiple synthesis versions
- Compare different synthesis levels
- A/B test different configurations

### Partial Regeneration
- Regenerate only specific chapters
- Update citations without full regeneration
- Incremental synthesis

---

## Summary

The caching system is designed to:
1. ✅ Store expensive LLM-generated content
2. ✅ Enable instant format conversion
3. ✅ Validate cache before use
4. ✅ Persist across sessions

**Next Steps**: Implement UI integration (Phase 2-4)

---

## Relationship to General Task Caching Architecture

This synthesis cache is one instance of the broader **Task-Level Caching** pattern. See **[TASK_CACHING_ARCHITECTURE.md](TASK_CACHING_ARCHITECTURE.md)** for:

### How SynthesisCache Fits Into General Architecture

```python
# SynthesisCache (specific) maps to TaskCache (general):

TaskCache(
    task_name="synthesis",
    task_display_name="Document Synthesis",
    input_document_ids=[...],
    config_hash=hash(config_used),
    results={
        "chapters": chapters,
        "synthesis_level": synthesis_level,
        "theme_ids": theme_ids,
        "total_words": total_words,
        "total_citations": total_citations,
    },
    output_files=[markdown_path, docx_path, pdf_path],
    metadata={"word_count": total_words, "citation_count": total_citations},
    created_at=generated_at,
    last_used_at=datetime.now()
)
```

### Additional Caching Opportunities

The general architecture identifies **pipeline-level** caching opportunities within synthesis:

1. **Theme Selection** (cache selected themes)
2. **Chapter Planning** (cache chapter outline)
3. **Chapter Generation** (cache individual chapter content - expensive LLM)
4. **Citation Generation** (cache formatted citations)
5. **Output Formatting** (cache formatted files per format)

**Benefit**: Could regenerate only formatting (stage 5) without re-running LLM (stages 1-4), enabling instant style changes even within same format.

### Other Tasks That Need Caching

Following the same pattern, these tasks should also implement task-level caching:

1. **Theme Discovery Task** (`ThemeDiscoveryCache`)
   - Cache: discovered themes, cluster assignments, quality metrics
   - Reuse when: documents unchanged, clustering parameters unchanged
   - Benefit: Instant theme restoration on app restart

2. **Document Processing Task** (`ProcessingCache`)
   - Cache: extracted text, chunks, embeddings
   - Reuse when: PDF unchanged, chunking parameters unchanged
   - Benefit: Skip expensive embedding generation on re-processing

3. **Query/RAG Task** (future)
   - Cache: retrieved chunks, generated responses
   - Reuse when: same query, same document set
   - Benefit: Instant answers to repeated questions

See **[TASK_CACHING_ARCHITECTURE.md](TASK_CACHING_ARCHITECTURE.md)** for complete architecture details.
