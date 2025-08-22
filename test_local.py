#!/usr/bin/env python3
"""
Test ODIA.dev TTS Locally
Run this to make sure everything works before deploying
"""

import subprocess
import sys

print("\n" + "="*60)
print("🧪 ODIA.dev Local Test")
print("="*60)

# Step 1: Check Python version
print("\n[1] Checking Python version...")
python_version = sys.version
print(f"✅ Python {python_version.split()[0]}")

# Step 2: Install requirements
print("\n[2] Installing requirements...")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                   check=True, capture_output=True, text=True)
    print("✅ All packages installed")
except subprocess.CalledProcessError as e:
    print(f"❌ Failed to install packages: {e}")
    print("Run manually: pip install -r requirements.txt")

# Step 3: Test edge-tts
print("\n[3] Testing edge-tts...")
try:
    result = subprocess.run(["edge-tts", "--list-voices"], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        voices = [line for line in result.stdout.split('\n') if 'NG' in line]
        print(f"✅ edge-tts working! Found {len(voices)} Nigerian voices")
    else:
        print("❌ edge-tts not working properly")
except Exception as e:
    print(f"❌ edge-tts error: {e}")

# Step 4: Test the app
print("\n[4] Starting ODIA.dev server...")
print("-"*60)
print("🚀 Server starting on http://localhost:5000")
print("📱 Open your browser to test!")
print("🛑 Press Ctrl+C to stop")
print("-"*60)

try:
    # Run the app
    subprocess.run([sys.executable, "app.py"])
except KeyboardInterrupt:
    print("\n✅ Server stopped")
    
print("\n" + "="*60)
print("✅ Local test complete!")
print("Ready to deploy to Render!")
print("="*60)
