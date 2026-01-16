#!/bin/bash
# Prepare a new release

set -e  # Exit on error

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/prepare_release.sh <version>"
    echo "Example: ./scripts/prepare_release.sh 0.2.0"
    exit 1
fi

echo "============================================================"
echo "Preparing release $VERSION"
echo "============================================================"

# Update version in pyproject.toml
echo "Updating pyproject.toml..."
sed -i.bak "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Update version in build scripts
echo "Updating build_macos.py..."
sed -i.bak "s/APP_VERSION = \".*\"/APP_VERSION = \"$VERSION\"/" scripts/build_macos.py
rm scripts/build_macos.py.bak

echo "Updating build_windows.py..."
sed -i.bak "s/APP_VERSION = \".*\"/APP_VERSION = \"$VERSION\"/" scripts/build_windows.py
rm scripts/build_windows.py.bak

# Update CHANGELOG
echo "Updating CHANGELOG.md..."
DATE=$(date +%Y-%m-%d)
sed -i.bak "s/## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $DATE/" CHANGELOG.md
rm CHANGELOG.md.bak

echo ""
echo "Version updated to $VERSION"
echo ""
echo "Next steps:"
echo "1. Update CHANGELOG.md with changes for this release"
echo "2. Review changes: git diff"
echo "3. Commit: git commit -am \"chore: Prepare release $VERSION\""
echo "4. Tag: git tag -a v$VERSION -m \"Release $VERSION\""
echo "5. Run: python scripts/check_release_ready.py"
echo "6. Build distributions if ready"
echo "7. Push: git push && git push --tags"
