# Changelog

All notable changes to Hrisa Docs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-11

### ✨ Features

- Add installation instructions and improve build scripts (`9aef504`)
- Add Docker-based cross-platform build system (`b6cbe6b`)
- Add Linux build support with Docker (`f7d0168`)
- Add context-aware error messages with troubleshooting guidance (`38a632b`)
- Add project management improvements with duplicate/rename/bulk operations (`6f62a14`)
- Add Quick Wins UI improvements for better UX (`1ecaf86`)
- Integrate official Hrisa Docs logo into build pipeline (`deb0301`)
- Add 13 AI-generated logo concepts from Bing Image Creator (`897bb42`)
- Add initial logo/icon concept mockups (`dfd0c7e`)
- Update File menu with 'Import' and 'Open File' options (`1a0f1c9`)
- Reorganize menu bar with new Project menu (`8eed4a2`)
- Add make build command for macOS app bundling (`da19a95`)
- Complete GUI appearance system and remove all emojis (`9eec9c7`)
- Add multi-selection and delete all for generated documents (`7b02c3c`)
- Add URL import feature with polished UI (`09ee373`)
- Implement URL Import Task for web content fetching (`25bcc9a`)
- Integrate SummarizationTask with existing synthesis engine (`d15f20a`)
- Add project management GUI components (`f39d536`)
- Add multi-project support and task caching system (`fd48971`)
- Add 'make reset' command for testing (`3e77c3a`)
- Add figure extraction feature with CSV export and comprehensive testing (`555f8f2`)
- Add PDF export functionality to GUI (`f976cbd`)
- Add comprehensive GUI testing guide (`653b0c9`)
- Add comprehensive manual test script (`88139a8`)
- Add comprehensive test suite with 80+ passing tests (`a76161f`)

### 🐛 Bug Fixes

- Fix architecture diagram formatting (`641221d`)
- Add proper padding to icon so it matches size of other macOS apps (`c9494bf`)
- Create proper macOS-style icon with transparent corners (`3908c57`)
- Remove white background from icon, make transparent (`73108ed`)
- Correct icon path variable formatting in build scripts (`134caca`)
- Correct import order in test_full_workflow.py (`5841fad`)
- Windows version info encoding error (`eb506b0`)
- Windows build Unicode escape error in spec file (`93cae2f`)
- Replace Unicode checkmarks with ASCII for Windows compatibility (`7fb5e95`)
- Format code and configure linter for CI/CD (`52410b4`)
- Remove non-existent CLI entry point causing build failures (`9b76b0a`)
- Make 'New Project' menu item directly open creation dialog (`46841c6`)
- Add xelatex detection in common TeX Live locations (`661f26c`)
- Add granular progress updates during synthesis initialization (`427cb36`)
- PDF export format not working properly (`d4d85d0`)
- Use settings paths in GUI widgets and project manager (`a403740`)
- Use PyInstaller-compatible paths for data directories (`44f3817`)
- Use PyInstaller-compatible resource path for prompts.yaml (`eb9768f`)
- Include prompts.yaml file in packaged application (`dd43269`)
- Add comprehensive ChromaDB modules to hidden imports (`d28d54d`)
- Add ChromaDB telemetry modules to hidden imports (`f286107`)
- Correct entry point path in macOS build script (`b1a8111`)
- Connect click handler for 'Update selected figures' button (`3c96f52`)
- Allow .txt, .docx, and .pdf files in document picker (`9872d8b`)
- Update test suite for refactored codebase (35 → 0 failures) (`b674c35`)
- Emit documents_changed signal when project is loaded (`a48167f`)
- Enable figure extraction button when documents are loaded (`0e3f78b`)
- Internationalize Figure Extraction widget UI (`3eed8c2`)
- Fix SynthesisEngine method name: synthesize_chapter -> generate_chapter (`18bbd88`)
- Fix merge bugs: language preservation and percentage calculation (`059ad07`)
- Fix Ollama model name: llama3 -> llama3.1:latest (`29ecf71`)
- Fix ThemeAnalyzer API - vector_store is required parameter (`abcb141`)
- Fix GUI workers API mismatches (`04bc406`)

### 📚 Documentation

- Add comprehensive alpha testing guide and update documentation (`0ea2860`)
- Add comprehensive DIY icon creation guide (`6bba27b`)
- Add comprehensive troubleshooting guide (`39803dd`)
- Add logo integration completion summary (`6ac4567`)
- Add Ubuntu/Linux native package to future roadmap (`a21eba3`)
- Add CLI and web version to future roadmap (`ac790ca`)
- Add rebrand summary document (`43c0fd5`)
- Add CI/CD setup summary and status (`d09dbfb`)
- Add comprehensive documentation for users and developers (`5684af2`)
- Improve cache validation docstring (`c3c71ca`)
- Add comprehensive project documentation (`707ce53`)
- Add comprehensive user documentation and packaging scripts (`1a48404`)
- Add comprehensive project documentation (`b525223`)
- Add testing reset guide (`e6fee93`)

### ♻️ Refactoring

- Update widgets for multi-project support (`f33c435`)

### ✅ Tests

- Add 5 integration tests for new project management workflows (`1bba677`)
- Add comprehensive tests for new project management features (`55e0779`)
- Fix test failures for CI/CD (`9b59b8f`)
- Add comprehensive unit and integration test suite (`255018f`)
- Add manual test script for URL Import Task (`33293c0`)
- Add comprehensive E2E tests for multi-project workflow (`4a3d5a6`)
- Add tests for multi-project system (`a76d490`)

### 🔧 Chores

- Remove .DS_Store from repository (`d16f973`)
- Update .gitignore for macOS and test files (`4aea99e`)

### Other Changes

- Implement local CI/CD pipeline as GitHub Actions fallback (`2426151`)
- Document Windows build options and limitations (`f8cfc77`)
- : Remove padding from icon, return to working version (`94b4417`)
- : Simplified icon to cleaner chili design (still needs manual refinement) (`9baf6f9`)
- : Add visual branding documentation and reference images (`531535d`)
- : Fix Windows build and test marker errors (`d4a8f46`)
- : Fix test failures in GitHub Actions (`adb8ece`)
- : Rename project from 'Document Processor' to 'Hrisa Docs' (`35c2244`)
- : Add GitHub Actions workflow and Windows build documentation (`747660d`)
- : Add release preparation script (`64223ef`)
- : Add release readiness check script (`313fce3`)
- : Make URL dialog fully consistent with dark theme (`3672d4f`)
- : Apply dark theme to URL import dialog (`a6884c7`)
- Implement language management system (FR/EN/AR) (`b3f88ba`)
- Implement smart merge with validation and LLM label generation (`1ab572a`)
- Implement theme merge functionality (`d4e703f`)
- Enable multi-selection in theme list widget (`dda1d32`)
- Wire up backend to GUI with worker threads (`cbac9b9`)
- Implement GUI widgets and integrate into main window (`e056610`)
- Make all prompts language-agnostic (no hardcoded languages) (`19aee33`)
- Complete Phase 5: Synthesis Engine with Language Detection (`1708547`)


---

**Legend:**
- ✨ Features: New functionality
- 🐛 Bug Fixes: Bugs that were fixed
- 🔄 Changes: Updates to existing features
- 📚 Documentation: Documentation improvements
- ♻️ Refactoring: Code improvements without changing functionality
- 🗑️ Removals: Deprecated or removed features
- ✅ Tests: Test additions or improvements
- 🔧 Chores: Maintenance tasks
