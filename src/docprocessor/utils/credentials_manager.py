"""
Credentials Manager for securely storing sensitive credentials using OS keyring.

This module provides a singleton CredentialsManager class that uses the system keyring
(macOS Keychain, Windows Credential Manager, Linux Secret Service) to securely store
and retrieve API credentials.
"""

from typing import Optional
import keyring
from keyring.errors import KeyringError

from .logger import get_logger

logger = get_logger(__name__)


class CredentialsManager:
    """
    Singleton manager for securely storing and retrieving credentials using OS keyring.

    Uses the system's native credential storage:
    - macOS: Keychain
    - Windows: Credential Manager
    - Linux: Secret Service (e.g., GNOME Keyring, KWallet)
    """

    _instance: Optional["CredentialsManager"] = None
    SERVICE_NAME = "DocProcessor-SearchImport"
    KEY_GOOGLE_API = "google_api_key"
    KEY_GOOGLE_ENGINE = "google_search_engine_id"

    def __new__(cls):
        """Singleton pattern - only one instance throughout app lifetime."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the credentials manager."""
        if self._initialized:
            return
        self._initialized = True
        logger.debug("CredentialsManager initialized")

    def is_keyring_available(self) -> bool:
        """
        Check if keyring is available and functioning.

        Returns:
            bool: True if keyring is available, False otherwise
        """
        try:
            # Test keyring by trying to access it
            keyring.get_keyring()
            return True
        except Exception as e:
            logger.warning(f"Keyring unavailable: {e}")
            return False

    def save_google_credentials(self, api_key: str, engine_id: str) -> bool:
        """
        Save Google Custom Search credentials securely to OS keyring.

        Args:
            api_key: Google API key
            engine_id: Google Custom Search Engine ID

        Returns:
            bool: True if saved successfully, False if keyring unavailable
        """
        try:
            keyring.set_password(self.SERVICE_NAME, self.KEY_GOOGLE_API, api_key)
            keyring.set_password(self.SERVICE_NAME, self.KEY_GOOGLE_ENGINE, engine_id)
            logger.info("Saved Google API credentials to keyring")
            return True
        except KeyringError as e:
            logger.error(f"Failed to save credentials to keyring: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving credentials: {e}")
            return False

    def load_google_credentials(self) -> Optional[tuple[str, str]]:
        """
        Load Google Custom Search credentials from OS keyring.

        Returns:
            Optional[tuple[str, str]]: (api_key, engine_id) if found, None otherwise
        """
        try:
            api_key = keyring.get_password(self.SERVICE_NAME, self.KEY_GOOGLE_API)
            engine_id = keyring.get_password(self.SERVICE_NAME, self.KEY_GOOGLE_ENGINE)

            if api_key and engine_id:
                logger.debug("Loaded Google API credentials from keyring")
                return (api_key, engine_id)
            else:
                logger.debug("No saved credentials found in keyring")
                return None
        except KeyringError as e:
            logger.warning(f"Failed to load credentials from keyring: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading credentials: {e}")
            return None

    def clear_google_credentials(self) -> bool:
        """
        Clear Google Custom Search credentials from OS keyring.

        Returns:
            bool: True if cleared successfully, False if keyring unavailable
        """
        try:
            try:
                keyring.delete_password(self.SERVICE_NAME, self.KEY_GOOGLE_API)
            except keyring.errors.PasswordDeleteError:
                # Key doesn't exist, that's fine
                pass

            try:
                keyring.delete_password(self.SERVICE_NAME, self.KEY_GOOGLE_ENGINE)
            except keyring.errors.PasswordDeleteError:
                # Key doesn't exist, that's fine
                pass

            logger.info("Cleared Google API credentials from keyring")
            return True
        except KeyringError as e:
            logger.error(f"Failed to clear credentials from keyring: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error clearing credentials: {e}")
            return False


# Global singleton instance accessor
_credentials_manager_instance: Optional[CredentialsManager] = None


def get_credentials_manager() -> CredentialsManager:
    """
    Get the global CredentialsManager singleton instance.

    Returns:
        CredentialsManager: The singleton instance
    """
    global _credentials_manager_instance
    if _credentials_manager_instance is None:
        _credentials_manager_instance = CredentialsManager()
    return _credentials_manager_instance
