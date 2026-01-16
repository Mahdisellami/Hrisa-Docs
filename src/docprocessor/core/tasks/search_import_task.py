"""Search & Import Task implementation.

Search Tunisian government/legal sources for documents and import them.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional

from ...models.project import SearchResult
from ...utils.logger import get_logger
from ..task_base import Task, TaskCategory, TaskConfig, TaskResult, TaskStatus

logger = get_logger(__name__)


class SearchImportTask(Task):
    """Task for searching and importing documents from research sources.

    Supports:
    - Google Custom Search API (primary method)
    - Site-specific search engines (future enhancement)
    - Multiple Tunisian government and legal sources
    """

    @property
    def name(self) -> str:
        return "search_import"

    @property
    def display_name(self) -> str:
        return "Search & Import"

    @property
    def description(self) -> str:
        return (
            "Search government and legal databases for documents, "
            "then import relevant results to your project."
        )

    @property
    def category(self) -> TaskCategory:
        return TaskCategory.ENRICHMENT

    @property
    def icon(self) -> str:
        return "🔍"

    # ========== Requirements ==========

    @property
    def input_types(self) -> List[str]:
        return ["search_query"]

    @property
    def output_types(self) -> List[str]:
        return ["search_results", "document"]

    @property
    def requires_internet(self) -> bool:
        return True

    @property
    def min_inputs(self) -> int:
        return 1  # At least one search query

    @property
    def max_inputs(self) -> Optional[int]:
        return 5  # Up to 5 queries at once

    # ========== Configuration ==========

    def get_default_config(self) -> TaskConfig:
        """Default search & import configuration."""
        config = TaskConfig()

        # Search parameters
        config.set("max_results_per_query", 10)  # Results per query
        config.set("search_strategy", "google")  # "google" | "native" | "auto"

        # Google Custom Search
        config.set("google_api_key", None)  # Required for Google search
        config.set("google_search_engine_id", None)  # Required for Google search

        # Source filtering
        config.set("sources", [])  # Empty = all sources, or list of domains
        config.set("file_types", ["pdf", "html", "docx"])  # Filter by file type

        # Import behavior
        config.set("auto_import", False)  # If True, skip result preview

        return config

    def validate_config(self, config: TaskConfig) -> tuple[bool, Optional[str]]:
        """Validate configuration parameters."""

        # Validate max_results
        max_results = config.get("max_results_per_query", 10)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 50:
            return False, f"max_results_per_query must be between 1 and 50, got {max_results}"

        # Validate search strategy
        strategy = config.get("search_strategy", "google")
        if strategy not in ["google", "native", "auto"]:
            return False, f"search_strategy must be 'google', 'native', or 'auto', got {strategy}"

        # Validate Google API credentials if using Google
        if strategy in ["google", "auto"]:
            api_key = config.get("google_api_key")
            search_engine_id = config.get("google_search_engine_id")

            if not api_key:
                return (
                    False,
                    "google_api_key is required for Google Custom Search. "
                    "Get one at https://console.cloud.google.com/",
                )
            if not search_engine_id:
                return (
                    False,
                    "google_search_engine_id is required. "
                    "Create one at https://programmablesearchengine.google.com/",
                )

        return True, None

    # ========== Input Validation ==========

    def validate_inputs(self, inputs: List[Any]) -> tuple[bool, Optional[str]]:
        """Validate that inputs are valid search queries."""

        if not inputs or len(inputs) == 0:
            return False, "At least one search query is required"

        if self.max_inputs and len(inputs) > self.max_inputs:
            return False, f"Maximum {self.max_inputs} queries allowed, got {len(inputs)}"

        # Validate each query
        for query in inputs:
            if not isinstance(query, str):
                return False, f"Query must be a string, got {type(query)}"

            if not query.strip():
                return False, "Query cannot be empty"

            if len(query) > 500:
                return False, f"Query too long (max 500 characters): {query[:50]}..."

        return True, None

    # ========== Execution ==========

    def execute(
        self,
        inputs: List[Any],
        config: TaskConfig,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> TaskResult:
        """Execute the search & import task.

        Args:
            inputs: List of search queries
            config: Task configuration
            progress_callback: Progress reporting callback

        Returns:
            TaskResult with search results
        """
        started_at = datetime.now()

        try:
            # Report starting
            self.report_progress(0, "Starting search...", progress_callback)

            # Validate inputs
            is_valid, error_msg = self.validate_inputs(inputs)
            if not is_valid:
                return self.create_result(
                    status=TaskStatus.FAILED, started_at=started_at, error_message=error_msg
                )

            # Validate config
            is_valid, error_msg = self.validate_config(config)
            if not is_valid:
                return self.create_result(
                    status=TaskStatus.FAILED, started_at=started_at, error_message=error_msg
                )

            # Search each query
            all_results = []
            failed_queries = []

            for i, query in enumerate(inputs):
                if self.is_cancelled():
                    return self.create_result(
                        status=TaskStatus.CANCELLED,
                        started_at=started_at,
                        output_data={"results": all_results, "failed": failed_queries},
                    )

                # Calculate progress
                progress = int((i / len(inputs)) * 100)
                self.report_progress(
                    progress, f"Searching {i+1}/{len(inputs)}: {query[:50]}...", progress_callback
                )

                # Execute search
                try:
                    results = self._search_query(query, config)
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {e}")
                    failed_queries.append({"query": query, "error": str(e)})

            # Report completion
            self.report_progress(100, "Search complete!", progress_callback)

            # Determine status
            if len(all_results) == 0:
                status = TaskStatus.FAILED
                error_message = f"No results found. {len(failed_queries)} queries failed."
            elif len(failed_queries) > 0:
                status = TaskStatus.COMPLETED
                error_message = f"Partial success: {len(failed_queries)} queries failed"
            else:
                status = TaskStatus.COMPLETED
                error_message = None

            # Return result
            return self.create_result(
                status=status,
                started_at=started_at,
                output_data={
                    "results": [r.to_dict() for r in all_results],
                    "failed": failed_queries,
                    "result_count": len(all_results),
                    "query_count": len(inputs),
                },
                metadata={
                    "total_queries": len(inputs),
                    "max_results_per_query": config.get("max_results_per_query"),
                    "search_strategy": config.get("search_strategy"),
                },
                error_message=error_message,
            )

        except Exception as e:
            logger.error(f"Unexpected error in search task: {e}")
            return self.create_result(
                status=TaskStatus.FAILED,
                started_at=started_at,
                error_message=f"Unexpected error: {str(e)}",
            )

    # ========== Helper Methods ==========

    def _search_query(self, query: str, config: TaskConfig) -> List[SearchResult]:
        """Search a single query using appropriate handler.

        Args:
            query: Search query string
            config: Task configuration

        Returns:
            List of SearchResult objects
        """
        from .search_handlers import GoogleSearchHandler, get_handler_for_source

        strategy = config.get("search_strategy", "auto")  # "google" | "native" | "auto"
        sources = config.get("sources", [])  # Source domains to search

        all_results = []

        if strategy == "google":
            # Force Google only
            handler = GoogleSearchHandler()
            logger.info(f"Using Google handler for query: {query}")
            return handler.search(query, config.parameters, sources)

        elif strategy == "native":
            # Try native handlers, fail if none available
            if not sources:
                logger.warning("Native strategy requires source domains, using Google")
                handler = GoogleSearchHandler()
                return handler.search(query, config.parameters, sources)

            for source in sources:
                handler = get_handler_for_source(source)
                handler_name = handler.capability.name

                if handler_name == "google":
                    logger.warning(f"No native handler for {source}, using Google")

                try:
                    logger.info(f"Using {handler_name} handler for {source}")
                    results = handler.search(query, config.parameters, [source])
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Handler {handler_name} failed for {source}: {e}")
                    # Don't fallback in native mode - let it fail
                    raise

            return all_results

        else:  # "auto" - smart fallback (default)
            # If sources specified, try native handlers first with Google fallback
            if sources:
                for source in sources:
                    handler = get_handler_for_source(source)
                    handler_name = handler.capability.name

                    try:
                        logger.info(f"Using {handler_name} handler for {source}")
                        results = handler.search(query, config.parameters, [source])
                        all_results.extend(results)
                    except Exception as e:
                        logger.error(f"Handler {handler_name} failed, trying fallback: {e}")
                        # Fallback to Google for this source
                        google = GoogleSearchHandler()
                        try:
                            logger.info(f"Falling back to Google for {source}")
                            results = google.search(query, config.parameters, [source])
                            all_results.extend(results)
                        except Exception as fallback_error:
                            logger.error(f"Google fallback also failed: {fallback_error}")
                            # Continue with other sources

                return self._deduplicate_results(all_results)
            else:
                # No sources specified - use Google for everything
                handler = GoogleSearchHandler()
                logger.info("No sources specified, using Google handler")
                return handler.search(query, config.parameters, sources)

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results by URL.

        Args:
            results: List of SearchResult objects

        Returns:
            Deduplicated list of SearchResult objects
        """
        seen_urls = set()
        unique_results = []

        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
            else:
                logger.debug(f"Skipping duplicate URL: {result.url}")

        logger.info(f"Deduplicated {len(results)} results to {len(unique_results)}")
        return unique_results

