# Testing Reset Guide

## Quick Reset for Testing

When testing the application, you may want to start fresh without any existing projects, documents, or cached data.

## Usage

```bash
make reset
```

This command will:
- ✅ Delete all projects and their documents
- ✅ Clear all vector databases
- ✅ Remove all output files
- ✅ Clean Python cache files (`__pycache__`, `.pyc`)
- ✅ Remove system files (`.DS_Store`)
- ✅ Recreate clean directory structure

**No confirmation required** - designed for quick testing iterations.

## Testing Workflow

### Fresh Start Testing
```bash
# 1. Reset everything
make reset

# 2. Start the application
make run

# 3. Test with clean slate
# - No projects loaded
# - No documents in memory
# - No cached data
```

### Between Test Runs
```bash
# Quick reset between test iterations
make reset && make run
```

## What Gets Cleaned

```
data/
├── projects/        ← All project folders deleted
├── vector_db/       ← All vector databases cleared
└── output/          ← All generated outputs removed

All Python cache and system files removed throughout project
```

## Alternative Commands

| Command | Purpose | Confirmation Required |
|---------|---------|----------------------|
| `make reset` | Quick reset for testing | ❌ No |
| `make clean-all` | Full cleanup | ✅ Yes |
| `make clean` | Cache only | ❌ No |
| `make clean-projects` | Projects only | ✅ Yes |

## When to Use

### Use `make reset` when:
- Starting a new test session
- Testing with different document sets
- Debugging state-related issues
- Verifying fresh installation behavior
- Testing internationalization changes
- Need to clear weird states

### Use `make clean-all` when:
- Preparing for production deployment
- Archiving before major changes
- Need confirmation before deletion

## Safety Notes

⚠️ **`make reset` is destructive and immediate:**
- No confirmation prompt
- All data in `data/` directory will be deleted
- Cannot be undone

✅ **Best practices:**
- Keep important documents outside the `data/` directory
- Use version control for important projects
- Back up before major testing sessions

## Testing the Figure Extraction Feature

For the Figure Extraction feature specifically:

```bash
# 1. Reset to clean state
make reset

# 2. Launch app
make run

# 3. In the app:
#    - Create a new project
#    - Add test document (test_documents/quick_test.txt)
#    - Go to "📊 Mise à jour des données" tab
#    - Click "Extraire les figures du document"

# 4. Test complete - reset for next iteration
make reset
```

## Troubleshooting

### "Permission denied" errors
```bash
# Check directory permissions
ls -la data/

# Fix if needed
chmod -R u+w data/
make reset
```

### Directories not recreated
```bash
# Manually recreate
mkdir -p data/projects data/vector_db data/output

# Or run setup again
make setup
```

### Application shows old data after reset
- Close the application completely
- Run `make reset`
- Restart the application with `make run`

## Quick Reference

```bash
# Most common testing workflow
make reset && make run

# Full help
make help

# Check what will be cleaned (dry run)
ls -R data/projects data/vector_db data/output
```

---

**Last Updated**: 2026-01-07
**Related Docs**: MANUAL_TESTING_STEPS.md, USER_GUIDE.md
