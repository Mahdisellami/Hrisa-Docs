"""URL Import Task implementation.

Simple task that imports a document from a URL.
"""

import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional
from urllib.parse import urlparse

import requests

from ...utils.logger import get_logger
from ..task_base import Task, TaskCategory, TaskConfig, TaskResult, TaskStatus

logger = get_logger(__name__)


class URLImportTask(Task):
    """Task for importing documents from URLs.

    Supports:
    - Direct PDF links
    - HTML pages (converts to text)
    - Academic paper links (arXiv, PubMed, etc.)
    """

    @property
    def name(self) -> str:
        return "import_url"

    @property
    def display_name(self) -> str:
        return "Import from URL"

    @property
    def description(self) -> str:
        return (
            "Import documents directly from URLs. Supports PDF links, "
            "HTML pages, and academic paper repositories."
        )

    @property
    def category(self) -> TaskCategory:
        return TaskCategory.IMPORT

    @property
    def icon(self) -> str:
        return "🔗"

    # ========== Requirements ==========

    @property
    def input_types(self) -> List[str]:
        return ["url"]

    @property
    def output_types(self) -> List[str]:
        return ["document", "pdf", "text"]

    @property
    def requires_internet(self) -> bool:
        return True

    @property
    def min_inputs(self) -> int:
        return 1  # At least one URL

    @property
    def max_inputs(self) -> Optional[int]:
        return 10  # Import up to 10 URLs at once

    # ========== Configuration ==========

    def get_default_config(self) -> TaskConfig:
        """Default URL import configuration."""
        config = TaskConfig()

        # Request parameters
        config.set("timeout", 30)  # Request timeout in seconds
        config.set("user_agent", "Mozilla/5.0 (Hrisa Docs)")
        config.set("follow_redirects", True)

        # Content handling
        config.set("extract_metadata", True)  # Extract title, author, etc.
        config.set("save_original", True)  # Keep original file
        config.set("convert_html", True)  # Convert HTML to text

        # Validation
        config.set("verify_ssl", True)  # Verify SSL certificates
        config.set("max_file_size", 50 * 1024 * 1024)  # 50 MB limit

        return config

    def validate_config(self, config: TaskConfig) -> tuple[bool, Optional[str]]:
        """Validate configuration parameters."""

        # Validate timeout
        timeout = config.get("timeout", 30)
        if not isinstance(timeout, (int, float)) or timeout < 1 or timeout > 300:
            return False, f"Timeout must be between 1 and 300 seconds, got {timeout}"

        # Validate max file size
        max_size = config.get("max_file_size", 50 * 1024 * 1024)
        if not isinstance(max_size, int) or max_size < 1024 or max_size > 500 * 1024 * 1024:
            return False, f"Max file size must be between 1KB and 500MB, got {max_size}"

        return True, None

    # ========== Input Validation ==========

    def validate_inputs(self, inputs: List[Any]) -> tuple[bool, Optional[str]]:
        """Validate that inputs are valid URLs."""

        if not inputs or len(inputs) == 0:
            return False, "At least one URL is required"

        if self.max_inputs and len(inputs) > self.max_inputs:
            return False, f"Maximum {self.max_inputs} URLs allowed, got {len(inputs)}"

        # Validate each URL
        for url in inputs:
            if not isinstance(url, str):
                return False, f"URL must be a string, got {type(url)}"

            # Basic URL validation
            try:
                parsed = urlparse(url)
                if parsed.scheme not in ["http", "https"]:
                    return False, f"URL must use http or https protocol: {url}"
                if not parsed.netloc:
                    return False, f"Invalid URL format: {url}"
            except Exception as e:
                return False, f"Invalid URL: {url} - {str(e)}"

        return True, None

    # ========== Execution ==========

    def execute(
        self,
        inputs: List[Any],
        config: TaskConfig,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> TaskResult:
        """Execute the URL import task.

        Args:
            inputs: List of URLs to import
            config: Task configuration
            progress_callback: Progress reporting callback

        Returns:
            TaskResult with imported documents
        """
        started_at = datetime.now()

        try:
            # Report starting
            self.report_progress(0, "Starting URL import...", progress_callback)

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

            # Import each URL
            imported_documents = []
            failed_urls = []

            for i, url in enumerate(inputs):
                if self.is_cancelled():
                    return self.create_result(
                        status=TaskStatus.CANCELLED,
                        started_at=started_at,
                        output_data={"imported": imported_documents, "failed": failed_urls},
                    )

                # Calculate progress
                progress = int((i / len(inputs)) * 100)
                self.report_progress(
                    progress, f"Importing {i+1}/{len(inputs)}: {url}", progress_callback
                )

                # Import URL
                try:
                    document = self._import_url(url, config)
                    imported_documents.append(document)
                except Exception as e:
                    failed_urls.append({"url": url, "error": str(e)})

            # Report completion
            self.report_progress(100, "Import complete!", progress_callback)

            # Determine status
            if len(imported_documents) == 0:
                status = TaskStatus.FAILED
                error_message = f"Failed to import any URLs. {len(failed_urls)} failed."
            elif len(failed_urls) > 0:
                status = TaskStatus.COMPLETED
                error_message = f"Partial success: {len(failed_urls)} URLs failed"
            else:
                status = TaskStatus.COMPLETED
                error_message = None

            # Return result
            return self.create_result(
                status=status,
                started_at=started_at,
                output_data={
                    "imported": imported_documents,
                    "failed": failed_urls,
                    "success_count": len(imported_documents),
                    "failure_count": len(failed_urls),
                },
                metadata={
                    "total_urls": len(inputs),
                    "timeout": config.get("timeout"),
                },
                error_message=error_message,
            )

        except Exception as e:
            return self.create_result(
                status=TaskStatus.FAILED,
                started_at=started_at,
                error_message=f"Unexpected error: {str(e)}",
            )

    # ========== Helper Methods ==========

    def _import_url(self, url: str, config: TaskConfig) -> dict:
        """Import a single URL.

        Args:
            url: URL to import
            config: Task configuration

        Returns:
            Document dict with metadata

        Raises:
            Exception if import fails
        """
        logger.info(f"Importing URL: {url}")

        # Get configuration
        timeout = config.get("timeout", 30)
        verify_ssl = config.get("verify_ssl", True)
        user_agent = config.get("user_agent", "Mozilla/5.0 (Hrisa Docs)")
        follow_redirects = config.get("follow_redirects", True)
        max_file_size = config.get("max_file_size", 50 * 1024 * 1024)
        extract_metadata = config.get("extract_metadata", True)
        save_original = config.get("save_original", True)
        convert_html = config.get("convert_html", True)

        # Prepare headers
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        # Make HTTP request
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                verify=verify_ssl,
                allow_redirects=follow_redirects,
                stream=True,  # Stream for large files
            )
            response.raise_for_status()  # Raise exception for bad status codes
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for {url}: {e}")
            raise Exception(f"Failed to fetch URL: {str(e)}")

        # Check file size
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > max_file_size:
            raise Exception(f"File too large: {int(content_length)} bytes (max: {max_file_size})")

        # Detect content type
        content_type = response.headers.get("content-type", "").lower()
        logger.info(f"Content-Type: {content_type}")

        # Determine file extension and handling strategy
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            return self._handle_pdf(url, response, config)
        elif "text/html" in content_type or "application/xhtml" in content_type:
            return self._handle_html(url, response, config)
        elif "text/plain" in content_type or url.lower().endswith(".txt"):
            return self._handle_text(url, response, config)
        else:
            # Try to handle as binary file
            logger.warning(f"Unknown content type: {content_type}, attempting binary download")
            return self._handle_binary(url, response, config)

    def _handle_pdf(self, url: str, response: requests.Response, config: TaskConfig) -> dict:
        """Handle PDF content from URL.

        Args:
            url: Source URL
            response: HTTP response object
            config: Task configuration

        Returns:
            Document dict
        """
        logger.info("Handling PDF content")

        # Generate filename from URL
        parsed = urlparse(url)
        filename = Path(parsed.path).name or "document.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        # Create unique filename using URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{Path(filename).stem}_{url_hash}.pdf"

        # Save file
        save_dir = Path("data/imported_documents")
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / filename

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Saved PDF to: {file_path}")

        # Extract metadata
        metadata = {
            "source": "url",
            "original_url": url,
            "imported_at": datetime.now().isoformat(),
            "content_type": "application/pdf",
            "file_size": file_path.stat().st_size,
        }

        return {
            "url": url,
            "title": Path(filename).stem,
            "content_type": "pdf",
            "file_path": str(file_path),
            "metadata": metadata,
        }

    def _handle_html(self, url: str, response: requests.Response, config: TaskConfig) -> dict:
        """Handle HTML content from URL.

        Args:
            url: Source URL
            response: HTTP response object
            config: Task configuration

        Returns:
            Document dict
        """
        logger.info("Handling HTML content")

        # Get HTML content
        html_content = response.text

        # Try to import BeautifulSoup
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.warning("BeautifulSoup not available, using simple text extraction")
            # Fallback: simple tag removal
            import re

            text = re.sub(r"<[^>]+>", "", html_content)
            title = "Webpage"
        else:
            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else "Webpage"

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator="\n", strip=True)

        # Clean up text
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned_text = "\n".join(lines)

        # Generate filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_"))[:50]
        filename = f"{safe_title}_{url_hash}.txt"

        # Save as text file
        save_dir = Path("data/imported_documents")
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        logger.info(f"Saved HTML as text to: {file_path}")

        # Extract metadata
        metadata = {
            "source": "url",
            "original_url": url,
            "imported_at": datetime.now().isoformat(),
            "content_type": "text/html",
            "converted_to": "text",
            "file_size": file_path.stat().st_size,
        }

        return {
            "url": url,
            "title": title,
            "content_type": "text",
            "file_path": str(file_path),
            "metadata": metadata,
        }

    def _handle_text(self, url: str, response: requests.Response, config: TaskConfig) -> dict:
        """Handle plain text content from URL.

        Args:
            url: Source URL
            response: HTTP response object
            config: Task configuration

        Returns:
            Document dict
        """
        logger.info("Handling text content")

        # Get text content
        text_content = response.text

        # Generate filename
        parsed = urlparse(url)
        filename = Path(parsed.path).name or "document.txt"
        if not filename.endswith(".txt"):
            filename += ".txt"

        # Create unique filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{Path(filename).stem}_{url_hash}.txt"

        # Save file
        save_dir = Path("data/imported_documents")
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        logger.info(f"Saved text to: {file_path}")

        # Extract metadata
        metadata = {
            "source": "url",
            "original_url": url,
            "imported_at": datetime.now().isoformat(),
            "content_type": "text/plain",
            "file_size": file_path.stat().st_size,
        }

        return {
            "url": url,
            "title": Path(filename).stem,
            "content_type": "text",
            "file_path": str(file_path),
            "metadata": metadata,
        }

    def _handle_binary(self, url: str, response: requests.Response, config: TaskConfig) -> dict:
        """Handle generic binary content from URL.

        Args:
            url: Source URL
            response: HTTP response object
            config: Task configuration

        Returns:
            Document dict
        """
        logger.info("Handling binary content")

        # Try to guess extension from URL or content-type
        parsed = urlparse(url)
        filename = Path(parsed.path).name or "document"

        # If no extension, try to guess from content-type
        if "." not in filename:
            content_type = response.headers.get("content-type", "")
            ext = mimetypes.guess_extension(content_type.split(";")[0])
            if ext:
                filename += ext
            else:
                filename += ".bin"

        # Create unique filename
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{Path(filename).stem}_{url_hash}{Path(filename).suffix}"

        # Save file
        save_dir = Path("data/imported_documents")
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / filename

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Saved binary file to: {file_path}")

        # Extract metadata
        metadata = {
            "source": "url",
            "original_url": url,
            "imported_at": datetime.now().isoformat(),
            "content_type": response.headers.get("content-type", "application/octet-stream"),
            "file_size": file_path.stat().st_size,
        }

        return {
            "url": url,
            "title": Path(filename).stem,
            "content_type": "binary",
            "file_path": str(file_path),
            "metadata": metadata,
        }
