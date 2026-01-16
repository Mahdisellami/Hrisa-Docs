# Screenshot Guide for Hrisa Docs

This guide will help you capture the right screenshots for the README.

## Screenshots Needed (5-7 total)

### 1. Main Window - Project Dashboard
**File name**: `01-main-window.png`
**What to show**: 
- Main window with project list
- Show at least 2-3 projects
- Make sure window is reasonably sized (not full screen)
**How**: 
- Open app, go to project dashboard
- Press `Cmd+Shift+4` on macOS, then Space, then click window

### 2. Document Management Tab
**File name**: `02-documents-tab.png`
**What to show**:
- Source Documents tab active
- List of imported PDFs (5-10 documents)
- Document metadata visible (title, pages, size)
**How**:
- Open a project
- Go to "Source Documents" tab
- Press `Cmd+Shift+4`, select area

### 3. Processing in Progress
**File name**: `03-processing.png`
**What to show**:
- Documents being processed
- Progress bar visible
- Status messages
**How**:
- Start processing documents
- Quickly capture while processing
- Press `Cmd+Shift+4`, select area

### 4. Themes Tab
**File name**: `04-themes-tab.png`
**What to show**:
- Discovered themes list
- Theme details (label, document count, keywords)
- Theme management buttons
**How**:
- After theme discovery completes
- Go to "Themes" tab
- Press `Cmd+Shift+4`, select area

### 5. Synthesis Tab
**File name**: `05-synthesis-tab.png`
**What to show**:
- Synthesis configuration
- Chapter list or preview
- Export options
**How**:
- Go to "Synthesis" tab
- Show the synthesis interface
- Press `Cmd+Shift+4`, select area

### 6. Settings Window (Optional)
**File name**: `06-settings.png`
**What to show**:
- Settings dialog with tabs
- Show appearance or system settings
**How**:
- Open Settings (Cmd+,)
- Press `Cmd+Shift+4`, select area

### 7. Dark Mode (Optional)
**File name**: `07-dark-mode.png`
**What to show**:
- Any main view in dark mode
- Shows theme support
**How**:
- Switch to dark mode in settings
- Take any of the above screenshots
- Press `Cmd+Shift+4`, select area

## Screenshot Tips

### Quality
- **Resolution**: Take at 2x resolution (Retina) but they'll be displayed smaller
- **Size**: Aim for 1200-1600px width
- **Format**: PNG (not JPEG) for crisp text

### Content
- **Clean data**: Use realistic but clean sample data
- **No personal info**: Avoid real document titles if sensitive
- **Good lighting**: Use light mode for consistency (unless showing dark mode)
- **Proper window size**: Not too small, not full screen (~1400x900 window)

### Composition
- **Show full window**: Include title bar and all UI elements
- **Center content**: Make sure key features are visible
- **Avoid clutter**: Close unnecessary dialogs/notifications

## macOS Screenshot Commands

```bash
# Capture entire window (includes shadow)
Cmd+Shift+4, then Space, then click window

# Capture selected area
Cmd+Shift+4, then drag to select

# Capture entire screen
Cmd+Shift+3

# Screenshots save to: ~/Desktop by default
```

## After Taking Screenshots

1. **Rename files** according to the guide above
2. **Move to repository**:
   ```bash
   mv ~/Desktop/01-main-window.png docs/screenshots/
   mv ~/Desktop/02-documents-tab.png docs/screenshots/
   # ... etc
   ```

3. **Optimize file sizes** (optional):
   ```bash
   # Install imageoptim (if not already)
   brew install --cask imageoptim
   
   # Optimize all screenshots
   open -a ImageOptim docs/screenshots/*.png
   ```

4. **Commit to repository**:
   ```bash
   git add docs/screenshots/
   git commit -m "docs: Add application screenshots"
   ```

## Checklist

Before starting:
- [ ] Clean up test data (use realistic sample projects/documents)
- [ ] Check app theme (light mode recommended for main screenshots)
- [ ] Close unnecessary windows/notifications
- [ ] Prepare sample PDFs if needed

During screenshot capture:
- [ ] 01-main-window.png - Project dashboard
- [ ] 02-documents-tab.png - Document list
- [ ] 03-processing.png - Processing in progress
- [ ] 04-themes-tab.png - Theme discovery
- [ ] 05-synthesis-tab.png - Synthesis interface
- [ ] 06-settings.png (optional) - Settings dialog
- [ ] 07-dark-mode.png (optional) - Dark theme

After capture:
- [ ] Rename files correctly
- [ ] Move to docs/screenshots/
- [ ] Check file sizes (< 500KB each ideally)
- [ ] Optimize if needed
- [ ] Add to git

## Example README Section

Once screenshots are ready, I'll add this to README:

```markdown
## Screenshots

### Project Dashboard
![Project Dashboard](docs/screenshots/01-main-window.png)

### Document Management
![Document Management](docs/screenshots/02-documents-tab.png)

### Theme Discovery
![Themes](docs/screenshots/04-themes-tab.png)

### Synthesis
![Synthesis](docs/screenshots/05-synthesis-tab.png)
```

---

**Ready?** Follow the checklist above and let me know when screenshots are ready!
