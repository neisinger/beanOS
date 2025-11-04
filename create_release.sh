#!/bin/bash
# Script to create the v2.3.1 release for beanOS
# Run this script after the release PR has been merged to main

set -e

VERSION="v2.3.1"
TITLE="beanOS v2.3.1 - Button B Cappuccino Fix"

echo "Creating release $VERSION..."

# Ensure we're on main and up to date
echo "Switching to main branch..."
git checkout main
git pull origin main

# Create and push the tag
echo "Creating tag $VERSION..."
git tag -a $VERSION -m "Release version 2.3.1 - Button B Cappuccino Fix"

echo "Pushing tag to GitHub..."
git push origin $VERSION

echo ""
echo "✅ Tag created and pushed!"
echo ""
echo "The GitHub Actions workflow will now automatically create the release."
echo "Check the progress at: https://github.com/neisinger/beanOS/actions"
echo ""
echo "The release will be available at: https://github.com/neisinger/beanOS/releases/tag/$VERSION"
echo ""
