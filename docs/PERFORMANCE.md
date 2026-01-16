# Performance Guide

This document describes the performance characteristics of Hrisa Docs, how to benchmark your system, and tips for optimization.

## Table of Contents

- [Quick Performance Summary](#quick-performance-summary)
- [Benchmarking Your System](#benchmarking-your-system)
- [Detailed Performance Metrics](#detailed-performance-metrics)
- [System Requirements](#system-requirements)
- [Performance Optimization](#performance-optimization)
- [Bottleneck Analysis](#bottleneck-analysis)
- [Hardware Recommendations](#hardware-recommendations)

## Quick Performance Summary

**Typical Performance on Modern Hardware** (M1 MacBook Pro, 16GB RAM):

| Operation | Speed | Notes |
|-----------|-------|-------|
| PDF Text Extraction | ~5-10 pages/sec | Varies by PDF complexity |
| Text Chunking | ~25,700 chunks/sec | Very fast, CPU-bound |
| Embedding Generation | ~146 chunks/sec | Most time-intensive operation |
| Vector Storage | ~2,044 chunks/sec | Excellent, disk I/O bound |
| Vector Search | < 1ms | Blazing fast |
| Theme Discovery | ~30-60 sec | For 100 documents |
| Chapter Synthesis | ~1-2 min/chapter | Depends on Ollama model |

**Expected Processing Times:**

- **Small corpus** (10 PDFs, ~500 pages): 5-10 minutes
- **Medium corpus** (50 PDFs, ~2,500 pages): 30-45 minutes
- **Large corpus** (100 PDFs, ~5,000 pages): 60-90 minutes

## Benchmarking Your System

### Run Performance Profile

Use the included profiling script to benchmark your system:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run profiler
python scripts/profile_performance.py
```

### Sample Output

```
================================================================================
Document Processor Performance Profiling
================================================================================

Creating sample document...
Document created: 161400 characters

--------------------------------------------------------------------------------
1. TEXT CHUNKING
--------------------------------------------------------------------------------
✓ Chunked document in 0.006s
  Created 386 chunks
  Avg chunk size: 418 chars

  Throughput: ~64,333 chunks/sec

--------------------------------------------------------------------------------
2. EMBEDDING GENERATION
--------------------------------------------------------------------------------
Model: sentence-transformers/all-MiniLM-L6-v2
Dimension: 384
✓ Generated 50 embeddings in 0.342s
  Throughput: 146.2 chunks/sec
  Per-chunk: 6.8ms

--------------------------------------------------------------------------------
3. VECTOR STORE OPERATIONS
--------------------------------------------------------------------------------
✓ Added 50 chunks in 0.024s
  Throughput: 2,083.3 chunks/sec

✓ Searched vector store in 0.001s
  Found 10 results

================================================================================
PROFILING COMPLETE
================================================================================
```

### Understanding Results

**Chunking Performance:**
- Should be > 10,000 chunks/sec
- If slower, check CPU usage and Python version
- This is rarely a bottleneck

**Embedding Performance:**
- **Good**: > 100 chunks/sec
- **Acceptable**: 50-100 chunks/sec
- **Slow**: < 50 chunks/sec
- Most time-intensive operation - see optimization tips below

**Vector Store Performance:**
- Storage: > 1,000 chunks/sec is excellent
- Search: < 10ms is excellent
- If slow, check disk I/O and available RAM

## Detailed Performance Metrics

### Component Breakdown

#### 1. PDF Text Extraction (PyMuPDF)

**Performance:**
- Simple PDFs: 10-15 pages/sec
- Complex PDFs (tables, images): 3-5 pages/sec
- Scanned PDFs (no OCR): ~20 pages/sec (metadata only)

**Variables:**
- PDF size and complexity
- Number of embedded images
- Text vs scanned content
- File compression

#### 2. Text Chunking

**Performance:**
- Average: 25,000+ chunks/sec
- Chunk size: 500-1000 characters
- Overlap: 50-100 characters

**Variables:**
- Chunk size (larger = fewer chunks = faster)
- Overlap size (more overlap = more chunks)
- Text complexity (affects splitting logic)

#### 3. Embedding Generation

**Performance:**
- Model: all-MiniLM-L6-v2 (default)
- Speed: 100-200 chunks/sec (CPU)
- Batch size: 16-32 optimal
- Dimension: 384

**Variables:**
- CPU/GPU capabilities
- Batch size
- Model size
- Input text length

**Models Comparison:**

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| all-MiniLM-L6-v2 | 80MB | Fast | Good |
| all-mpnet-base-v2 | 420MB | Medium | Better |
| instructor-large | 1.3GB | Slow | Best |

#### 4. Vector Store (ChromaDB)

**Performance:**
- Add: 1,000-3,000 chunks/sec
- Search: < 5ms for 10 results
- Collection size: Scales to 1M+ chunks

**Variables:**
- Disk speed (SSD vs HDD)
- Available RAM
- Collection size
- Search result count

#### 5. Theme Discovery

**Performance:**
- Small corpus (10 docs): ~10 seconds
- Medium corpus (50 docs): ~30 seconds
- Large corpus (100 docs): ~60 seconds

**Variables:**
- Number of documents
- Clustering algorithm (K-means vs HDBSCAN)
- Number of themes to discover
- LLM speed for labeling

#### 6. Chapter Synthesis (Ollama)

**Performance:**
- Model: llama3.1:latest (default)
- Speed: ~30-50 tokens/sec
- Chapter: ~2-3 minutes (1000 tokens)

**Variables:**
- Ollama model size
- CPU/GPU capabilities
- Context window size
- Generation parameters

**Model Comparison:**

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.1:8b | 4.7GB | Fast | Good |
| llama3.1:70b | 39GB | Slow | Excellent |
| mistral:7b | 4.1GB | Very Fast | Good |

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores, 2.0 GHz
- **RAM**: 8GB
- **Storage**: 10GB free (5GB app + 5GB data)
- **OS**: macOS 12+, Ubuntu 22.04+, Windows 10+

**Expected Performance:**
- Small projects only (< 20 PDFs)
- Embedding: ~50 chunks/sec
- Processing: Slow but usable

### Recommended Requirements

- **CPU**: 8 cores, 2.5 GHz (Apple M1/M2 or Intel i7/i9)
- **RAM**: 16GB
- **Storage**: 50GB free SSD
- **OS**: macOS 14+, Ubuntu 22.04+, Windows 11+

**Expected Performance:**
- Medium to large projects (100+ PDFs)
- Embedding: ~150 chunks/sec
- Processing: Smooth and responsive

### Optimal Requirements

- **CPU**: 12+ cores, 3.0+ GHz (Apple M3 Pro/Max or AMD Ryzen 9)
- **RAM**: 32GB+
- **Storage**: 100GB+ free NVMe SSD
- **GPU**: CUDA-capable GPU (NVIDIA GTX 1060+) for acceleration

**Expected Performance:**
- Large projects (500+ PDFs)
- Embedding: ~300+ chunks/sec (with GPU)
- Processing: Very fast

## Performance Optimization

### 1. Embedding Generation (Biggest Bottleneck)

**Use GPU Acceleration:**

```bash
# Install CUDA-enabled PyTorch (if you have NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Hrisa Docs will automatically detect and use GPU
```

**Use Smaller Model:**

Edit `config/settings.py`:
```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, 80MB
# vs
EMBEDDING_MODEL = "all-mpnet-base-v2"  # Slower, 420MB, better quality
```

**Increase Batch Size:**

```python
# In processing settings
EMBEDDING_BATCH_SIZE = 32  # Default: 16, try 32 or 64
```

**Trade-off**: Higher batch size = more RAM usage but faster processing

### 2. Vector Store

**Use SSD Storage:**
- ChromaDB benefits greatly from fast disk I/O
- Place `~/.docprocessor/` on SSD if possible

**Increase RAM:**
- ChromaDB caches in memory
- More RAM = better search performance

### 3. Ollama Generation

**Use Faster Model:**

```bash
# Switch from llama3.1:70b to llama3.1:8b
ollama pull llama3.1:8b

# Or use even faster model
ollama pull mistral:7b
```

**Reduce Context Window:**

Edit synthesis settings to use smaller context:
```python
MAX_CONTEXT_CHUNKS = 10  # Default: 20
```

**Trade-off**: Less context = faster but potentially lower quality

### 4. PDF Processing

**Batch Processing:**
- Process PDFs in parallel using multiple workers
- Edit settings to increase worker count (future feature)

**Skip OCR:**
- For scanned PDFs, skip OCR if text quality is poor
- OCR is very slow and may not improve results

### 5. General Optimizations

**Close Background Apps:**
- Free up RAM and CPU for processing
- Especially important on minimum-spec systems

**Use Wired Connection:**
- If using remote Ollama server
- Faster than Wi-Fi

**Monitor Resources:**

```bash
# macOS
Activity Monitor

# Linux
htop

# Windows
Task Manager
```

Watch for:
- CPU usage (should be high during embedding)
- RAM usage (should stay under 80%)
- Disk I/O (important for ChromaDB)

## Bottleneck Analysis

### Identifying Bottlenecks

Run the profiler and look for:

1. **Slow Embedding (< 50 chunks/sec)**
   - CPU/GPU is bottleneck
   - Solution: Upgrade hardware or use smaller model

2. **Slow Vector Storage (< 500 chunks/sec)**
   - Disk I/O is bottleneck
   - Solution: Use SSD, close disk-intensive apps

3. **Slow Synthesis (> 5 min/chapter)**
   - LLM is bottleneck
   - Solution: Use faster Ollama model

4. **High Memory Usage (> 90%)**
   - RAM is bottleneck
   - Solution: Reduce batch size, process fewer documents at once

### Using Python Profiler

For detailed analysis:

```bash
# Profile specific operation
python -m cProfile -o profile.stats scripts/profile_performance.py

# Analyze results
python -m pstats profile.stats
# Then: sort cumulative, stats 20
```

## Hardware Recommendations

### Budget Setup ($800-1000)

- **Laptop**: MacBook Air M1 (8GB RAM)
- **Desktop**: Ryzen 5 5600 + 16GB RAM
- **Expected**: Good for small-medium projects

### Mid-Range Setup ($1500-2000)

- **Laptop**: MacBook Pro M2 (16GB RAM)
- **Desktop**: Ryzen 7 5800X + 32GB RAM + GTX 1660
- **Expected**: Excellent for medium-large projects

### High-End Setup ($3000+)

- **Laptop**: MacBook Pro M3 Max (32GB+ RAM)
- **Desktop**: Ryzen 9 7950X + 64GB RAM + RTX 4070
- **Expected**: Handles any project size effortlessly

### GPU Acceleration

**NVIDIA GPUs (CUDA Support):**
- GTX 1060 6GB: 2x faster embedding
- RTX 3060 12GB: 3-4x faster embedding
- RTX 4070: 5-6x faster embedding

**Apple Silicon (MPS):**
- M1/M2: Limited acceleration, ~20% faster
- M3 Pro/Max: Better acceleration, ~50% faster

**AMD GPUs:**
- Limited support via ROCm (Linux only)
- Better to use CPU on AMD systems

## Performance Tips Summary

### Do's ✓

- Use SSD for storage
- Close unnecessary apps during processing
- Process in batches (import → process → next batch)
- Monitor system resources
- Update to latest Ollama version
- Use appropriate model sizes for your hardware

### Don'ts ✗

- Don't max out RAM (leave 20% free)
- Don't process huge PDFs on minimum spec
- Don't use large models on slow hardware
- Don't run multiple heavy apps simultaneously
- Don't store ChromaDB on network drives
- Don't use very large context windows unnecessarily

## Future Performance Improvements

Planned optimizations:

1. **Multi-threaded PDF processing**
2. **Smarter caching strategies**
3. **Optional cloud GPU for embedding**
4. **Incremental processing (don't re-process unchanged docs)**
5. **Model quantization support**
6. **Batch API support for Ollama**

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common performance issues.
