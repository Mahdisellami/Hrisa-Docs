# Task Caching Architecture

## Overview

General caching system for expensive computational tasks at multiple abstraction levels: task, workflow, pipeline, and step.

**Design Principle**: Cache expensive computations, enable reuse when inputs haven't changed.

---

## Caching Levels

### 1. Task Level (Highest - User-Visible Operations)

**Definition**: Complete user-initiated operations that produce final outputs.

**Examples**:
- Document synthesis (PDFs → synthesized book)
- Theme discovery (document corpus → themes)
- Document processing (raw PDFs → embedded chunks)

**Cache Key**: Task name + input document IDs + configuration
**Cache Value**: Complete task results (output files, metadata, statistics)

**Use Cases**:
- Re-export synthesis to different format without regeneration
- Restore theme discovery results without re-clustering
- Skip re-processing unchanged documents

### 2. Workflow Level (Multi-Task Sequences)

**Definition**: Sequences of related tasks that build on each other.

**Examples**:
- Full pipeline: Process documents → Discover themes → Generate synthesis
- Iterative refinement: Generate draft → User edits themes → Regenerate

**Cache Key**: Workflow ID + all task results in sequence
**Cache Value**: Intermediate results between workflow steps

**Use Cases**:
- Resume interrupted workflows
- Skip completed workflow stages
- A/B test different workflow paths

### 3. Pipeline Level (Data Processing Chains)

**Definition**: Data transformation pipelines with multiple stages.

**Examples**:
- PDF extraction pipeline: Raw PDF → Text → Chunks → Embeddings
- Synthesis pipeline: Themes → Outline → Chapters → Formatted output

**Cache Key**: Pipeline stage + input data hash
**Cache Value**: Transformed data at each pipeline stage

**Use Cases**:
- Cache embeddings (expensive) while re-chunking (cheap)
- Cache chapter content while reformatting (styling changes)
- Reuse extraction when only embedding model changed

### 4. Step Level (Lowest - Atomic Operations)

**Definition**: Individual atomic operations within tasks.

**Examples**:
- Single LLM generation call
- Single embedding generation
- Single clustering operation

**Cache Key**: Operation type + input parameters + data hash
**Cache Value**: Operation-specific result

**Use Cases**:
- Cache expensive LLM calls for identical inputs
- Reuse embeddings for same text chunks
- Skip redundant computations

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Task Level                          │
│  TaskExecutionCache(task_name, inputs, config, results) │
│                                                          │
│  Examples:                                               │
│  - SynthesisTask: chapters, word count, citations       │
│  - ThemeDiscoveryTask: themes, clusters, labels         │
│  - ProcessingTask: chunk count, embedding stats         │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────┐
│              Workflow Level                              │
│  WorkflowCache(workflow_id, task_sequence, checkpoints) │
│                                                          │
│  Examples:                                               │
│  - Full synthesis workflow: [Process, Discover, Synth]  │
│  - Iterative refinement: [Draft, Edit, Regenerate]      │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────┐
│               Pipeline Level                             │
│  PipelineCache(stage_name, input_hash, output_data)     │
│                                                          │
│  Examples:                                               │
│  - Extraction: PDF hash → extracted text                │
│  - Chunking: text hash + params → chunks                │
│  - Embedding: chunks hash + model → vectors             │
│  - Synthesis: themes hash + config → chapters           │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────┐
│                 Step Level                               │
│  StepCache(operation, parameters, result)                │
│                                                          │
│  Examples:                                               │
│  - LLM call: prompt hash → generated text               │
│  - Embedding: text hash → vector                        │
│  - Clustering: vectors hash + k → cluster labels        │
└──────────────────────────────────────────────────────────┘
```

---

## Data Models (Conceptual - Storage Ignored)

### Task Cache

```python
@dataclass
class TaskCache:
    """Cache for complete task execution results."""

    # Identity
    task_name: str              # "synthesis", "theme_discovery", "processing"
    task_display_name: str      # User-friendly name

    # Input fingerprint
    input_document_ids: List[str]   # Which documents were used
    config_hash: str                 # Hash of configuration used

    # Results
    results: Dict[str, Any]          # Task-specific results
    output_files: List[str]          # Generated files
    metadata: Dict[str, Any]         # Statistics, counts, etc.

    # Timestamps
    created_at: datetime
    last_used_at: datetime

    def is_valid_for(self, document_ids: List[str], config: Dict) -> bool:
        """Check if cache is valid for given inputs."""
        return (
            set(self.input_document_ids) == set(document_ids) and
            self.config_hash == hash_config(config)
        )
