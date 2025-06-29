#!/usr/bin/env bash
# Git LFS Setup Script for Aterges
# Use this for handling large files properly

echo "🗂️ GIT LFS SETUP FOR ATERGES"
echo "================================"

# Check if Git LFS is installed
if ! command -v git-lfs &> /dev/null; then
    echo "❌ Git LFS is not installed"
    echo "📦 Install it first:"
    echo "   Windows: Download from https://git-lfs.github.io/"
    echo "   Mac: brew install git-lfs"
    echo "   Ubuntu: sudo apt install git-lfs"
    exit 1
fi

echo "✅ Git LFS is installed"

# Initialize Git LFS in the repository
echo "🔧 Initializing Git LFS..."
git lfs install

# Track common large file types
echo "📋 Setting up tracking for large file types..."

# Document formats that can be large
git lfs track "*.pdf"
git lfs track "*.psd"
git lfs track "*.ai"
git lfs track "*.sketch"

# Media files
git lfs track "*.mp4"
git lfs track "*.mov"
git lfs track "*.avi"
git lfs track "*.mkv"
git lfs track "*.mp3"
git lfs track "*.wav"
git lfs track "*.png" # Only if very large images
git lfs track "*.jpg" # Only if very large images

# Archive files
git lfs track "*.zip"
git lfs track "*.tar.gz"
git lfs track "*.rar"
git lfs track "*.7z"

# Database files
git lfs track "*.db"
git lfs track "*.sqlite"
git lfs track "*.dump"

# Binary executables
git lfs track "*.exe"
git lfs track "*.dmg"
git lfs track "*.deb"
git lfs track "*.rpm"

echo "✅ Large file types configured for LFS tracking"

# Add .gitattributes to repository
git add .gitattributes

echo "📄 Created .gitattributes file"
echo ""
echo "🎯 USAGE GUIDE:"
echo "==============="
echo ""
echo "For files >50MB, use Git LFS:"
echo "1. Add file type to tracking: git lfs track '*.large-extension'"
echo "2. Add and commit normally: git add . && git commit -m 'Add large file'"
echo "3. Push as usual: git push origin main"
echo ""
echo "📊 To check LFS status:"
echo "   git lfs ls-files    # List LFS tracked files"
echo "   git lfs status      # Show LFS file status"
echo "   git lfs env         # Show LFS environment"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Regular files <50MB: Use normal git"
echo "   - Large files >50MB: Use git lfs track first"
echo "   - Binary files: Always use LFS"
echo "   - Media files: Always use LFS"
echo ""
echo "✅ Git LFS setup complete!"
