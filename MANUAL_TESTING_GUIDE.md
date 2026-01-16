# Manual UI Testing Guide - Multi-Project Feature

This guide provides comprehensive manual test cases for the new multi-project functionality.

## Prerequisites

1. Start the application:
   ```bash
   .venv/bin/python -m docprocessor.gui.main
   ```

2. Prepare test documents (PDFs) in advance

---

## Test Suite 1: Project Dashboard

### Test 1.1: First Launch
**Expected**: Project Dashboard should appear automatically on first launch

**Steps**:
1. Launch application for the first time
2. Verify "Projects Dashboard" dialog appears
3. Verify "New Project" button is visible
4. Verify search box is present
5. Verify no projects are listed initially

**Pass Criteria**:
- ✅ Dashboard appears without error
- ✅ UI is clean and responsive
- ✅ All controls are visible

---

### Test 1.2: Create New Project
**Steps**:
1. Click "New Project" button
2. Enter project name: "Test Project 1"
3. Enter description: "Testing project creation"
4. Select template: "Default"
5. Check "Mark as favorite"
6. Click OK

**Pass Criteria**:
- ✅ Project appears in dashboard
- ✅ Star icon shows it's favorited
- ✅ Dashboard closes automatically
- ✅ Main window shows project name in header
- ✅ Status bar shows "0 docs, 0 themes, 0 tasks"

---

### Test 1.3: Create Multiple Projects
**Steps**:
1. Click "Manage Projects" in project bar
2. Create "Research Project" (Academic template)
3. Create "Legal Analysis" (Legal template)
4. Create "Creative Writing" (Creative template)
5. Verify all 4 projects appear in list

**Pass Criteria**:
- ✅ All projects created successfully
- ✅ Each project shows correct template icon/label
- ✅ Projects sorted by creation date

---

### Test 1.4: Search Projects
**Steps**:
1. Open Project Dashboard
2. Type "Test" in search box
3. Verify only "Test Project 1" appears
4. Clear search
5. Type "Research"
6. Verify only "Research Project" appears

**Pass Criteria**:
- ✅ Search filters projects correctly
- ✅ Search is case-insensitive
- ✅ Clearing search shows all projects

---

### Test 1.5: Filter Projects
**Steps**:
1. Open Project Dashboard
2. Click "Favorites" filter
3. Verify only favorited projects appear
4. Click "All Projects"
5. Verify all projects appear

**Pass Criteria**:
- ✅ Filters work correctly
- ✅ UI updates immediately

---

## Test Suite 2: Project Switching

### Test 2.1: Switch Between Projects
**Steps**:
1. Select "Test Project 1" (should already be active)
2. Note the window title
3. Click "Manage Projects"
4. Select "Research Project"
5. Note window title changes
6. Verify project name in header changed

**Pass Criteria**:
- ✅ Window title updates to show project name
- ✅ Project name in switcher bar updates
- ✅ Status bar shows correct project stats
- ✅ No errors or crashes

---

### Test 2.2: Last Project Persistence
**Steps**:
1. Switch to "Legal Analysis" project
2. Close application
3. Relaunch application
4. Verify "Legal Analysis" loads automatically

**Pass Criteria**:
- ✅ Last project loads on startup
- ✅ All project data intact
- ✅ No dashboard appears (went straight to project)

---

## Test Suite 3: Document Management

### Test 3.1: Add Documents to Project
**Steps**:
1. Ensure you're in "Test Project 1"
2. Click Files tab
3. Click "Add" button
4. Select 2-3 PDF files
5. Verify documents appear in list
6. Note file sizes shown

**Pass Criteria**:
- ✅ Documents appear in list
- ✅ File names and sizes displayed correctly
- ✅ "Process" button becomes enabled
- ✅ Document count updates in status bar

---

### Test 3.2: Documents Persist Per Project
**Steps**:
1. In "Test Project 1", add 2 documents
2. Switch to "Research Project"
3. Verify no documents in list
4. Add 3 different documents
5. Switch back to "Test Project 1"
6. Verify original 2 documents still there
7. Switch to "Research Project"
8. Verify 3 documents still there

