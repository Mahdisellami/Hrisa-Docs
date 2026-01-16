"""Google Custom Search API handler - reliable fallback for all sources."""

from typing import List, Optional
from urllib.parse import urlparse

from ....models.project import SearchResult
from ....utils.logger import get_logger
from .base_handler import HandlerCapability, SearchHandler

logger = get_logger(__name__)


class GoogleSearchHandler(SearchHandler):
    """Handler for Google Custom Search API.

    This handler uses Google's Custom Search API to search any website.
    It's the most reliable fallback as it can handle any domain and doesn't
    require scraping or site-specific knowledge.

    Configuration:
        google_api_key: Google Cloud API key (required)
        google_search_engine_id: Programmable Search Engine ID (required)
        max_results_per_query: Maximum results to return (default: 10)
        file_types: List of file types to filter (default: ["pdf", "html", "docx"])
    """

    @property
    def capability(self) -> HandlerCapability:
        """Return Google handler capabilities."""
        return HandlerCapability(
            name="google",
            domains=["*"],  # Can search any domain
            requires_api_key=True,
            search_types=["api"],
            reliability="high",
        )

    def can_handle(self, source_domain: Optional[str] = None) -> bool:
        """Google can handle any domain.

        Args:
            source_domain: Domain to check (ignored, always returns True)

        Returns:
            Always True - Google can search any site
        """
        return True

    def search(
        self,
        query: str,
        config: dict,
        source_filter: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Search using Google Custom Search API.

        Args:
            query: Search query string
            config: Configuration dictionary with google_api_key and google_search_engine_id
            source_filter: Optional list of domains to restrict search to

        Returns:
            List of SearchResult objects

        Raises:
            ImportError: If google-api-python-client not installed
            Exception: If Google API returns an error
        """
        try:
            from googleapiclient.discovery import build
        except ImportError:
            raise ImportError(
                "google-api-python-client is required for Google Custom Search. "
                "Install with: pip install google-api-python-client"
            )

        api_key = config.get("google_api_key")
        search_engine_id = config.get("google_search_engine_id")
        max_results = config.get("max_results_per_query", 10)
        file_types = config.get("file_types", ["pdf", "html", "docx"])

        # Build search query with site restrictions if specified
        search_query = query
        if source_filter and len(source_filter) > 0:
            # Add site: operator for each source
            site_queries = " OR ".join([f"site:{source}" for source in source_filter])
            search_query = f"{query} ({site_queries})"

        # Add file type restrictions
        if file_types and len(file_types) > 0:
            filetype_query = " OR ".join([f"filetype:{ft}" for ft in file_types])
            search_query = f"{search_query} ({filetype_query})"

        logger.info(f"Google search query: {search_query}")

        # Execute Google Custom Search
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            response = (
                service.cse()
                .list(q=search_query, cx=search_engine_id, num=min(max_results, 10))
                .execute()
            )

            # Parse results
            results = []
            items = response.get("items", [])

            for item in items:
                # Extract file type from URL
                url = item.get("link", "")
                file_type = self._detect_file_type(url)

                # Extract source domain
                parsed_url = urlparse(url)
                source_name = parsed_url.netloc

                # Create SearchResult
                result = SearchResult(
                    title=item.get("title", "Untitled"),
                    url=url,
                    snippet=item.get("snippet", ""),
                    source_name=source_name,
                    file_type=file_type,
                    relevance_score=0.0,  # Google doesn't provide scores
                    metadata={
                        "displayLink": item.get("displayLink"),
                        "formattedUrl": item.get("formattedUrl"),
                        "handler_used": "google",
                    },
                    search_query=query,
                )
                results.append(result)

            logger.info(f"Found {len(results)} results for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Google Custom Search error: {e}")
            raise

    def validate_config(self, config: dict) -> tuple[bool, Optional[str]]:
        """Validate Google API configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
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

    def is_available(self) -> bool:
        """Check if Google API client is installed.

        Returns:
            True if google-api-python-client is available
        """
        try:
            from googleapiclient.discovery import build  # noqa: F401

            return True
        except ImportError:
            return False

    def _detect_file_type(self, url: str) -> str:
        """Detect file type from URL extension.

        Args:
            url: URL string

        Returns:
            File type: "pdf", "html", "docx", etc.
        """
        url_lower = url.lower()

        if url_lower.endswith(".pdf"):
            return "pdf"
        elif url_lower.endswith(".docx") or url_lower.endswith(".doc"):
            return "docx"
        elif url_lower.endswith(".html") or url_lower.endswith(".htm"):
            return "html"
        elif url_lower.endswith(".txt"):
            return "text"
        elif url_lower.endswith(".xml"):
            return "xml"
        else:
            # Default to HTML for web pages
            return "html"
