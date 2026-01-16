# Search Handlers

This directory contains pluggable search handlers that implement different search strategies for the Search & Import feature.

## Overview

The search handler architecture follows a strategy pattern, allowing different search implementations to coexist and be selected dynamically based on the source domain and availability.

## Architecture

```
search_handlers/
├── base_handler.py        # Abstract base class + interface
├── google_handler.py      # Google Custom Search API (fallback)
├── ckan_handler.py        # CKAN API for data.gov.tn
└── __init__.py            # Handler registry
```

## Available Handlers

### GoogleSearchHandler
- **Domains**: `*` (any domain)
- **Reliability**: High
- **Requirements**: Google Custom Search API key + Search Engine ID
- **Use case**: Fallback for all sources; only handler for sites without native APIs

### CKANSearchHandler
- **Domains**: `data.gov.tn`, `catalog.data.gov.tn`
- **Reliability**: Medium
- **Requirements**: None (public API)
- **Use case**: Native search for Tunisian open data portal

## Creating a New Handler

### Step 1: Implement SearchHandler Interface

Create a new file in `search_handlers/` (e.g., `my_handler.py`):

```python
from typing import List, Optional
from ....models.project import SearchResult
from ....utils.logger import get_logger
from .base_handler import HandlerCapability, SearchHandler

logger = get_logger(__name__)


class MyCustomHandler(SearchHandler):
    """Handler for my-site.com."""

    @property
    def capability(self) -> HandlerCapability:
        return HandlerCapability(
            name="my-custom-handler",
            domains=["my-site.com", "www.my-site.com"],
            requires_api_key=False,
            search_types=["api"],  # or ["form"], ["scraping"]
            reliability="medium",
        )

    def can_handle(self, source_domain: Optional[str] = None) -> bool:
        if not source_domain:
            return False
        return any(domain in source_domain for domain in self.capability.domains)

    def search(
        self,
        query: str,
        config: dict,
        source_filter: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        # Implement your search logic here
        results = []
        # ... fetch and parse results ...
        return results

    def validate_config(self, config: dict) -> tuple[bool, Optional[str]]:
        # Validate any required configuration
        return True, None

    def is_available(self) -> bool:
        # Check if dependencies are installed
        return True
```

### Step 2: Register Handler

Add your handler to `__init__.py`:

```python
from .my_handler import MyCustomHandler

REGISTERED_HANDLERS: List[SearchHandler] = [
    MyCustomHandler(),      # Add your handler first (before Google)
    CKANSearchHandler(),
    GoogleSearchHandler(),  # Keep Google last as fallback
]
```

### Step 3: Write Tests

Create `tests/core/tasks/search_handlers/test_my_handler.py`:

```python
def test_my_handler_basic_search():
    handler = MyCustomHandler()
    config = {"max_results_per_query": 5}

    results = handler.search("test query", config)
    assert len(results) > 0
    assert all(r.source_name == "my-site.com" for r in results)

def test_my_handler_domain_matching():
    handler = MyCustomHandler()
    assert handler.can_handle("my-site.com")
    assert not handler.can_handle("other-site.com")
```

## SearchResult Format

All handlers must return `List[SearchResult]` with this structure:

```python
SearchResult(
    title="Document Title",
    url="https://example.com/doc.pdf",
    snippet="Preview text...",
    source_name="example.com",
    file_type="pdf",  # "pdf", "html", "docx", "csv", etc.
    relevance_score=0.0,  # 0.0-1.0 if available
    metadata={
        "handler_used": "my-handler-name",
        # ... other metadata ...
    },
    search_query="original query",
)
```

## Search Strategies

Users can select search strategy via configuration:

### "google" (Safe Default)
Force Google for all searches:
```python
config.set("search_strategy", "google")
```

### "native" (Testing Only)
Use only native handlers, fail if unavailable:
```python
config.set("search_strategy", "native")
config.set("sources", ["data.gov.tn"])
```

### "auto" (Smart Fallback - Recommended)
Try native first, fall back to Google on error:
```python
config.set("search_strategy", "auto")  # Default
config.set("sources", ["data.gov.tn", "finances.gov.tn"])
# Will use CKAN for data.gov.tn, Google for finances.gov.tn
```

## Best Practices

### 1. Error Handling
Always raise exceptions on failure - the dispatcher will handle fallback:
```python
def search(self, query, config, source_filter):
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return self._parse_results(response.json())
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise  # Let dispatcher handle fallback
```

### 2. Timeouts
Always use timeouts for network requests:
```python
response = requests.get(url, timeout=10)
```

### 3. Logging
Log important events for debugging:
```python
logger.info(f"Searching {self.capability.name}: {query}")
logger.debug(f"API response: {response.status_code}")
logger.error(f"Search failed: {error}")
```

### 4. Metadata
Include handler name in metadata for debugging:
```python
metadata = {
    "handler_used": self.capability.name,
    # ... other metadata ...
}
```

### 5. Result Limits
Respect `max_results_per_query` from config:
```python
max_results = config.get("max_results_per_query", 10)
return results[:max_results]
```

## Handler Selection Logic

When a search is performed, the dispatcher:

1. Gets strategy from config (`google` | `native` | `auto`)
2. If `google`: Use GoogleSearchHandler
3. If `native` or `auto`:
   - For each source domain, call `get_handler_for_source(domain)`
   - Tries handlers in registry order
   - Returns first handler where `can_handle(domain)` and `is_available()` are True
   - Falls back to Google if no native handler available (auto mode only)

## Testing Your Handler

### Unit Tests
```bash
pytest tests/core/tasks/search_handlers/test_my_handler.py
```

### Integration Tests
```bash
pytest tests/core/tasks/test_search_import_task_handlers.py
```

### Manual Testing
```python
from docprocessor.core.tasks.search_import_task import SearchImportTask
from docprocessor.core.task_base import TaskConfig

task = SearchImportTask()
config = TaskConfig()
config.set("search_strategy", "auto")
config.set("sources", ["my-site.com"])
config.set("max_results_per_query", 5)

result = task.execute(["test query"], config)
print(f"Found {len(result.output_data['results'])} results")
```

## Troubleshooting

### Handler Not Being Used
- Check `can_handle()` logic
- Verify handler is registered in `__init__.py` before GoogleSearchHandler
- Check `is_available()` returns True

### Fallback to Google Always Happening
- Enable debug logging: `logger.setLevel(logging.DEBUG)`
- Check handler exceptions in logs
- Verify API/network connectivity

### Duplicate Results
- Results are deduplicated by URL automatically
- If seeing duplicates, check URL normalization

## Future Enhancements

Potential improvements for the handler system:

- Parallel searching across multiple sources
- Result ranking/scoring normalization
- Handler metrics (success rate, latency)
- Dynamic handler discovery
- Per-handler configuration UI
- Result caching
- Rate limiting per handler
