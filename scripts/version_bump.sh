#!/bin/bash
# Version management script for Hrisa Docs
# Bumps version and updates all relevant files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get current version from pyproject.toml
get_current_version() {
    grep '^version = ' pyproject.toml | cut -d'"' -f2
}

# Bump version
bump_version() {
    local current_version=$1
    local bump_type=$2

    IFS='.' read -r major minor patch <<< "$current_version"

    case "$bump_type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Invalid bump type: $bump_type"
            echo "Usage: $0 [major|minor|patch] or $0 <version>"
            exit 1
            ;;
    esac

    echo "$major.$minor.$patch"
}

# Update version in files
update_version() {
    local new_version=$1

    echo -e "${BLUE}[INFO]${NC} Updating version to $new_version..."

    # Update pyproject.toml
    sed -i.bak "s/^version = .*/version = \"$new_version\"/" pyproject.toml
    rm -f pyproject.toml.bak
    echo "  ✓ Updated pyproject.toml"

    # Update build scripts
    for script in scripts/build_macos.py scripts/build_linux.py scripts/build_windows.py; do
        if [ -f "$script" ]; then
            sed -i.bak "s/APP_VERSION = .*/APP_VERSION = \"$new_version\"/" "$script"
            rm -f "${script}.bak"
            echo "  ✓ Updated $script"
        fi
    done

    # Update Dockerfiles if they contain version
    for dockerfile in Dockerfile.ubuntu Dockerfile.windows; do
        if [ -f "$dockerfile" ] && grep -q "0.1.0" "$dockerfile"; then
            sed -i.bak "s/0\.1\.0/$new_version/g" "$dockerfile"
            rm -f "${dockerfile}.bak"
            echo "  ✓ Updated $dockerfile"
        fi
    done

    echo -e "${GREEN}[SUCCESS]${NC} Version updated to $new_version"
}

# Create git tag
create_tag() {
    local version=$1

    echo ""
    read -p "Create git tag v$version? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "Bump version to $version" || true
        git tag -a "v$version" -m "Release v$version"
        echo -e "${GREEN}[SUCCESS]${NC} Created tag v$version"
        echo ""
        echo "To push the tag:"
        echo "  git push origin v$version"
    fi
}

# Main
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║  Hrisa Docs - Version Management      ║"
    echo "╚════════════════════════════════════════╝"
    echo ""

    CURRENT_VERSION=$(get_current_version)
    echo "Current version: $CURRENT_VERSION"
    echo ""

    if [ $# -eq 0 ]; then
        echo "Usage:"
        echo "  $0 major       # Bump major version (1.0.0 -> 2.0.0)"
        echo "  $0 minor       # Bump minor version (0.1.0 -> 0.2.0)"
        echo "  $0 patch       # Bump patch version (0.1.0 -> 0.1.1)"
        echo "  $0 1.2.3       # Set specific version"
        exit 0
    fi

    # Determine new version
    if [[ $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        NEW_VERSION=$1
    else
        NEW_VERSION=$(bump_version "$CURRENT_VERSION" "$1")
    fi

    echo "New version: $NEW_VERSION"
    echo ""

    read -p "Proceed with version bump? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 0
    fi

    update_version "$NEW_VERSION"
    create_tag "$NEW_VERSION"

    echo ""
    echo -e "${GREEN}[SUCCESS]${NC} Version bump completed!"
}

main "$@"
