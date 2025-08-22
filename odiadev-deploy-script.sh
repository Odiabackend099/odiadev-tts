#!/bin/bash

echo "🚀 ODIADEV TTS - Deploy to GitHub & Render"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "Deploy ODIADEV TTS Platform - $(date '+%Y-%m-%d %H:%M:%S')"

# Check if remote exists
if ! git remote | grep -q "origin"; then
    echo ""
    echo "⚠️  No git remote found!"
    echo "Please add your GitHub repository:"
    echo ""
    echo "git remote add origin https://github.com/YOUR_USERNAME/odiadev-tts.git"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Push to GitHub
echo "🌐 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "🎯 Next Steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New+' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Render will auto-deploy from render.yaml"
echo ""
echo "Your app will be live at: https://odiadev-tts.onrender.com"
echo "=========================================="