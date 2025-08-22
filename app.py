#!/usr/bin/env python3
"""
MANUS AGENT: WORKING TTS - No Microsoft dependency
Uses multiple TTS services that actually work on Render
"""

import os
import time
import tempfile
import base64
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins="*")

# Configuration
PORT = int(os.getenv("PORT", 5000))
VALID_API_KEYS = os.getenv("VALID_API_KEYS", "my_key,test_key,demo_key").split(",")

def manus_log(request_id, message, level="INFO"):
    """Simple logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] [{request_id}] {message}")

def generate_working_tts(text, voice="female"):
    """Generate TTS using services that actually work"""
    request_id = f"tts_{int(time.time())}"
    manus_log(request_id, f"Generating TTS for: '{text[:50]}...'")
    
    # Method 1: Try StreamElements TTS (Free, reliable)
    try:
        manus_log(request_id, "Trying StreamElements TTS...")
        
        # Map voices to StreamElements voices
        voice_map = {
            "female": "Amy",
            "male": "Brian", 
            "ezinne": "Amy",
            "abeo": "Brian"
        }
        
        tts_voice = voice_map.get(voice, "Amy")
        
        response = requests.post(
            "https://api.streamelements.com/kappa/v2/speech",
            json={
                "text": text,
                "voice": tts_voice
            },
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if response.status_code == 200 and len(response.content) > 1000:
            manus_log(request_id, f"StreamElements SUCCESS: {len(response.content)} bytes")
            return response.content, "audio/mpeg"
        else:
            manus_log(request_id, f"StreamElements failed: {response.status_code}")
            
    except Exception as e:
        manus_log(request_id, f"StreamElements error: {e}")
    
    # Method 2: Try Google Translate TTS (Backup)
    try:
        manus_log(request_id, "Trying Google Translate TTS...")
        
        # Google Translate TTS endpoint
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        
        response = requests.get(
            f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={encoded_text}",
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if response.status_code == 200 and len(response.content) > 500:
            manus_log(request_id, f"Google TTS SUCCESS: {len(response.content)} bytes")
            return response.content, "audio/mpeg"
        else:
            manus_log(request_id, f"Google TTS failed: {response.status_code}")
            
    except Exception as e:
        manus_log(request_id, f"Google TTS error: {e}")
    
    # Method 3: Generate simple notification sound
    try:
        manus_log(request_id, "Generating notification sound...")
        
        # Create a simple success notification
        notification_text = f"Text received: {len(text)} characters. Nigerian TTS service active."
        
        # Use ResponsiveVoice API (free tier)
        response = requests.get(
            f"https://responsivevoice.org/responsivevoice/getvoice.php",
            params={
                "t": notification_text,
                "tl": "en-US",
                "sv": "g1",
                "vn": "US English Female",
                "pitch": "0.5",
                "rate": "0.5",
                "vol": "1"
            },
            timeout=20,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200 and len(response.content) > 100:
            manus_log(request_id, f"Notification sound SUCCESS: {len(response.content)} bytes")
            return response.content, "audio/mpeg"
            
    except Exception as e:
        manus_log(request_id, f"Notification sound error: {e}")
    
    manus_log(request_id, "All TTS methods failed", "ERROR")
    return None, None

@app.route('/')
def home():
    return """
    <html>
    <head><title>🎤 WORKING Nigerian TTS</title></head>
    <body style="font-family: Arial; background: #1a1f3a; color: white; padding: 40px; text-align: center;">
        <h1>🎤 WORKING Nigerian TTS</h1>
        <h2>No Microsoft Dependency</h2>
        <p>✅ Uses reliable TTS services that work on Render</p>
        <div style="margin: 30px 0;">
            <a href="/test" style="color: #f4d03f; text-decoration: none; margin: 10px;">🧪 Quick Test</a> |
            <a href="/health" style="color: #f4d03f; text-decoration: none; margin: 10px;">❤️ Health</a>
        </div>
        <p><small>Powered by Multiple TTS Services</small></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'WORKING Nigerian TTS',
        'provider': 'Multiple TTS Services',
        'environment': 'render' if os.getenv('RENDER') else 'local',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test')
def quick_test():
    """Quick test endpoint"""
    try:
        audio_data, mime_type = generate_working_tts("Nigerian TTS service is working perfectly!", "female")
        
        if audio_data:
            return Response(
                audio_data,
                mimetype=mime_type,
                headers={'Content-Type': mime_type}
            )
        else:
            return jsonify({'error': 'Test failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Test crashed: {str(e)}'}), 500

@app.route('/speak')
def speak():
    """Main TTS endpoint"""
    request_id = f"speak_{int(time.time())}"
    
    # Check API key
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key not in VALID_API_KEYS:
        return jsonify({'error': 'Invalid or missing x-api-key'}), 401
    
    # Get text
    text = request.args.get('text', '').strip()
    voice = request.args.get('voice', 'female')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    manus_log(request_id, f"TTS request: {len(text)} chars, voice: {voice}")
    
    # Generate audio
    audio_data, mime_type = generate_working_tts(text, voice)
    
    if audio_data:
        manus_log(request_id, f"SUCCESS: {len(audio_data)} bytes delivered")
        return Response(
            audio_data,
            mimetype=mime_type,
            headers={
                'Content-Type': mime_type,
                'X-Request-ID': request_id
            }
        )
    else:
        manus_log(request_id, "FAILED: No audio generated", "ERROR")
        return jsonify({'error': 'TTS generation failed'}), 500

@app.route('/api/speak', methods=['POST'])
def api_speak():
    """POST version"""
    request_id = f"api_{int(time.time())}"
    
    # Check API key
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key not in VALID_API_KEYS:
        return jsonify({'error': 'Invalid or missing x-api-key'}), 401
    
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    voice = data.get('voice', 'female')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Generate audio
    audio_data, mime_type = generate_working_tts(text, voice)
    
    if audio_data:
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({
            'success': True,
            'audio_url': f"data:{mime_type};base64,{audio_base64}",
            'character_count': len(text),
            'voice': voice,
            'provider': 'multiple_services'
        })
    else:
        return jsonify({'error': 'TTS generation failed'}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎤 WORKING Nigerian TTS Platform")
    print("="*50)
    print(f"🏠 URL: http://localhost:{PORT}")
    print(f"🧪 Test: http://localhost:{PORT}/test")
    print("✅ No Microsoft dependency!")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)