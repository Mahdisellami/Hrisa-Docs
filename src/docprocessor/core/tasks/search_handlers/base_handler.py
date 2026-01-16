"""Base handler interface for search implementations.

This module defines the abstract base class that all search handlers must implement,
providing a consistent interface for different search strategies (Google API, CKAN API, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ....models.project import SearchResult


@dataclass
class HandlerCapability:
    """Describes what a search handler can do.

    Attributes:
        name: Handler identifier (e.g., "google", "ckan-data.gov.tn")
        domains: List of domains this handler can search
        requires_api_key: Whether this handler needs API credentials
        search_types: Types of search supported ("api", "form", "scraping")
        reliability: Expected reliability ("high", "medium", "low")
    """

    name: str
    domains: List[str]
    requires_api_key: bool
    search_types: List[str] = field(default_factory=lambda: ["api"])
    reliability: str = "medium"


class SearchHandler(ABC):
    """Abstract base class for all search handlers.

    All search handlers must implement this interface to be compatible
    with the SearchImportTask dispatcher.

    Example:
        class MyCustomHandler(SearchHandler):
            @property
            def capability(self) -> HandlerCapability:
                return HandlerCapability(
                    name="my-custom-handler",
                    domains=["example.com"],
                    requires_api_key=False,
                    search_types=["api"],
                    reliability="high"
                )

            def can_handle(self, source_domain: Optional[str] = None) -> bool:
                return source_domain and "example.com" in source_domain

            def search(self, query: str, config: dict, source_filter: Optional[List[str]] = None) -> List[SearchResult]:
                # Implement search logic
                return []

            def validate_config(self, config: dict) -> tuple[bool, Optional[str]]:
                return True, None
    """

    @property
    @abstractmethod
    def capability(self) -> HandlerCapability:
        """Return handler capabilities.

        Returns:
            HandlerCapability describing this handler's features
        """
        pass

    @abstractmethod
    def can_handle(self, source_domain: Optional[str] = None) -> bool:
        """Check if this handler can handle the given source domain.

        Args:
            source_domain: Domain name to check (e.g., "data.gov.tn")

        Returns:
            True if this handler can search the source, False otherwise
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        config: dict,
        source_filter: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Execute search and return results.

        Args:
            query: Search query string
            config: Configuration dictionary (from TaskConfig.parameters)
            source_filter: Optional list of source domains to restrict search to

        Returns:
            List of SearchResult objects

        Raises:
            Exception: If search fails (will trigger fallback in auto mode)
        """
        pass

    @abstractmethod
    def validate_config(self, config: dict) -> tuple[bool, Optional[str]]:
        """Validate handler-specific configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message should be None
        """
        pass

    def is_available(self) -> bool:
        """Check if handler is available (dependencies installed, etc.).

        Returns:
            True if handler can be used, False otherwise

        Note:
            Default implementation returns True. Override if handler has
            optional dependencies that might not be installed.
        """
        return True