```

### Workflow Cache

```python
@dataclass
class WorkflowCache:
    """Cache for multi-task workflow results."""

    # Identity
    workflow_id: str                # "full_synthesis", "iterative_refinement"
    workflow_name: str              # User-friendly name

    # Task sequence
    tasks: List[str]                # Ordered task names
    checkpoints: Dict[str, TaskCache]  # Results after each task

    # State
    current_task_index: int         # Where we are in workflow
    completed: bool

    # Timestamps
    started_at: datetime
    updated_at: datetime

    def get_last_checkpoint(self) -> Optional[TaskCache]:
        """Get most recent completed task cache."""
        if self.current_task_index > 0:
            task_name = self.tasks[self.current_task_index - 1]
            return self.checkpoints.get(task_name)
        return None

    def can_resume(self) -> bool:
        """Check if workflow can be resumed."""
        return not self.completed and self.current_task_index > 0
```

### Pipeline Cache

```python
@dataclass
class PipelineStageCache:
    """Cache for individual pipeline stage."""

    # Identity
    stage_name: str                 # "extraction", "chunking", "embedding"
    pipeline_name: str              # "document_processing", "synthesis"

    # Input fingerprint
    input_hash: str                 # Hash of input data
    parameters: Dict[str, Any]      # Stage-specific parameters

    # Output
    output_data: Any                # Stage result (type varies)
    output_hash: str                # Hash of output (for next stage)

    # Metadata
    created_at: datetime
    computation_time_seconds: float

    def is_valid_for(self, input_data: Any, params: Dict) -> bool:
        """Check if cache is valid for given inputs."""
        return (
            self.input_hash == hash_data(input_data) and
            self.parameters == params
        )
```

### Step Cache

```python
@dataclass
class StepCache:
    """Cache for atomic operations."""

    # Operation identity
    operation_type: str             # "llm_generate", "embed_text", "cluster"
    operation_params: Dict[str, Any]  # All parameters

    # Input fingerprint
    input_hash: str                 # Hash of input data

    # Output
    result: Any                     # Operation result

    # Metadata
    created_at: datetime
    computation_time_ms: float
    cache_hits: int                 # How many times reused

    def get(self) -> Any:
        """Get cached result and increment hit counter."""
        self.cache_hits += 1
        return self.result
```

---

## Cache Invalidation Strategy

### Task Level Invalidation

**Invalidate when**:
- Input documents added/removed/modified
- Configuration changed (that affects output content)
- User explicitly requests regeneration

**Keep when**:
- Output format changed (DOCX → PDF)
- Styling parameters changed
- Citation style changed

### Workflow Level Invalidation

**Invalidate when**:
- Any task in sequence invalidated
- Workflow definition changed

**Partial invalidation**:
- If task 2 of 4 is invalidated, keep tasks 1, 3, 4 if possible
- Resume from last valid checkpoint

### Pipeline Level Invalidation

**Invalidate when**:
- Input data changed
- Stage parameters changed

**Keep when**:
- Downstream stages can reuse if inputs haven't changed

### Step Level Invalidation

**Invalidate when**:
- Input parameters changed
- Model changed (for LLM/embedding operations)

**Time-based expiration**:
- LLM calls: expire after 7 days (models may improve)
- Embeddings: expire after 30 days
- Clustering: expire when new documents added

---

## Example: Synthesis Task Caching

### Current Implementation (Synthesis-Specific)

```python
@dataclass
class SynthesisCache:
    chapters: List[Dict[str, Any]]
    generated_at: datetime
    synthesis_level: str
    theme_ids: List[str]
    total_words: int
    total_citations: int
    config_used: Dict[str, Any]
```

### How It Fits Into General Architecture

**SynthesisCache is a Task-Level Cache**:

```python
# SynthesisCache maps to TaskCache like this:
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

### Synthesis Pipeline Stages (Could Be Cached Separately)

```
Stage 1: Theme Selection
Input: all_themes + user_selection
Output: selected_themes
Cache: PipelineStageCache("theme_selection", hash(all_themes), selected_themes)

Stage 2: Chapter Planning
Input: selected_themes + synthesis_level
Output: chapter_outline
Cache: PipelineStageCache("chapter_planning", hash(themes), chapter_outline)

Stage 3: Chapter Generation (per chapter)
Input: theme + outline + chunks + config
Output: chapter_content
Cache: PipelineStageCache(f"chapter_{i}", hash(inputs), chapter_content)

Stage 4: Citation Generation
Input: chapters + source_documents
Output: formatted_citations
Cache: PipelineStageCache("citations", hash(chapters), formatted_citations)

Stage 5: Output Formatting
Input: chapters + output_format + template
Output: formatted_file
Cache: PipelineStageCache(f"format_{fmt}", hash(chapters), formatted_file)
```