**Pass Criteria**:
- ✅ Each project maintains its own document list
- ✅ Documents don't mix between projects
- ✅ Switching is smooth and fast

---

### Test 3.3: Remove Documents
**Steps**:
1. In current project, select 1 document
2. Click "Remove" button
3. Verify document removed
4. Verify count updates
5. Switch to another project and back
6. Verify removal persisted

**Pass Criteria**:
- ✅ Document removed from list
- ✅ Count updated
- ✅ Change persists across project switches

---

### Test 3.4: Clear All Documents
**Steps**:
1. Add 3 documents to project
2. Click "Clear All"
3. Verify all documents removed
4. Switch projects and back
5. Verify still cleared

**Pass Criteria**:
- ✅ All documents removed
- ✅ "Process" button disabled
- ✅ Persists correctly

---

## Test Suite 4: Project Settings

### Test 4.1: Open Project Settings
**Steps**:
1. Click "⚙️ Project Settings" in project bar
2. Verify settings dialog opens
3. Verify all sections present:
   - Project Information
   - Language Model Settings
   - Processing Settings
   - Output Settings

**Pass Criteria**:
- ✅ Dialog opens without error
- ✅ All sections visible
- ✅ All fields populated with current values

---

### Test 4.2: Modify Project Information
**Steps**:
1. Open Project Settings
2. Change project name to "Test Project 1 - Modified"
3. Add author: "Your Name"
4. Add tags: "test, demo, example"
5. Click OK
6. Verify project name updated in header
7. Open settings again
8. Verify all changes saved

**Pass Criteria**:
- ✅ All changes saved
- ✅ UI updated immediately
- ✅ Changes persist after dialog close

---

### Test 4.3: Modify LLM Settings
**Steps**:
1. Open Project Settings
2. Change Language to: "en"
3. Change LLM Model to: "llama2:latest"
4. Change Temperature to: 0.8
5. Click OK
6. Reopen settings
7. Verify all changes saved

**Pass Criteria**:
- ✅ Settings saved correctly
- ✅ Each field shows updated value

---

### Test 4.4: Modify Processing Settings
**Steps**:
1. Open Project Settings
2. Set Chunk Size: 800
3. Set Chunk Overlap: 150
4. Click OK
5. Verify saved (reopen to check)

**Pass Criteria**:
- ✅ Numeric settings saved correctly

---

### Test 4.5: Modify Output Settings
**Steps**:
1. Open Project Settings
2. Change Output Format to: "docx"
3. Check "Include Citations"
4. Change Citation Style to: "APA"
5. Click OK
6. Verify saved

**Pass Criteria**:
- ✅ Dropdown changes saved
- ✅ Checkbox state saved
- ✅ All persist correctly

---

### Test 4.6: Settings Per Project
**Steps**:
1. In "Test Project 1": Set language to "en", model to "llama2"
2. Switch to "Research Project"
3. Open settings, verify language is "fr" (default)
4. Set language to "ar", model to "mistral"
5. Switch back to "Test Project 1"
6. Open settings, verify still "en" and "llama2"
7. Switch to "Research Project"
8. Verify still "ar" and "mistral"

**Pass Criteria**:
- ✅ Each project maintains independent settings
- ✅ Settings don't interfere with each other
- ✅ All persist correctly

---

### Test 4.7: Cancel Settings Changes
**Steps**:
1. Open Project Settings
2. Change several fields
3. Click Cancel (X or Cancel button)
4. Reopen settings
5. Verify changes were NOT saved

**Pass Criteria**:
- ✅ Cancel works correctly
- ✅ No changes persist

---

## Test Suite 5: Project Management Operations

### Test 5.1: Favorite/Unfavorite Projects
**Steps**:
1. Open Project Dashboard
2. Click star icon on "Research Project" to favorite
3. Verify star becomes filled
4. Click "Favorites" filter
5. Verify project appears
6. Click star again to unfavorite
7. Verify star becomes empty
8. Refresh filter
9. Verify project no longer in Favorites

