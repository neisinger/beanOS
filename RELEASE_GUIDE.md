# Release Creation Guide for beanOS v2.3.1

This guide explains how to create the v2.3.1 release for beanOS on GitHub.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated, OR
- Access to GitHub web interface with repository permissions

## Files for Release

The release should include the following files:
- `main.py` (main application)
- `maintenance_config.json` (configuration file)

## Option 1: Using GitHub CLI

If you have the GitHub CLI installed and authenticated:

```bash
# Navigate to the repository
cd /path/to/beanOS

# Create and push the tag
git tag -a v2.3.1 -m "Release version 2.3.1 - Button B Cappuccino Fix"
git push origin v2.3.1

# Create the release with the files
gh release create v2.3.1 \
  --title "beanOS v2.3.1 - Button B Cappuccino Fix" \
  --notes-file RELEASE_NOTES_v2.3.1.md \
  main.py \
  maintenance_config.json
```

## Option 2: Using GitHub Web Interface

1. **Create and push the tag:**
   ```bash
   git tag -a v2.3.1 -m "Release version 2.3.1 - Button B Cappuccino Fix"
   git push origin v2.3.1
   ```

2. **Create the release on GitHub:**
   - Go to https://github.com/neisinger/beanOS/releases
   - Click "Draft a new release"
   - Select the tag `v2.3.1` (or create it if not exists)
   - Set the release title: `beanOS v2.3.1 - Button B Cappuccino Fix`
   - Copy the content from `RELEASE_NOTES_v2.3.1.md` into the description
   - Upload the following files as release assets:
     - `main.py`
     - `maintenance_config.json`
   - Click "Publish release"

## Release Information

**Version:** 2.3.1
**Tag:** v2.3.1
**Title:** beanOS v2.3.1 - Button B Cappuccino Fix

**Summary:**
This release fixes a critical bug where Button B was not correctly incrementing the cappuccino count. The achievement checking for cappuccino has also been restored.

**Key Changes:**
- 🐛 Fixed: Button B now correctly increments cappuccino count
- 🏆 Improved: Achievement checking for cappuccino button restored

## Verification

After creating the release, verify that:
- [ ] The tag v2.3.1 exists in the repository
- [ ] The release is visible at https://github.com/neisinger/beanOS/releases
- [ ] The release includes main.py and maintenance_config.json as downloadable assets
- [ ] The release notes are properly formatted and complete
