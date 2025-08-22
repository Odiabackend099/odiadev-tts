#!/bin/bash

echo "🚀 ODIA.dev TTS Platform - Quick Deploy"
echo "========================================"

# Step 1: Update your GitHub repo
echo "📦 Updating GitHub repository..."
git add .
git commit -m "Deploy ODIA.dev TTS Platform - Ready to go!"
git push origin main

echo ""
echo "✅ GitHub updated!"
echo ""
echo "🎯 Now follow these simple steps:"
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repo: Odiabackend099/odiadev-tts"
echo "4. Render will auto-detect settings from render.yaml"
echo "5. Click 'Create Web Service'"
echo ""
echo "🎉 Your app will be live in 2-3 minutes!"
echo "========================================"
echo ""
echo "Your app URL will be:"
echo "https://odia-tts-platform.onrender.com"
echo ""