**Pass Criteria**:
- ✅ Favorite toggle works
- ✅ Filter updates correctly
- ✅ Visual feedback is clear

---

### Test 5.2: Archive Project
**Steps**:
1. Open Project Dashboard
2. Right-click "Creative Writing" project (or use menu)
3. Click "Archive"
4. Verify project disappears from active list
5. Click "Archived" filter
6. Verify project appears in archived list

**Pass Criteria**:
- ✅ Project archived successfully
- ✅ Appears in archived filter
- ✅ Not in active projects

---

### Test 5.3: Restore Archived Project
**Steps**:
1. Click "Archived" filter
2. Select archived project
3. Click "Restore" (or context menu)
4. Click "All Projects"
5. Verify project back in active list

**Pass Criteria**:
- ✅ Restoration works
- ✅ Project back in active list
- ✅ All data intact

---

### Test 5.4: Delete Project Permanently
**Steps**:
1. Create a temporary test project
2. Open Project Dashboard
3. Right-click project
4. Click "Delete Permanently"
5. Confirm deletion
6. Verify project removed completely

**Pass Criteria**:
- ✅ Confirmation dialog appears
- ✅ Project deleted
- ✅ Cannot be recovered

---

## Test Suite 6: Multi-Language Support

### Test 6.1: French Interface
**Steps**:
1. If app has language switcher, set to French
2. Verify all labels translated:
   - Project Dashboard
   - Button labels
   - Dialog titles
   - Status messages

**Pass Criteria**:
- ✅ All UI elements in French
- ✅ No English text showing
- ✅ Layout looks correct

---

### Test 6.2: Arabic Interface (RTL)
**Steps**:
1. Switch to Arabic
2. Verify UI mirrors for RTL
3. Verify all text in Arabic
4. Verify layout is correct

**Pass Criteria**:
- ✅ RTL layout works
- ✅ All text translated
- ✅ No layout issues

---

## Test Suite 7: Integration Tests

### Test 7.1: Complete Workflow
**Steps**:
1. Create new project "Integration Test"
2. Add 3 PDF documents
3. Change project settings (language, model)
4. Switch to different project
5. Switch back to "Integration Test"
6. Verify all data intact:
   - Documents still there
   - Settings unchanged
   - Project info correct
7. Close and reopen app
8. Verify project loads correctly

**Pass Criteria**:
- ✅ All operations successful
- ✅ No data loss
- ✅ Everything persists

---

### Test 7.2: Rapid Project Switching
**Steps**:
1. Switch between 5 different projects rapidly
2. Verify each loads correctly
3. Verify no errors or crashes
4. Verify UI updates properly

**Pass Criteria**:
- ✅ No crashes
- ✅ Smooth switching
- ✅ Correct data for each project

---

### Test 7.3: Project with Many Documents
**Steps**:
1. Create project
2. Add 20+ documents
3. Verify all load correctly
4. Remove some documents
5. Add more documents
6. Switch projects and back
7. Verify all operations work smoothly

**Pass Criteria**:
- ✅ Handles many documents
- ✅ No performance issues
- ✅ All operations work

---

## Test Suite 8: Error Handling

### Test 8.1: Invalid Project Name
**Steps**:
1. Try to create project with empty name
2. Verify error message appears
3. Try with special characters only
4. Verify handled correctly

**Pass Criteria**:
- ✅ Validation prevents invalid names
- ✅ Clear error messages
- ✅ No crashes

---

### Test 8.2: Missing Files
**Steps**:
1. Add documents to project
2. Manually delete one PDF file from disk
3. Reopen app
4. Open project
5. Verify missing file marked with warning (⚠️)

**Pass Criteria**:
- ✅ App handles missing files gracefully
- ✅ Warning indicator shown
- ✅ Other documents still work

---

### Test 8.3: Close Window While Editing
**Steps**:
1. Open project settings
2. Make changes
3. Close main window without clicking OK/Cancel
4. Reopen app
5. Verify changes were NOT saved

**Pass Criteria**:
- ✅ Graceful window close
- ✅ Unsaved changes discarded
- ✅ Project state intact

---

## Test Suite 9: Performance

