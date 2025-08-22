#!/usr/bin/env python3
"""
MANUS AGENT: API Testing Script
Test your TTS API locally before deployment
"""

import requests
import json
import time

def test_local_api():
    """Test the API locally"""
    base_url = "http://localhost:5000"
    
    print("🤖 MANUS AGENT: Testing Local API")
    print("="*50)
    
    # Test 1: Health Check
    print("\n[1] Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Diagnosis
    print("\n[2] Testing Auto-Diagnosis...")
    try:
        response = requests.get(f"{base_url}/manus/diagnose")
        print(f"✅ Diagnosis: {response.status_code}")
        diagnosis = response.json()
        print(f"   Status: {diagnosis['status']}")
        for check, result in diagnosis['checks'].items():
            print(f"   {check}: {result}")
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
    
    # Test 3: TTS Generation
    print("\n[3] Testing TTS Generation...")
    try:
        headers = {'x-api-key': 'my_key'}
        params = {'text': 'Hello from Manus Agent!', 'voice': 'female'}
        
        response = requests.get(f"{base_url}/speak", headers=headers, params=params)
        print(f"✅ TTS: {response.status_code}")
        
        if response.status_code == 200:
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)
            print(f"   Audio saved: test_output.mp3 ({len(response.content)} bytes)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
    
    print("\n" + "="*50)
    print("🎉 Local testing complete!")
    print("Ready to deploy to Render!")

if __name__ == "__main__":
    test_local_api()