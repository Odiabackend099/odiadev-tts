#!/bin/bash

echo "🚀 ODIA.dev Quick Start"
echo "======================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 This will set up your ODIA.dev TTS platform"
    echo ""
    read -p "Have you cloned your GitHub repo? (y/n): " answer
    if [ "$answer" != "y" ]; then
        echo ""
        echo "Please first run:"
        echo "git clone https://github.com/Odiabackend099/odiadev-tts.git"
        echo "cd odiadev-tts"
        echo ""
        exit 1
    fi
fi

# Check for required files
echo "✅ Checking files..."
required_files=("app.py" "requirements.txt" "render.yaml")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing files: ${missing_files[*]}"
    echo "Please copy all the provided files to this folder"
    exit 1
fi

echo "✅ All files present!"
echo ""

# Install dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages"
    echo "Try: python -m pip install -r requirements.txt"
    exit 1
fi

echo "✅ Packages installed!"
echo ""

# Test locally
echo "🧪 Do you want to test locally first? (y/n): "
read test_local

if [ "$test_local" = "y" ]; then
    echo "Starting local server..."
    echo "Open http://localhost:5000 in your browser"
    echo "Press Ctrl+C when done testing"
    python app.py
fi

# Deploy
echo ""
echo "🚀 Ready to deploy to Render!"
echo ""
echo "Steps:"
echo "1. Commit your changes:"
echo "   git add ."
echo "   git commit -m 'Deploy ODIA.dev TTS'"
echo "   git push"
echo ""
echo "2. Go to https://dashboard.render.com"
echo "3. Create New > Web Service"
echo "4. Connect your GitHub repo"
echo "5. Click Create Web Service"
echo ""
echo "Your app will be live at:"
echo "https://odia-tts-platform.onrender.com"
echo ""
echo "======================="
echo "✨ Good luck!"
