# Quick Start: Creating the v2.3.1 Release

## Prerequisites
This PR must be merged to `main` first.

## Simple Steps to Create the Release

Once this PR is merged, follow these simple steps:

### Option 1: Automatic (Recommended) 

Just create and push a tag:

```bash
git checkout main
git pull
git tag -a v2.3.1 -m "Release version 2.3.1 - Button B Cappuccino Fix"
git push origin v2.3.1
```

That's it! The GitHub Actions workflow will automatically:
✅ Create the release
✅ Add the release notes
✅ Attach `main.py` and `maintenance_config.json` as downloadable files

### Option 2: Manual Trigger via GitHub UI

1. Go to: https://github.com/neisinger/beanOS/actions/workflows/release.yml
2. Click "Run workflow"
3. Enter version: `v2.3.1`
4. Click "Run workflow"

## What Happens Next

After creating the tag (Option 1) or running the workflow (Option 2):

1. A new release will appear at: https://github.com/neisinger/beanOS/releases
2. Users can download `main.py` and `maintenance_config.json` directly
3. The release will include full release notes and installation instructions

## Verification

Check that the release was created:
- Visit: https://github.com/neisinger/beanOS/releases/tag/v2.3.1
- Confirm the files are attached: `main.py` and `maintenance_config.json`

---

For more details, see [RELEASE_GUIDE.md](RELEASE_GUIDE.md)
