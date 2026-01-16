"""Search handler registry and management.

This module provides a centralized registry of all available search handlers
and utility functions for selecting the best handler for a given source.

Usage:
    from docprocessor.core.tasks.search_handlers import get_handler_for_source

    handler = get_handler_for_source("data.gov.tn")
    results = handler.search("budget public", config)
"""

from typing import List, Optional

from .base_handler import HandlerCapability, SearchHandler
from .ckan_handler import CKANSearchHandler
from .google_handler import GoogleSearchHandler

# Static handler registry - simple and explicit
# Handlers are tried in order, so put native handlers first
REGISTERED_HANDLERS: List[SearchHandler] = [
    CKANSearchHandler(),  # Try native handlers first
    GoogleSearchHandler(),  # Google as fallback (can handle anything)
]


def get_handler_for_source(source_domain: Optional[str] = None) -> SearchHandler:
    """Get the best handler for a source domain.

    Tries each registered handler in order and returns the first one that
    can handle the domain and is available. Google handler is always last
    as the fallback since it can handle any domain.

    Args:
        source_domain: Domain name (e.g., "data.gov.tn") or None for any

    Returns:
        SearchHandler that can handle the source

    Example:
        >>> handler = get_handler_for_source("data.gov.tn")
        >>> print(handler.capability.name)
        'ckan-data.gov.tn'

        >>> handler = get_handler_for_source("finances.gov.tn")
        >>> print(handler.capability.name)
        'google'  # Falls back to Google
    """
    for handler in REGISTERED_HANDLERS:
        if handler.can_handle(source_domain) and handler.is_available():
            return handler

    # Fallback to Google (should always work since it can handle any domain)
    # This line should never be reached if GoogleSearchHandler is in the registry
    return GoogleSearchHandler()


def get_all_handlers() -> List[SearchHandler]:
    """Get all registered handlers.

    Returns:
        List of all registered SearchHandler instances

    Example:
        >>> handlers = get_all_handlers()
        >>> for h in handlers:
        ...     print(f"{h.capability.name}: {h.capability.domains}")
        ckan-data.gov.tn: ['data.gov.tn', 'catalog.data.gov.tn']
        google: ['*']
    """
    return REGISTERED_HANDLERS


def get_handler_by_name(name: str) -> Optional[SearchHandler]:
    """Get a handler by its capability name.

    Args:
        name: Handler name (e.g., "google", "ckan-data.gov.tn")

    Returns:
        SearchHandler with matching name, or None if not found

    Example:
        >>> handler = get_handler_by_name("ckan-data.gov.tn")
        >>> handler.search("données ouvertes", config)
    """
    for handler in REGISTERED_HANDLERS:
        if handler.capability.name == name:
            return handler
    return None


def list_handler_capabilities() -> List[HandlerCapability]:
    """Get capabilities of all registered handlers.

    Returns:
        List of HandlerCapability objects

    Example:
        >>> caps = list_handler_capabilities()
        >>> for cap in caps:
        ...     print(f"{cap.name} - Reliability: {cap.reliability}")
        ckan-data.gov.tn - Reliability: medium
        google - Reliability: high
    """
    return [handler.capability for handler in REGISTERED_HANDLERS]


# Export public API
__all__ = [
    "SearchHandler",
    "HandlerCapability",
    "GoogleSearchHandler",
    "CKANSearchHandler",
    "REGISTERED_HANDLERS",
    "get_handler_for_source",
    "get_all_handlers",
    "get_handler_by_name",
    "list_handler_capabilities",
]