### Test 9.1: Project List Performance
**Steps**:
1. Create 10+ projects
2. Open Project Dashboard
3. Verify fast loading
4. Search through projects
5. Switch filters rapidly
6. Verify responsive

**Pass Criteria**:
- ✅ Dashboard loads quickly
- ✅ Search is instant
- ✅ Filters update fast

---

### Test 9.2: Project Switching Performance
**Steps**:
1. Create projects with various amounts of data
2. Time how long it takes to switch between them
3. Verify switches feel instant (< 1 second)

**Pass Criteria**:
- ✅ Fast switching
- ✅ No noticeable lag
- ✅ UI updates smoothly

---

## Test Results Template

Use this template to record your test results:

```
## Test Execution Report

**Date**: ___________
**Tester**: ___________
**Build**: ___________

### Test Suite 1: Project Dashboard
- [ ] Test 1.1: First Launch
- [ ] Test 1.2: Create New Project
- [ ] Test 1.3: Create Multiple Projects
- [ ] Test 1.4: Search Projects
- [ ] Test 1.5: Filter Projects

### Test Suite 2: Project Switching
- [ ] Test 2.1: Switch Between Projects
- [ ] Test 2.2: Last Project Persistence

### Test Suite 3: Document Management
- [ ] Test 3.1: Add Documents to Project
- [ ] Test 3.2: Documents Persist Per Project
- [ ] Test 3.3: Remove Documents
- [ ] Test 3.4: Clear All Documents

### Test Suite 4: Project Settings
- [ ] Test 4.1: Open Project Settings
- [ ] Test 4.2: Modify Project Information
- [ ] Test 4.3: Modify LLM Settings
- [ ] Test 4.4: Modify Processing Settings
- [ ] Test 4.5: Modify Output Settings
- [ ] Test 4.6: Settings Per Project
- [ ] Test 4.7: Cancel Settings Changes

### Test Suite 5: Project Management Operations
- [ ] Test 5.1: Favorite/Unfavorite Projects
- [ ] Test 5.2: Archive Project
- [ ] Test 5.3: Restore Archived Project
- [ ] Test 5.4: Delete Project Permanently

### Test Suite 6: Multi-Language Support
- [ ] Test 6.1: French Interface
- [ ] Test 6.2: Arabic Interface (RTL)

### Test Suite 7: Integration Tests
- [ ] Test 7.1: Complete Workflow
- [ ] Test 7.2: Rapid Project Switching
- [ ] Test 7.3: Project with Many Documents

### Test Suite 8: Error Handling
- [ ] Test 8.1: Invalid Project Name
- [ ] Test 8.2: Missing Files
- [ ] Test 8.3: Close Window While Editing

### Test Suite 9: Performance
- [ ] Test 9.1: Project List Performance
- [ ] Test 9.2: Project Switching Performance

### Issues Found
| Test ID | Description | Severity | Status |
|---------|-------------|----------|--------|
| | | | |

### Summary
- Total Tests: ___
- Passed: ___
- Failed: ___
- Blocked: ___
- Pass Rate: ___%
```

---

## Notes for Testers

1. **Test in a clean state**: Start with no existing projects for most accurate results
2. **Use real PDFs**: Test with actual PDF files of various sizes
3. **Test all languages**: If multilingual, test UI in each language
4. **Document issues**: Record any bugs, crashes, or unexpected behavior
5. **Performance**: Note any slowness or lag
6. **Usability**: Comment on UI/UX issues

---

## Common Issues to Watch For

- [ ] Projects not persisting after close
- [ ] Documents mixing between projects
- [ ] Settings not saving
- [ ] UI not updating after operations
- [ ] Crashes when switching rapidly
- [ ] Memory leaks with many projects
- [ ] Missing translations
- [ ] Layout issues in different languages

---

## Quick Smoke Test (5 minutes)

If you only have time for a quick test:

1. Create 2 projects
2. Add documents to each
3. Switch between them
4. Change settings in one project
5. Close and reopen app
6. Verify everything persisted

**Pass Criteria**: No crashes, data persists correctly.
