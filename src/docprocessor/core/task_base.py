"""Base classes for the Task abstraction layer.

This module provides the foundation for all document processing tasks
in the multi-task platform architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class TaskStatus(Enum):
    """Status of a task execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskCategory(Enum):
    """Categories of tasks for organization."""

    ANALYSIS = "analysis"  # Analyze documents (AI detection, plagiarism, etc.)
    TRANSFORMATION = "transformation"  # Transform content (reformulation, style change)
    GENERATION = "generation"  # Generate new content (summarization, synthesis)
    VALIDATION = "validation"  # Validate content (spell check, citations)
    ENRICHMENT = "enrichment"  # Add information (web search, cross-reference)
    IMPORT = "import"  # Import documents (URL, web scraping)
    EXPORT = "export"  # Export results (format conversion)


@dataclass
class TaskResult:
    """Result of a task execution."""

    task_name: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Outputs
    output_data: Optional[Any] = None  # Task-specific output
    output_files: List[Path] = None  # Generated files

    # Metadata
    metadata: Dict[str, Any] = None  # Task-specific metadata

    # Error handling
    error_message: Optional[str] = None
    error_details: Optional[str] = None

    # Progress tracking
    progress_percent: int = 0
    progress_message: str = ""

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TaskConfig:
    """Configuration for task execution."""

    # Common parameters
    verbose: bool = False
    save_intermediate: bool = False

    # LLM parameters (if task uses LLM)
    llm_model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # Task-specific parameters stored in this dict
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.parameters.get(key, default)

    def set(self, key: str, value: Any):
        """Set a parameter value."""
        self.parameters[key] = value


class Task(ABC):
    """Base class for all document processing tasks.

    All tasks in the system inherit from this class and implement
    the required methods. This provides a consistent interface for
    task execution, configuration, and result handling.
    """

    def __init__(self):
        """Initialize the task."""
        self._is_cancelled = False

    # ========== Task Metadata ==========

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this task (e.g., 'summarize', 'ai_detect')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """User-facing name for this task (e.g., 'Summarize Documents')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what this task does."""
        pass

    @property
    @abstractmethod
    def category(self) -> TaskCategory:
        """Category this task belongs to."""
        pass

    @property
    def icon(self) -> str:
        """Emoji or icon for this task (for UI display)."""
        return "📋"

    # ========== Task Requirements ==========

    @property
    @abstractmethod
    def input_types(self) -> List[str]:
        """List of accepted input types.

        Examples: ['pdf', 'text', 'html', 'docx', 'document_collection']
        """
        pass

    @property
    @abstractmethod
    def output_types(self) -> List[str]:
        """List of generated output types.

        Examples: ['text', 'report', 'document', 'score', 'metadata']
        """
        pass

    @property
    def requires_llm(self) -> bool:
        """Whether this task requires an LLM."""
        return False

    @property
    def requires_internet(self) -> bool:
        """Whether this task requires internet connection."""
        return False

    @property
    def requires_embeddings(self) -> bool:
        """Whether this task requires vector embeddings."""
        return False

    @property
    def is_destructive(self) -> bool:
        """Whether this task modifies or deletes data (requires confirmation)."""
        return False

    # ========== Task Configuration ==========

    @abstractmethod
    def get_default_config(self) -> TaskConfig:
        """Return default configuration for this task."""
        pass

    @abstractmethod
    def validate_config(self, config: TaskConfig) -> tuple[bool, Optional[str]]:
        """Validate task configuration.

        Returns:
            (is_valid, error_message)
        """
        pass

    # ========== Input Validation ==========

    @abstractmethod
    def validate_inputs(self, inputs: List[Any]) -> tuple[bool, Optional[str]]:
        """Validate that inputs are appropriate for this task.

        Args:
            inputs: List of input documents/data

        Returns:
            (is_valid, error_message)
        """
        pass

    @property
    def min_inputs(self) -> int:
        """Minimum number of inputs required."""
        return 1

    @property
    def max_inputs(self) -> Optional[int]:
        """Maximum number of inputs allowed (None = unlimited)."""
        return None

    # ========== Task Execution ==========

    @abstractmethod
    def execute(
        self,
        inputs: List[Any],
        config: TaskConfig,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> TaskResult:
        """Execute the task.

        Args:
            inputs: Input documents/data for processing
            config: Task configuration
            progress_callback: Optional callback for progress updates.
                              Called with (percent: int, message: str)

        Returns:
            TaskResult containing outputs and metadata
        """
        pass

    def cancel(self):
        """Request cancellation of running task."""
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """Check if task has been cancelled."""
        return self._is_cancelled

    # ========== Helper Methods ==========

    def report_progress(
        self, percent: int, message: str, callback: Optional[Callable[[int, str], None]]
    ):
        """Report progress to callback if provided.

        Args:
            percent: Progress percentage (0-100)
            message: Progress message
            callback: Progress callback function
        """
        if callback:
            callback(percent, message)

    def create_result(
        self,
        status: TaskStatus,
        started_at: datetime,
        output_data: Any = None,
        output_files: List[Path] = None,
        metadata: Dict[str, Any] = None,
        error_message: str = None,
    ) -> TaskResult:
        """Helper to create a TaskResult."""
        return TaskResult(
            task_name=self.name,
            status=status,
            started_at=started_at,
            completed_at=datetime.now(),
            output_data=output_data,
            output_files=output_files or [],
            metadata=metadata or {},
            error_message=error_message,
        )


class TaskRegistry:
    """Central registry for all available tasks.

    Manages registration and retrieval of task implementations.
    """

    def __init__(self):
        """Initialize empty task registry."""
        self._tasks: Dict[str, Task] = {}

    def register(self, task: Task):
        """Register a task.

        Args:
            task: Task instance to register

        Raises:
            ValueError: If task with same name already registered
        """
        if task.name in self._tasks:
            raise ValueError(f"Task '{task.name}' is already registered")
        self._tasks[task.name] = task

    def unregister(self, task_name: str):
        """Unregister a task by name."""
        if task_name in self._tasks:
            del self._tasks[task_name]

    def get(self, task_name: str) -> Optional[Task]:
        """Get a task by name.

        Args:
            task_name: Name of the task

        Returns:
            Task instance or None if not found
        """
        return self._tasks.get(task_name)

    def list_all(self) -> List[Task]:
        """Get list of all registered tasks."""
        return list(self._tasks.values())

    def list_by_category(self, category: TaskCategory) -> List[Task]:
        """Get tasks in a specific category."""
        return [task for task in self._tasks.values() if task.category == category]

    def find_by_input_type(self, input_type: str) -> List[Task]:
        """Find tasks that accept a specific input type."""
        return [task for task in self._tasks.values() if input_type in task.input_types]

    def find_by_output_type(self, output_type: str) -> List[Task]:
        """Find tasks that produce a specific output type."""
        return [task for task in self._tasks.values() if output_type in task.output_types]

    def is_registered(self, task_name: str) -> bool:
        """Check if a task is registered."""
        return task_name in self._tasks

    def count(self) -> int:
        """Get number of registered tasks."""
        return len(self._tasks)


# Global task registry instance
_global_registry = TaskRegistry()


def get_task_registry() -> TaskRegistry:
    """Get the global task registry instance."""
    return _global_registry


def register_task(task: Task):
    """Register a task in the global registry.

    Args:
        task: Task instance to register
    """
    _global_registry.register(task)


def get_task(task_name: str) -> Optional[Task]:
    """Get a task from the global registry.

    Args:
        task_name: Name of the task

    Returns:
        Task instance or None if not found
    """
    return _global_registry.get(task_name)
