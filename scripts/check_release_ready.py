#!/usr/bin/env python3
"""Check if the project is ready for release.

Performs comprehensive checks before creating a release:
- Dependencies installed
- Tests passing
- Documentation complete
- Version consistency
- Build scripts functional
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

ROOT_DIR = Path(__file__).parent.parent


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            cwd=ROOT_DIR
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def check_dependencies() -> bool:
    """Check that all dependencies are installed."""
    print("Checking dependencies...")
    
    success, output = run_command([sys.executable, "-m", "pip", "check"])
    if success:
        print(f"{GREEN}✓{RESET} Dependencies OK")
        return True
    else:
        print(f"{RED}✗{RESET} Dependency issues:")
        print(output)
        return False


def check_tests() -> bool:
    """Run the test suite."""
    print("\nRunning tests...")
    
    success, output = run_command([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-q"
    ])
    
    if success:
        print(f"{GREEN}✓{RESET} All tests passing")
        return True
    else:
        print(f"{RED}✗{RESET} Some tests failing")
        return False


def check_required_files() -> bool:
    """Check that required files exist."""
    print("\nChecking required files...")
    
    required_files = [
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "docs/USER_GUIDE.md",
        "docs/QUICKSTART.md",
        "docs/PACKAGING.md",
        "scripts/build_macos.py",
        "scripts/build_windows.py",
        "pyproject.toml",
        "Makefile",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            print(f"{GREEN}✓{RESET} {file_path}")
        else:
            print(f"{RED}✗{RESET} {file_path} missing")
            all_exist = False
    
    return all_exist


def check_version_consistency() -> bool:
    """Check that version is consistent across files."""
    print("\nChecking version consistency...")
    
    # Check pyproject.toml
    pyproject = ROOT_DIR / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if 'version = "0.1.0"' in content:
            print(f"{GREEN}✓{RESET} pyproject.toml version: 0.1.0")
        else:
            print(f"{YELLOW}⚠{RESET} Version mismatch in pyproject.toml")
            return False
    
    # Check build scripts
    build_macos = ROOT_DIR / "scripts" / "build_macos.py"
    if build_macos.exists():
        content = build_macos.read_text()
        if 'APP_VERSION = "0.1.0"' in content:
            print(f"{GREEN}✓{RESET} build_macos.py version: 0.1.0")
        else:
            print(f"{YELLOW}⚠{RESET} Version mismatch in build_macos.py")
            return False
    
    build_windows = ROOT_DIR / "scripts" / "build_windows.py"
    if build_windows.exists():
        content = build_windows.read_text()
        if 'APP_VERSION = "0.1.0"' in content:
            print(f"{GREEN}✓{RESET} build_windows.py version: 0.1.0")
        else:
            print(f"{YELLOW}⚠{RESET} Version mismatch in build_windows.py")
            return False
    
    return True


def check_git_status() -> bool:
    """Check git status."""
    print("\nChecking git status...")
    
    success, output = run_command(["git", "status", "--short"])
    if success and not output.strip():
        print(f"{GREEN}✓{RESET} Working directory clean")
        return True
    else:
        print(f"{YELLOW}⚠{RESET} Uncommitted changes:")
        print(output)
        return False


def check_ollama() -> bool:
    """Check if Ollama is available."""
    print("\nChecking Ollama...")
    
    success, output = run_command(["which", "ollama"])
    if success:
        print(f"{GREEN}✓{RESET} Ollama installed")
        
        # Check if running
        success, output = run_command(["ollama", "list"])
        if success:
            print(f"{GREEN}✓{RESET} Ollama running")
            return True
        else:
            print(f"{YELLOW}⚠{RESET} Ollama not running")
            return False
    else:
        print(f"{RED}✗{RESET} Ollama not installed")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Release Readiness Check")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Required Files", check_required_files),
        ("Version Consistency", check_version_consistency),
        ("Git Status", check_git_status),
        ("Ollama", check_ollama),
        ("Tests", check_tests),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"{RED}✗{RESET} {name} check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print(f"\n{GREEN}✓ Project is ready for release!{RESET}")
        print("\nNext steps:")
        print("  1. Build distributions:")
        print("     python scripts/build_macos.py")
        print("     python scripts/build_windows.py")
        print("  2. Test distributions on clean systems")
        print("  3. Create GitHub release")
        print("  4. Update version for next release")
        sys.exit(0)
    else:
        print(f"\n{RED}✗ Project is not ready for release{RESET}")
        print("\nPlease fix the issues above before releasing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
