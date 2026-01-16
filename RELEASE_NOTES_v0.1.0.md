# Hrisa Docs v0.1.0 - First Public Release

**Release Date**: January 14, 2026
**Pre-release**: No

---

## 🎯 What's New

The first public release of **Hrisa Docs** - a powerful desktop application that helps researchers consolidate publications into synthesized books using RAG (Retrieval-Augmented Generation) with local LLMs.

This release includes the complete **Phase 2: Search & Import** feature, a comprehensive document discovery system that lets you search and import documents directly from Tunisian government websites, legal databases, and open data portals.

## ✨ New Features

### 🔍 Search & Import from Research Sources

Search for documents across multiple sources using keywords and automatically import relevant results into your project.

**Supported Sources**:
- **data.gov.tn** - Tunisian Open Data Portal (native CKAN API)
- **finances.gov.tn** - Ministry of Finance
- **jibaya.tn** - Tax Documentation
- **iort.gov.tn** - Official Gazette
- **ins.tn** - Statistics Institute
- **arp.tn** - Assembly Laws
- Plus any website via Google Custom Search API fallback

**Key Capabilities**:
- **Keyword Search**: Enter queries like "BEPS transfer pricing" or "circular economy"
- **Multi-Source Search**: Search multiple sources simultaneously
- **Smart Handler System**: Native API integration (CKAN) with Google fallback
- **Result Preview**: Review titles, snippets, and source before importing
- **Batch Import**: Select multiple documents to import at once
- **File Type Filtering**: Automatically handles PDF, HTML, and DOCX files

### 🔐 Secure Credential Storage

- **OS Keyring Integration**: Credentials stored securely in Windows Credential Manager (Windows), Keychain (macOS)
- **Remember Credentials**: Optional checkbox to save API keys across sessions
- **One-Click Clear**: Remove saved credentials with confirmation dialog
- **Auto-Load**: Credentials auto-populate when dialog opens

### 📜 Search History

- **Recent Searches**: See your last 20 searches with query, results count, and timestamp
- **Click to Repeat**: Click any history entry to re-run the search
- **Context Menu**: Right-click to remove individual entries
- **Clear All**: Button to clear entire history
- **Persistent Storage**: History saved in user preferences

### 🌳 Advanced Result Organization

- **Grouped by Source**: Results organized in collapsible tree by domain
- **Batch Selection**: Check parent node to select all results from a source
- **Handler Indicators**: Color-coded badges show which search method was used:
  - 🔍 **CKAN** (green) - Native API search
  - 🔎 **Google** (blue) - Google Custom Search fallback
- **Sort by Relevance**: Results sorted by result count per source

### ⚙️ Search Strategies

Choose how to search sources:
- **Auto (Recommended)**: Try native API first, fall back to Google if needed
- **Native Only**: Use only native handlers (e.g., CKAN for data.gov.tn)
- **Google Only**: Use Google Custom Search for all sources

### 🎨 User Experience Improvements

- **Bilingual Interface**: All new features fully translated (French/English)
- **Keyboard Shortcut**: Ctrl+Shift+S (Cmd+Shift+S on macOS) to open search dialog
- **Theme Support**: Search dialog respects dark/light theme settings
- **Responsive UI**: Dialog adapts to different screen sizes
- **Progress Feedback**: Real-time status updates during search

## 📥 Downloads

### macOS
**File**: `HrisaDocs-0.1.0-macOS.dmg` (~280 MB)
**Requirements**: macOS 12.0 (Monterey) or later
**Architecture**: Universal (Apple Silicon + Intel)

**Installation**:
1. Download the DMG file
2. Double-click to mount
3. Drag "Hrisa Docs.app" to Applications folder
4. First launch: Right-click → Open (to bypass Gatekeeper)

### Windows
**File**: `HrisaDocs-0.1.0-Setup.exe` (~200 MB)
**Requirements**: Windows 10/11 (64-bit)

**Installation**:
1. Download the installer
2. Run `HrisaDocs-0.1.0-Setup.exe`
3. Follow installation wizard
4. Launch from Start Menu or Desktop shortcut

**Note**: First launch may be slow as Windows Defender scans the file.

