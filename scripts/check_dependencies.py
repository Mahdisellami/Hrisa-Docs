#!/usr/bin/env python3
"""
Dependency checker and installer for Hrisa Docs.

Checks for required dependencies (Ollama, Pandoc) and offers to install them.
Supports macOS, Windows, and Linux.
"""

import os
import platform
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


class DependencyChecker:
    """Check and install Hrisa Docs dependencies."""

    def __init__(self):
        self.system = platform.system()
        self.issues = []
        self.ollama_installed = False
        self.pandoc_installed = False
        self.model_available = False

    def check_ollama(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                print("✅ Ollama is installed:", result.stdout.strip())
                self.ollama_installed = True
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        print("❌ Ollama is not installed")
        self.issues.append("ollama")
        return False

    def check_pandoc(self) -> bool:
        """Check if Pandoc is installed."""
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.split("\n")[0]
                print(f"✅ Pandoc is installed: {version}")
                self.pandoc_installed = True
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        print("⚠️  Pandoc is not installed (optional, needed for PDF export)")
        self.issues.append("pandoc")
        return False

    def check_ollama_model(self, model_name: str = "llama3.1:latest") -> bool:
        """Check if required Ollama model is available."""
        if not self.ollama_installed:
            return False

        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and model_name.split(":")[0] in result.stdout:
                print(f"✅ Model '{model_name}' is available")
                self.model_available = True
                return True
        except subprocess.TimeoutExpired:
            pass

        print(f"❌ Model '{model_name}' is not available")
        self.issues.append("model")
        return False

    def install_ollama(self) -> bool:
        """Install Ollama based on platform."""
        print("\n📦 Installing Ollama...")

        if self.system == "Darwin":  # macOS
            return self._install_ollama_macos()
        elif self.system == "Windows":
            return self._install_ollama_windows()
        elif self.system == "Linux":
            return self._install_ollama_linux()
        else:
            print(f"❌ Unsupported platform: {self.system}")
            return False

    def _install_ollama_macos(self) -> bool:
        """Install Ollama on macOS."""
        try:
            print("Downloading Ollama installer for macOS...")
            url = "https://ollama.ai/download/Ollama-darwin.zip"
            zip_path = Path("/tmp/Ollama.zip")

            urllib.request.urlretrieve(url, zip_path)

            print("Installing Ollama...")
            subprocess.run(["open", str(zip_path)], check=True)

            print("\n⚠️  Please complete the Ollama installation manually")
            print("   After installation, run this script again")
            return False

        except Exception as e:
            print(f"❌ Failed to download Ollama: {e}")
            print("   Please install manually from: https://ollama.ai/download")
            return False

    def _install_ollama_windows(self) -> bool:
        """Install Ollama on Windows."""
        try:
            print("Downloading Ollama installer for Windows...")
            url = "https://ollama.ai/download/OllamaSetup.exe"
            installer_path = Path.home() / "Downloads" / "OllamaSetup.exe"

            print(f"   Saving to: {installer_path}")
            urllib.request.urlretrieve(url, installer_path)
            print("   Download complete!")

            print("\nInstalling Ollama (this may take a few minutes)...")
            print("   Running silent installation...")

            # Run installer with silent flag and wait for completion
            result = subprocess.run(
                [str(installer_path), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
                check=False,
                capture_output=True,
                text=True,
            )

            print(f"   Installer exit code: {result.returncode}")

            if result.returncode == 0:
                print("✅ Ollama installer completed successfully")
                # Wait a moment for service to start
                import time
                print("   Waiting for Ollama service to start...")
                time.sleep(5)

                # Try to start Ollama service explicitly
                try:
                    print("   Attempting to start Ollama service...")
                    subprocess.run(
                        ["net", "start", "Ollama"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                except Exception as e:
                    print(f"   Note: Could not start service explicitly: {e}")

                # Verify Ollama is accessible
                try:
                    verify_result = subprocess.run(
                        ["ollama", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if verify_result.returncode == 0:
                        print(f"   ✅ Ollama is responding: {verify_result.stdout.strip()}")
                        self.ollama_installed = True
                        return True
                    else:
                        print("   ⚠️  Ollama installed but not responding yet")
                        self.ollama_installed = False
                        return False
                except Exception as e:
                    print(f"   ⚠️  Cannot verify Ollama: {e}")
                    self.ollama_installed = False
                    return False
            else:
                print(f"⚠️  Installer exited with code {result.returncode}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                if result.stderr:
                    print(f"   Errors: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to install Ollama: {e}")
            print(f"   Exception type: {type(e).__name__}")
            print(f"   Exception details: {str(e)}")
            print("   Please install manually from: https://ollama.ai/download")
            return False

    def _install_ollama_linux(self) -> bool:
        """Install Ollama on Linux."""
        try:
            print("Installing Ollama via curl script...")
            subprocess.run(
                ["curl", "-fsSL", "https://ollama.ai/install.sh"],
                stdout=subprocess.PIPE,
                check=True,
            )
            result = subprocess.run(
                ["sh", "-"],
                stdin=subprocess.PIPE,
                check=True,
            )

            if result.returncode == 0:
                print("✅ Ollama installed successfully")
                self.ollama_installed = True
                return True

        except Exception as e:
            print(f"❌ Failed to install Ollama: {e}")
            print("   Please install manually: curl -fsSL https://ollama.ai/install.sh | sh")
            return False

        return False

    def install_pandoc(self) -> bool:
        """Install Pandoc based on platform."""
        print("\n📦 Installing Pandoc (optional)...")

        if self.system == "Darwin":  # macOS
            return self._install_pandoc_macos()
        elif self.system == "Windows":
            return self._install_pandoc_windows()
        elif self.system == "Linux":
            return self._install_pandoc_linux()

        return False

    def _install_pandoc_macos(self) -> bool:
        """Install Pandoc on macOS via Homebrew."""
        try:
            # Check if Homebrew is installed
            subprocess.run(["brew", "--version"], capture_output=True, check=True)

            print("Installing Pandoc via Homebrew...")
            subprocess.run(["brew", "install", "pandoc"], check=True)

            print("✅ Pandoc installed successfully")
            self.pandoc_installed = True
            return True

        except subprocess.CalledProcessError:
            print("❌ Homebrew not found. Install from: https://brew.sh")
            print("   Or download Pandoc from: https://pandoc.org/installing.html")
            return False

    def _install_pandoc_windows(self) -> bool:
        """Install Pandoc on Windows."""
        try:
            print("Downloading Pandoc installer for Windows...")
            url = "https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-windows-x86_64.msi"
            installer_path = Path.home() / "Downloads" / "pandoc-installer.msi"

            print(f"   Saving to: {installer_path}")
            urllib.request.urlretrieve(url, installer_path)
            print("   Download complete!")

            print("\nInstalling Pandoc (this may take a minute)...")
            print("   Running silent installation...")

            # Run MSI installer silently with /qn (quiet, no UI) flag
            result = subprocess.run(
                ["msiexec", "/i", str(installer_path), "/qn", "/norestart"],
                check=False,
                capture_output=True,
                text=True,
            )

            print(f"   Installer exit code: {result.returncode}")

            if result.returncode == 0:
                print("✅ Pandoc installed successfully")
                self.pandoc_installed = True
                return True
            else:
                print(f"⚠️  Installer exited with code {result.returncode}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                if result.stderr:
                    print(f"   Errors: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to install Pandoc: {e}")
            print(f"   Exception type: {type(e).__name__}")
            print(f"   Exception details: {str(e)}")
            print("   Download manually from: https://pandoc.org/installing.html")
            return False

    def _install_pandoc_linux(self) -> bool:
        """Install Pandoc on Linux."""
        try:
            # Try apt-get first (Debian/Ubuntu)
            subprocess.run(
                ["sudo", "apt-get", "update"],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "pandoc"],
                check=True,
            )

            print("✅ Pandoc installed successfully")
            self.pandoc_installed = True
            return True

        except subprocess.CalledProcessError:
            try:
                # Try yum (RHEL/CentOS)
                subprocess.run(
                    ["sudo", "yum", "install", "-y", "pandoc"],
                    check=True,
                )
                print("✅ Pandoc installed successfully")
                self.pandoc_installed = True
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install Pandoc")
                print("   Install manually: https://pandoc.org/installing.html")
                return False

        return False

    def pull_ollama_model(self, model_name: str = "llama3.1:latest") -> bool:
        """Pull the required Ollama model."""
        if not self.ollama_installed:
            print("❌ Ollama must be installed first")
            return False

        print(f"\n📦 Pulling Ollama model '{model_name}'...")
        print("   This may take several minutes (4-5 GB download)...")

        try:
            subprocess.run(
                ["ollama", "pull", model_name],
                check=True,
            )

            print(f"✅ Model '{model_name}' pulled successfully")
            self.model_available = True
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to pull model: {e}")
            return False

    def run_checks(self, auto_install: bool = False) -> bool:
        """Run all dependency checks."""
        print("=" * 60)
        print("Hrisa Docs - Dependency Checker")
        print("=" * 60)
        print()

        # Check all dependencies
        ollama_ok = self.check_ollama()
        pandoc_ok = self.check_pandoc()

        if ollama_ok:
            model_ok = self.check_ollama_model()
        else:
            model_ok = False

        print()
        print("=" * 60)

        # If all OK
        if ollama_ok and model_ok:
            print("✅ All required dependencies are installed!")
            if not pandoc_ok:
                print("⚠️  Pandoc is optional but recommended for PDF export")
            return True

        # If auto-install enabled
        if auto_install:
            print("\n🔧 Auto-installing missing dependencies...")

            if not ollama_ok:
                print("\n📦 Installing Ollama...")
                self.install_ollama()
                # Re-check after installation attempt
                print("\n🔍 Verifying Ollama installation...")
                ollama_ok = self.check_ollama()

            if ollama_ok and not model_ok:
                print("\n📦 Pulling required model...")
                self.pull_ollama_model()
                # Re-check model
                model_ok = self.check_ollama_model()

            if not pandoc_ok:
                # In auto mode, automatically install Pandoc (optional but recommended)
                print("\n📦 Installing Pandoc (optional, for PDF export)...")
                self.install_pandoc()

            # Final summary
            print("\n" + "=" * 60)
            print("Installation Summary:")
            print(f"  Ollama: {'✅ Installed' if self.ollama_installed else '❌ Not installed'}")
            print(f"  Model:  {'✅ Available' if self.model_available else '❌ Not available'}")
            print(f"  Pandoc: {'✅ Installed' if self.pandoc_installed else '⚠️  Not installed (optional)'}")
            print("=" * 60)

            return self.ollama_installed and self.model_available

        # Interactive mode
        print("\n❌ Missing dependencies:")
        for issue in self.issues:
            print(f"   - {issue}")

        print("\nOptions:")
        print("1. Install Ollama (required)")
        if ollama_ok and not model_ok:
            print("2. Pull required model (required)")
        if not pandoc_ok:
            print("3. Install Pandoc (optional, for PDF export)")
        print("0. Exit")

        return False


def main():
    """Main entry point."""
    # Set up logging to file for debugging (especially on Windows)
    log_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", ".")))
    log_file = log_dir / "hrisa_deps_install.log"

    try:
        # Create log file and redirect output
        log_handle = open(log_file, "w", encoding="utf-8")
        # Keep original stdout/stderr for later
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # Redirect to log file
        sys.stdout = log_handle
        sys.stderr = log_handle

        print(f"=== Hrisa Docs Dependency Installation Log ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Python: {sys.executable}")
        print(f"Python Version: {sys.version}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Machine: {platform.machine()}")
        print(f"Arguments: {sys.argv}")
        print(f"Log file: {log_file}")
        print("=" * 60)
        print()

        checker = DependencyChecker()

        # Check if running in auto mode
        auto_install = "--auto" in sys.argv or "-a" in sys.argv
        print(f"Auto-install mode: {auto_install}")
        print()

        result = checker.run_checks(auto_install=auto_install)

        if not result:
            print("\n" + "=" * 60)
            print("⚠️  Please install missing dependencies and run again")
            print("=" * 60)
            log_handle.close()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            # Show message to user
            print(f"\n⚠️  Dependency installation incomplete. See log: {log_file}")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("🚀 Ready to use Hrisa Docs!")
        print("=" * 60)

        log_handle.close()
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        # Show success message to user
        print(f"\n✅ Dependencies installed successfully. Log: {log_file}")
        sys.exit(0)

    except Exception as e:
        # Handle logging errors
        try:
            print(f"ERROR in dependency checker: {e}", file=sys.stderr)
            if "log_handle" in locals():
                log_handle.close()
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
