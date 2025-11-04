# Release Creation Guide for beanOS

This guide explains how to create releases for beanOS on GitHub.

## Automated Release Process (Recommended)

The repository now includes GitHub Actions workflows that automate the release process.

### Option 1: Push a Tag (Automatic Release)

Simply create and push a tag, and the release will be created automatically:

```bash
# Create and push the tag
git tag -a v2.3.1 -m "Release version 2.3.1 - Button B Cappuccino Fix"
git push origin v2.3.1
```

The `release-on-tag.yml` workflow will automatically:
- Detect the new tag
- Create a GitHub release
- Attach `main.py` and `maintenance_config.json` as assets
- Generate release notes

### Option 2: Manual Workflow Trigger

Alternatively, you can manually trigger the release workflow from GitHub:

1. Go to https://github.com/neisinger/beanOS/actions
2. Select "Create Release" workflow
3. Click "Run workflow"
4. Enter the version (e.g., v2.3.1)
5. Click "Run workflow"

This will create the tag and release in one step.

## Manual Release Process

If you prefer to create releases manually:

### Using GitHub CLI

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

### Using GitHub Web Interface

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

**For v2.3.1 Release:**

**Version:** 2.3.1  
**Tag:** v2.3.1  
**Title:** beanOS v2.3.1 - Button B Cappuccino Fix

**Summary:**
This release fixes a critical bug where Button B was not correctly incrementing the cappuccino count. The achievement checking for cappuccino has also been restored.

**Key Changes:**
- 🐛 Fixed: Button B now correctly increments cappuccino count
- 🏆 Improved: Achievement checking for cappuccino button restored

## Files Included in Release

- `main.py` - Main application file
- `maintenance_config.json` - Maintenance configuration

## Verification

After creating the release, verify that:
- [ ] The tag exists in the repository
- [ ] The release is visible at https://github.com/neisinger/beanOS/releases
- [ ] The release includes main.py and maintenance_config.json as downloadable assets
- [ ] The release notes are properly formatted and complete
