#!/bin/bash
# Install script for Hrisa Docs

set -e

APP_NAME="hrisa-docs"
INSTALL_DIR="/opt/hrisa-docs"
BIN_LINK="/usr/local/bin/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/hrisa-docs.desktop"

echo "Installing Hrisa Docs..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files..."
if [ -d "$APP_NAME" ]; then
    # Old COLLECT mode: directory with executable inside
    cp -r "$APP_NAME"/* "$INSTALL_DIR/"
elif [ -f "$APP_NAME" ]; then
    # New --onefile mode: single executable file
    cp "$APP_NAME" "$INSTALL_DIR/$APP_NAME"
else
    echo "ERROR: $APP_NAME not found (neither file nor directory)"
    exit 1
fi

# Make executable
chmod +x "$INSTALL_DIR/$APP_NAME"

# Create symlink
echo "Creating symlink: $BIN_LINK"
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"

# Install desktop file
if [ -f "hrisa-docs.desktop" ]; then
    # --onefile mode: desktop file in current directory
    echo "Installing desktop file..."
    cp "hrisa-docs.desktop" "$DESKTOP_FILE"
    chmod 644 "$DESKTOP_FILE"

    # Update desktop file to use absolute path
    sed -i "s|Exec=$APP_NAME|Exec=$INSTALL_DIR/$APP_NAME|g" "$DESKTOP_FILE"
elif [ -f "$APP_NAME/hrisa-docs.desktop" ]; then
    # COLLECT mode: desktop file in app directory
    echo "Installing desktop file..."
    cp "$APP_NAME/hrisa-docs.desktop" "$DESKTOP_FILE"
    chmod 644 "$DESKTOP_FILE"

    # Update desktop file to use absolute path
    sed -i "s|Exec=$APP_NAME|Exec=$INSTALL_DIR/$APP_NAME|g" "$DESKTOP_FILE"
fi

# Copy icon if available
if [ -f "../assets/icon.png" ]; then
    echo "Installing icon..."
    mkdir -p /usr/share/icons/hicolor/512x512/apps
    cp ../assets/icon.png /usr/share/icons/hicolor/512x512/apps/hrisa-docs.png
fi

echo ""
echo "Installation complete!"
echo ""

# Check dependencies
echo "================================"
echo "Checking dependencies..."
echo "================================"
echo ""

# Check curl (needed for Ollama installation)
if ! command -v curl &> /dev/null; then
    echo "❌ curl not found (required for Ollama installation)"
    read -p "Install curl? [y/N]: " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y curl
        elif command -v yum &> /dev/null; then
            yum install -y curl
        else
            echo "⚠️  Could not install curl automatically"
            echo "   Install manually: sudo apt install curl"
        fi
    fi
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found (required)"
    if command -v curl &> /dev/null; then
        echo "   Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh

        if command -v ollama &> /dev/null; then
            echo "✅ Ollama installed successfully"
        else
            echo "⚠️  Ollama installation failed"
            echo "   Install manually: curl -fsSL https://ollama.ai/install.sh | sh"
        fi
    else
        echo "⚠️  Cannot install Ollama: curl is not available"
        echo "   Install curl first: sudo apt install curl"
        echo "   Then install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    fi
else
    echo "✅ Ollama is installed"
fi

# Pull required model
if command -v ollama &> /dev/null; then
    if ! ollama list | grep -q "llama3.1"; then
        echo ""
        echo "📦 Pulling llama3.1:latest model (this may take a few minutes)..."
        ollama pull llama3.1:latest
        echo "✅ Model downloaded"
    else
        echo "✅ Model llama3.1 is available"
    fi
fi

# Check Pandoc
if ! command -v pandoc &> /dev/null; then
    echo ""
    echo "⚠️  Pandoc not found (optional, for PDF export)"
    read -p "Install Pandoc? [y/N]: " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Try apt-get first
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y pandoc
        elif command -v yum &> /dev/null; then
            yum install -y pandoc
        else
            echo "⚠️  Could not install Pandoc automatically"
            echo "   Install manually: https://pandoc.org/installing.html"
        fi
    fi
else
    echo "✅ Pandoc is installed"
fi

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "Run 'hrisa-docs' from terminal or find 'Hrisa Docs' in your applications menu."
