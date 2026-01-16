#!/usr/bin/env bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Preparing Repository for Public Release${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: You have uncommitted changes${NC}"
    echo -e "${YELLOW}Please commit or stash your changes first${NC}"
    echo ""
    git status --short
    exit 1
fi

echo -e "${YELLOW}This script will:${NC}"
echo "  1. Create a backup of current history"
echo "  2. Squash all commits into a clean initial release"
echo "  3. Prepare the repository for going public"
echo ""
echo -e "${YELLOW}Current commit history:${NC}"
git log --oneline | head -20
echo ""

# Count commits
COMMIT_COUNT=$(git rev-list --count HEAD)
echo -e "${BLUE}Total commits: ${COMMIT_COUNT}${NC}"
echo ""

# Ask for confirmation
read -p "Do you want to squash these commits into one? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Aborted by user${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Step 1: Creating backup${NC}"

# Create or update backup branch
if git rev-parse --verify backup-pre-public >/dev/null 2>&1; then
    echo -e "${YELLOW}Backup branch 'backup-pre-public' already exists${NC}"
    read -p "Overwrite it? (yes/no): " OVERWRITE
    if [ "$OVERWRITE" = "yes" ]; then
        git branch -D backup-pre-public
        git branch backup-pre-public
        echo -e "${GREEN}✓ Backup updated${NC}"
    else
        echo -e "${YELLOW}Using existing backup${NC}"
    fi
else
    git branch backup-pre-public
    echo -e "${GREEN}✓ Backup created at 'backup-pre-public'${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Creating orphan branch for squash${NC}"

# Create orphan branch
TEMP_BRANCH="clean-public-$(date +%s)"
git checkout --orphan $TEMP_BRANCH

# Add all files
git add -A

echo ""
echo -e "${BLUE}Step 3: Creating commit message${NC}"

# Create comprehensive commit message
cat > /tmp/release_commit_msg.txt << 'EOF'
Initial public release: Hrisa Docs v0.1.0

Desktop application for researchers to consolidate publications into synthesized
books using RAG (Retrieval-Augmented Generation) with local LLMs.

## Features

### Document Processing
- Multi-format support (PDF, DOCX, TXT)
- Automatic text extraction and semantic chunking
- Fast processing (~30s per 100 pages)
- Citation tracking and source references

### AI-Powered Analysis
- Semantic search using vector embeddings
- Automatic theme discovery and clustering
- AI-powered chapter synthesis
- Local LLM integration (Ollama)

### User Experience
- Professional PyQt6 GUI with dark/light themes
- Multi-language support (French, English, Arabic)
- Full keyboard shortcuts
- Multi-project management
- Three accessibility size profiles

### Advanced Features
- Figure and table extraction
- URL import for web articles
- Export to Markdown and DOCX
- Comprehensive documentation

## Technical Stack
- GUI: PyQt6
- Vector DB: ChromaDB
- Embeddings: Sentence Transformers
- LLM: Ollama + LangChain
- PDF Processing: PyMuPDF

## Platforms
- macOS 12.0+ (Universal binary)
- Linux (Ubuntu 22.04+, Debian 11+)
- Windows 10+

## Testing
- 135+ unit and integration tests
- Coverage: 70%+
- Automated CI/CD pipeline

## Documentation
- Complete user guide
- Installation instructions for all platforms
- Troubleshooting guide
- Developer documentation
- 10 application screenshots

## License
MIT License - see LICENSE file

Built with privacy-first principles - all processing happens locally.
EOF

cat /tmp/release_commit_msg.txt
echo ""

read -p "Edit commit message? (yes/no): " EDIT_MSG
if [ "$EDIT_MSG" = "yes" ]; then
    ${EDITOR:-nano} /tmp/release_commit_msg.txt
fi

# Create the squashed commit
echo ""
echo -e "${BLUE}Step 4: Creating squashed commit${NC}"
git commit -F /tmp/release_commit_msg.txt

echo -e "${GREEN}✓ Squashed commit created${NC}"

echo ""
echo -e "${BLUE}Step 5: Replacing main branch${NC}"

# Delete old main and rename
git branch -D main 2>/dev/null || true
git branch -m main

echo -e "${GREEN}✓ Main branch replaced${NC}"

echo ""
echo -e "${BLUE}Step 6: Verification${NC}"

echo ""
echo "New commit history:"
git log --oneline
echo ""

echo "Branch status:"
git branch -a
echo ""

# Show stats
FILES=$(git ls-files | wc -l | tr -d ' ')
SIZE=$(du -sh . 2>/dev/null | cut -f1 || echo "Unknown")

echo -e "${GREEN}Repository Statistics:${NC}"
echo "  Files: $FILES"
echo "  Size: $SIZE"
echo "  Commits: 1 (clean slate)"
echo ""

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Repository prepared for public release!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Next steps:"
echo ""
echo "1. Review the changes:"
echo "   ${BLUE}git log${NC}"
echo "   ${BLUE}git show HEAD${NC}"
echo ""
echo "2. If satisfied, force push to GitHub:"
echo "   ${BLUE}git push -f origin main${NC}"
echo ""
echo "3. Make repository public:"
echo "   ${BLUE}GitHub → Settings → Danger Zone → Make public${NC}"
echo ""
echo "4. Create release:"
echo "   ${BLUE}git tag -a v0.1.0 -F RELEASE_NOTES_v0.1.0.md${NC}"
echo "   ${BLUE}git push origin v0.1.0${NC}"
echo ""
echo "Full history backed up at: ${GREEN}backup-pre-public${NC}"
echo "To restore: ${YELLOW}git checkout backup-pre-public && git branch -D main && git checkout -b main${NC}"
echo ""
