#!/usr/bin/env python3
"""Manual test script for URL Import Task."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docprocessor.core.tasks.url_import_task import URLImportTask
from docprocessor.core.task_base import TaskStatus


def progress_callback(percent, message):
    """Print progress updates."""
    print(f"[{percent:3d}%] {message}")


def test_url_import():
    """Test URL import with real URLs."""
    print("=" * 60)
    print("URL Import Task - Manual Test")
    print("=" * 60)
    print()

    # Create task
    task = URLImportTask()
    config = task.get_default_config()

    # Test URLs (using safe, public URLs)
    test_urls = [
        # Example.com text page
        "http://example.com",

        # A small public PDF (W3C specification - small)
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",

        # Plain text file
        "https://www.ietf.org/rfc/rfc2616.txt",
    ]

    print("Testing URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    print()

    # Execute task
    print("Starting import...")
    print("-" * 60)

    result = task.execute(
        inputs=test_urls,
        config=config,
        progress_callback=progress_callback
    )

    print("-" * 60)
    print()

    # Display results
    print(f"Status: {result.status.value}")
    print(f"Duration: {(result.completed_at - result.started_at).total_seconds():.2f}s")
    print()

    if result.status == TaskStatus.COMPLETED or result.output_data.get("success_count", 0) > 0:
        print(f"✅ Successfully imported: {result.output_data['success_count']}")
        print()

        if result.output_data['imported']:
            print("Imported documents:")
            for doc in result.output_data['imported']:
                print(f"  • {doc['title']}")
                print(f"    Type: {doc['content_type']}")
                print(f"    Path: {doc['file_path']}")
                print(f"    Size: {doc['metadata']['file_size']} bytes")
                print()

    if result.output_data.get("failed"):
        print(f"❌ Failed: {result.output_data['failure_count']}")
        print()
        print("Failed URLs:")
        for failed in result.output_data['failed']:
            print(f"  • {failed['url']}")
            print(f"    Error: {failed['error']}")
            print()

    # Show where files were saved
    if result.output_data.get("success_count", 0) > 0:
        print("=" * 60)
        print("Files saved to: data/imported_documents/")
        print("You can check the directory to see the downloaded files.")
        print()

    return result.status == TaskStatus.COMPLETED


if __name__ == "__main__":
    try:
        success = test_url_import()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