### Linux (Ubuntu/Debian)
**File**: `hrisa-docs-0.1.0-linux-x86_64.tar.gz` (~360 MB)
**Requirements**: Ubuntu 22.04+, Debian 11+, or compatible glibc

**Installation**:
```bash
tar -xzf hrisa-docs-0.1.0-linux-x86_64.tar.gz
cd hrisa-docs
sudo ./install.sh  # Optional: installs to /opt with desktop entry
./hrisa-docs       # Or run directly
```

## 🔧 Prerequisites

**Ollama** is required for LLM integration:

```bash
# Install Ollama from https://ollama.ai/download
ollama pull llama3.1:latest
```

**Optional**: Google Custom Search API credentials for broader source coverage:
1. Go to https://console.cloud.google.com/
2. Enable "Custom Search API"
3. Create API key
4. Create search engine at https://programmablesearchengine.google.com/

## 🐛 Bug Fixes

- **Windows Build**: Fixed PyInstaller packaging to include all required modules
- **ChromaDB**: Resolved tkinter conflict causing startup crashes
- **User Preferences**: Fixed file path resolution in packaged builds
- **Theme Colors**: Fixed text visibility issues in tree widget on dark theme
- **Dialog Layout**: Increased search dialog height to show all UI elements

## 🛠️ Technical Improvements

### Dependencies Added
- `keyring>=24.0.0` - OS-level secure credential storage
- `requests>=2.28.0` - HTTP requests for web scraping
- `beautifulsoup4>=4.11.0` - HTML parsing
- `google-api-python-client>=2.0.0` - Google Custom Search integration

### Architecture
- **Handler Pattern**: Pluggable search handler system with base class
- **Singleton Managers**: CredentialsManager and UserPreferencesManager
- **FIFO Queue**: Search history with automatic 20-entry limit
- **Worker Threads**: Background search and import operations
- **Result Caching**: De-duplication by URL to avoid duplicates

### Files Added
```
src/docprocessor/core/tasks/search_import_task.py
src/docprocessor/core/tasks/search_handlers/
├── __init__.py
├── base_handler.py
├── google_handler.py
└── ckan_handler.py
src/docprocessor/gui/dialogs/search_import_dialog.py
src/docprocessor/utils/credentials_manager.py
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)**: Get started in 5 minutes
- **[User Guide](docs/USER_GUIDE.md)**: Complete feature documentation
- **[Installation Guide](docs/INSTALLATION.md)**: Detailed installation instructions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Common issues and solutions

## 🚀 Performance

Search performance (tested on M1 MacBook Pro, 16GB RAM):

| Operation | Speed |
|-----------|-------|
| CKAN API Search | <2 seconds for 10 results |
| Google Search | 2-5 seconds for 10 results |
| PDF Download | 1-5 seconds depending on size |
| Result Display | Instant (tree rendering) |

**Typical Workflow**:
1. Enter search query: <1 second
2. Search 3 sources: 5-10 seconds
3. Review 20 results: User time
4. Import 5 PDFs: 10-30 seconds

## 🔮 Roadmap

### Planned for v0.2.0
- **OCR Support**: Process scanned PDFs with OCR
- **Citation Export**: BibTeX and RIS format export
- **Advanced Filters**: Filter results by date, file size, source type
- **Saved Searches**: Save frequently used queries

### Future Enhancements
- Additional native handlers for more Tunisian sources
- Automatic document classification
- Duplicate detection before import
- Scheduled searches with notifications
- Export search results to CSV

## 💬 Feedback

Please report issues or suggestions via:
- **GitHub Issues**: https://github.com/yourusername/Document-Processing/issues
- **Include**: Application version, OS version, and log files
- **Logs**: `~/.docprocessor/logs/docprocessor.log` (macOS/Linux) or `%USERPROFILE%\.docprocessor\logs\` (Windows)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [Keyring](https://github.com/jaraco/keyring) - Secure credential storage
- [Google Custom Search API](https://developers.google.com/custom-search) - Web search
- [CKAN API](https://docs.ckan.org/en/latest/api/) - Open data access

---

**Made with 🤖 for Researchers**

Discover, import, and synthesize research documents automatically.