**Benefit**: Could regenerate just Stage 5 (formatting) without re-running LLM (Stages 1-4).

---

## Example: Theme Discovery Task Caching

**Current**: Theme discovery runs every time, even if documents unchanged.

**With Task-Level Caching**:

```python
TaskCache(
    task_name="theme_discovery",
    task_display_name="Theme Discovery",
    input_document_ids=[doc1.id, doc2.id, ...],
    config_hash=hash({
        "n_themes": n_themes,
        "clustering_method": "kmeans",
        "min_cluster_size": 10
    }),
    results={
        "themes": discovered_themes,
        "clusters": cluster_assignments,
        "theme_labels": generated_labels,
        "silhouette_score": quality_metric
    },
    output_files=[],
    metadata={"num_themes": len(themes), "num_chunks": total_chunks},
    created_at=datetime.now(),
    last_used_at=datetime.now()
)
```

**Use Cases**:
1. User closes app → reopens → themes still there (cached)
2. User tries different n_themes → regenerate (config changed)
3. User adds new document → regenerate (inputs changed)

---

## Example: Document Processing Pipeline Caching

**Pipeline Stages**:

```
PDF → Text → Chunks → Embeddings → Vector DB

Stage 1: Text Extraction
Cache: PipelineStageCache("extract_text", hash(pdf_file), extracted_text)

Stage 2: Chunking
Cache: PipelineStageCache("chunk_text", hash(text + chunk_params), chunks)

Stage 3: Embedding
Cache: PipelineStageCache("embed_chunks", hash(chunks + model_name), embeddings)

Stage 4: Vector DB Insert
Cache: Not cached (side effect)
```

**Benefit**: If user changes chunk_size, only re-run Stage 2-4, reuse Stage 1 (extraction).

---

## Implementation Strategy (High-Level)

### Phase 1: Task-Level Caching (Current)
✅ **Status**: Partially complete (SynthesisCache exists)

**Next**:
1. Generalize SynthesisCache to TaskCache
2. Add TaskCache to TaskExecutionRecord
3. Implement cache validation logic
4. Add UI to show "cached" status and reuse options

### Phase 2: Pipeline-Level Caching
**Goal**: Cache intermediate pipeline stages

**Next**:
1. Identify expensive pipeline stages in synthesis, theme discovery, processing
2. Add PipelineStageCache to data models
3. Implement stage caching in workers
4. Add cache hit/miss logging

### Phase 3: Step-Level Caching
**Goal**: Cache individual expensive operations

**Next**:
1. Wrap LLM calls with step cache
2. Wrap embedding generation with step cache
3. Add cache statistics (hit rate, time saved)
4. Implement cache eviction policy

### Phase 4: Workflow-Level Caching
**Goal**: Support resumable multi-task workflows

**Next**:
1. Define common workflows
2. Add workflow state tracking
3. Implement checkpoint/resume logic
4. Add UI for "Resume workflow from last checkpoint"

---

## Benefits by Level

| Level | Primary Benefit | Example |
|-------|----------------|---------|
| **Task** | Avoid complete re-execution | Export synthesis to PDF without LLM |
| **Workflow** | Resume interrupted work | Continue after app crash |
| **Pipeline** | Reuse expensive stages | Keep embeddings, redo formatting |
| **Step** | Eliminate redundant operations | Cache identical LLM prompts |

---

## Cache Storage (TO BE DESIGNED)

**Note**: Storage implementation postponed per user request.

**Options to Consider Later**:
1. In-memory cache (fast, volatile)
2. SQLite database (persistent, queryable)
3. File-based cache (simple, portable)
4. Hybrid (hot cache in memory, cold cache on disk)

**Key Requirements**:
- Fast lookups by cache key
- Efficient invalidation
- Size management (LRU eviction)
- Persistence across sessions

---

## Summary

This architecture provides:

1. ✅ **Task-level caching**: Avoid re-running complete tasks (synthesis, themes, etc.)
2. ✅ **Pipeline-level caching**: Reuse expensive intermediate results
3. ✅ **Step-level caching**: Cache individual operations (LLM calls, embeddings)
4. ✅ **Workflow-level caching**: Support resumable multi-task workflows

**Current Status**:
- SynthesisCache exists (task-level, synthesis-specific)
- Can be generalized to TaskCache for all tasks

**Next Steps** (When Ready):
1. Generalize to TaskCache model
2. Implement pipeline caching for synthesis stages
3. Add step caching for LLM calls
4. Design storage layer
