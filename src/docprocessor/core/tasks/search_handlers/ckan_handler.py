"""CKAN API handler for data.gov.tn open data portal."""

import requests
from typing import List, Optional

from ....models.project import SearchResult
from ....utils.logger import get_logger
from .base_handler import HandlerCapability, SearchHandler

logger = get_logger(__name__)


class CKANSearchHandler(SearchHandler):
    """Handler for CKAN-based open data portals (data.gov.tn).

    CKAN (Comprehensive Knowledge Archive Network) is a standard platform
    for open data portals. This handler uses the CKAN API to search for
    datasets and resources on data.gov.tn.

    API Documentation: https://docs.ckan.org/en/2.9/api/

    Configuration:
        max_results_per_query: Maximum results to return (default: 10)
    """

    BASE_URL = "https://catalog.data.gov.tn/api/3/action/"

    @property
    def capability(self) -> HandlerCapability:
        """Return CKAN handler capabilities."""
        return HandlerCapability(
            name="ckan-data.gov.tn",
            domains=["data.gov.tn", "catalog.data.gov.tn"],
            requires_api_key=False,  # CKAN API is typically public
            search_types=["api"],
            reliability="medium",  # Less tested than Google
        )

    def can_handle(self, source_domain: Optional[str] = None) -> bool:
        """Check if this handler can handle the given domain.

        Args:
            source_domain: Domain to check

        Returns:
            True if domain is data.gov.tn or catalog.data.gov.tn
        """
        if not source_domain:
            return False
        return any(domain in source_domain for domain in self.capability.domains)

    def search(
        self,
        query: str,
        config: dict,
        source_filter: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Search using CKAN package_search API.

        Args:
            query: Search query string
            config: Configuration dictionary
            source_filter: Ignored for CKAN (single portal)

        Returns:
            List of SearchResult objects

        Raises:
            requests.RequestException: If API request fails
            Exception: If API returns error
        """
        max_results = config.get("max_results_per_query", 10)

        # CKAN API endpoint
        endpoint = f"{self.BASE_URL}package_search"
        params = {
            "q": query,
            "rows": max_results,
            "sort": "score desc, metadata_modified desc",
        }

        logger.info(f"CKAN search: {query} (max {max_results} results)")

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                error_msg = data.get("error", {}).get("message", "Unknown error")
                raise Exception(f"CKAN API returned error: {error_msg}")

            results = []
            packages = data.get("result", {}).get("results", [])

            logger.info(f"Found {len(packages)} packages from CKAN")

            for package in packages:
                # Extract resources (datasets) from each package
                resources = package.get("resources", [])

                # Limit resources per package to avoid too many results
                for resource in resources[:2]:  # Max 2 resources per package
                    url = resource.get("url", "")
                    if not url:
                        continue  # Skip resources without URLs

                    # Get resource format
                    format_str = resource.get("format", "").lower()
                    file_type = self._detect_format(format_str)

                    # Build result
                    result = SearchResult(
                        title=package.get("title", resource.get("name", "Untitled")),
                        url=url,
                        snippet=package.get("notes", "")[:200],  # Limit snippet length
                        source_name="data.gov.tn",
                        file_type=file_type,
                        relevance_score=0.0,  # CKAN doesn't provide relevance scores
                        metadata={
                            "package_id": package.get("id"),
                            "package_name": package.get("name"),
                            "organization": package.get("organization", {}).get("name"),
                            "tags": [tag.get("name") for tag in package.get("tags", [])],
                            "resource_id": resource.get("id"),
                            "resource_name": resource.get("name"),
                            "resource_format": resource.get("format"),
                            "handler_used": "ckan",
                        },
                        search_query=query,
                    )
                    results.append(result)

                # Stop if we have enough results
                if len(results) >= max_results:
                    break

            # Limit total results
            results = results[:max_results]

            logger.info(f"Returning {len(results)} CKAN results")
            return results

        except requests.RequestException as e:
            logger.error(f"CKAN API request failed: {e}")
            raise

        except Exception as e:
            logger.error(f"CKAN search error: {e}")
            raise

    def validate_config(self, config: dict) -> tuple[bool, Optional[str]]:
        """Validate CKAN configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, error_message)
            CKAN requires no special configuration
        """
        # CKAN has no required configuration
        return True, None

    def is_available(self) -> bool:
        """Check if CKAN handler is available.

        Returns:
            True if requests library is available (should always be True)
        """
        try:
            import requests  # noqa: F401

            return True
        except ImportError:
            return False

    def _detect_format(self, format_str: str) -> str:
        """Map CKAN formats to standard file types.

        Args:
            format_str: Format string from CKAN (e.g., "PDF", "CSV", "JSON")

        Returns:
            Standard file type: "pdf", "csv", "json", "html", etc.
        """
        format_map = {
            "pdf": "pdf",
            "csv": "csv",
            "json": "json",
            "xml": "xml",
            "html": "html",
            "htm": "html",
            "xls": "xls",
            "xlsx": "xlsx",
            "doc": "docx",
            "docx": "docx",
            "txt": "text",
            "zip": "zip",
            "geojson": "json",
            "kml": "xml",
            "shp": "shapefile",
        }

        format_lower = format_str.lower().strip()
        return format_map.get(format_lower, "html")  # Default to HTML
