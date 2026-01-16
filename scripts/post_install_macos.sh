#!/bin/bash
#
# Post-installation script for Hrisa Docs on macOS
# Checks and installs dependencies (Ollama, Pandoc)
#

set -e

echo "================================"
echo "Hrisa Docs - Dependency Setup"
echo "================================"
echo ""

# Check if we're in an app bundle
if [ -d "/Applications/Hrisa Docs.app" ]; then
    APP_DIR="/Applications/Hrisa Docs.app"
else
    echo "⚠️  Hrisa Docs not found in /Applications"
    echo "   Please install the app first"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

# Run dependency checker
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/check_dependencies.py" ]; then
    python3 "$SCRIPT_DIR/check_dependencies.py" --auto
elif [ -f "$APP_DIR/Contents/Resources/check_dependencies.py" ]; then
    python3 "$APP_DIR/Contents/Resources/check_dependencies.py" --auto
else
    echo "⚠️  Dependency checker not found, running manual checks..."

    # Check Ollama
    if ! command -v ollama &> /dev/null; then
        echo ""
        echo "❌ Ollama not found"
        echo "   Install from: https://ollama.ai/download"
        echo ""
        read -p "Open Ollama download page? [y/N]: " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            open "https://ollama.ai/download"
        fi
    else
        echo "✅ Ollama is installed"

        # Check for model
        if ! ollama list | grep -q "llama3.1"; then
            echo ""
            echo "📦 Pulling llama3.1:latest model..."
            ollama pull llama3.1:latest
        else
            echo "✅ Model llama3.1 is available"
        fi
    fi

    # Check Pandoc
    if ! command -v pandoc &> /dev/null; then
        echo ""
        echo "⚠️  Pandoc not found (optional, for PDF export)"
        read -p "Install Pandoc via Homebrew? [y/N]: " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if command -v brew &> /dev/null; then
                brew install pandoc
                echo "✅ Pandoc installed"
            else
                echo "❌ Homebrew not found. Install from: https://brew.sh"
            fi
        fi
    else
        echo "✅ Pandoc is installed"
    fi
fi

echo ""
echo "================================"
echo "✅ Setup complete!"
echo "================================"
echo ""
echo "You can now launch Hrisa Docs from Applications"
echo ""
