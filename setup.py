#!/usr/bin/env python3
"""
ODIA.dev Automatic Setup
Just run: python setup.py
"""

import os
import sys
import subprocess
import time

def print_banner():
    banner = """
    ╔════════════════════════════════════════╗
    ║       🎤 ODIA.dev TTS Platform        ║
    ║    Nigerian Languages Text-to-Speech   ║
    ╚════════════════════════════════════════╝
    """
    print(banner)

def check_files():
    """Check if all required files are present"""
    required = ['app.py', 'requirements.txt', 'render.yaml']
    missing = [f for f in required if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        print("\n📝 Please make sure you have:")
        print("   1. app.py")
        print("   2. requirements.txt") 
        print("   3. render.yaml")
        print("\nCopy all files from the artifacts to this folder!")
        return False
    
    print("✅ All required files found!")
    return True

def install_packages():
    """Install required Python packages"""
    print("\n📦 Installing packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Packages installed successfully!")
        return True
    except:
        print("❌ Failed to install packages")
        print("   Try manually: pip install -r requirements.txt")
        return False

def test_edge_tts():
    """Test if edge-tts is working"""
    print("\n🎤 Testing Text-to-Speech engine...")
    try:
        result = subprocess.run(["edge-tts", "--list-voices"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ TTS engine working!")
            return True
    except:
        pass
    
    print("⚠️  TTS engine not found - installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"])
    return True

def run_local_test():
    """Run local test"""
    print("\n🧪 Want to test locally before deploying? (y/n): ", end="")
    choice = input().lower()
    
    if choice == 'y':
        print("\n🚀 Starting local server...")
        print("📱 Open http://localhost:5000 in your browser")
        print("🛑 Press Ctrl+C to stop and continue\n")
        time.sleep(2)
        
        try:
            subprocess.run([sys.executable, "app.py"])
        except KeyboardInterrupt:
            print("\n✅ Local test completed!")

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n" + "="*50)
    print("🚀 READY TO DEPLOY!")
    print("="*50)
    
    print("\n📋 STEP-BY-STEP DEPLOYMENT:\n")
    
    print("1️⃣  PUSH TO GITHUB:")
    print("   git add .")
    print('   git commit -m "Deploy ODIA.dev TTS"')
    print("   git push\n")
    
    print("2️⃣  DEPLOY ON RENDER:")
    print("   • Go to: https://dashboard.render.com")
    print("   • Click: New + → Web Service")
    print("   • Connect: Odiabackend099/odiadev-tts")
    print("   • Click: Create Web Service\n")
    
    print("3️⃣  YOUR APP WILL BE LIVE AT:")
    print("   🌐 https://odia-tts-platform.onrender.com\n")
    
    print("⏱️  Deployment takes 2-3 minutes")
    print("="*50)

def main():
    print_banner()
    
    # Step 1: Check files
    if not check_files():
        sys.exit(1)
    
    # Step 2: Install packages
    if not install_packages():
        print("\n⚠️  Package installation failed, but continuing...")
    
    # Step 3: Test edge-tts
    test_edge_tts()
    
    # Step 4: Optional local test
    run_local_test()
    
    # Step 5: Show deployment instructions
    show_deployment_instructions()
    
    print("\n✨ Setup complete! Follow the steps above to deploy.")
    print("💬 Need help? Just ask me to clarify any step!\n")

if __name__ == "__main__":
    main()
