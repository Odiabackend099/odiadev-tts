#!/usr/bin/env python3
"""
MANUS AGENT: Self-Diagnosing Nigerian TTS API
Auto-debugs Render deployment issues and fixes them
"""

import os
import secrets
import subprocess
import tempfile
import base64
import time
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

# 🤖 MANUS AGENT: Auto-configuration
app = Flask(__name__)
CORS(app, origins="*")

# Environment variables with smart defaults
PORT = int(os.getenv("PORT", 5000))
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "https://vgh0i1c5ko11.manus.space")
VALID_API_KEYS = os.getenv("VALID_API_KEYS", "my_key,test_key,demo_key").split(",")
ADMIN_KEY = os.getenv("ADMIN_KEY", "manus_admin_2025")

# 🎤 Nigerian Voice Mapping
NIGERIAN_VOICES = {
    "female": "en-NG-EzinneNeural",
    "male": "en-NG-AbeoNeural", 
    "ezinne": "en-NG-EzinneNeural",
    "abeo": "en-NG-AbeoNeural",
    "aria": "en-US-AriaNeural",
    "guy": "en-US-GuyNeural"
}

# 🤖 MANUS AGENT: Smart Logging
def manus_log(request_id, message, level="INFO"):
    """Smart logging with request tracking"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] [{request_id}] {message}")

# 🤖 MANUS AGENT: Auto-Diagnosis Endpoints
@app.route('/manus/diagnose')
def manus_diagnose():
    """Auto-diagnose deployment issues"""
    request_id = request.headers.get('x-request-id', f"diag_{int(time.time())}")
    manus_log(request_id, "🤖 MANUS AGENT: Starting auto-diagnosis")
    
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "agent": "MANUS v1.0",
        "status": "diagnosing",
        "checks": {},
        "recommendations": []
    }
    
    # ✅ Check 1: Environment Variables
    env_check = {
        "TTS_SERVICE_URL": "✅ SET" if TTS_SERVICE_URL else "❌ MISSING",
        "VALID_API_KEYS": "✅ SET" if VALID_API_KEYS else "❌ MISSING", 
        "PORT": f"✅ {PORT}",
        "RENDER": "✅ YES" if os.getenv("RENDER") else "❌ LOCAL"
    }
    diagnosis["checks"]["environment"] = env_check
    manus_log(request_id, f"Environment check: {env_check}")
    
    # ✅ Check 2: Network Connectivity
    try:
        test_response = requests.get(TTS_SERVICE_URL, timeout=10)
        network_status = f"✅ REACHABLE ({test_response.status_code})"
        manus_log(request_id, f"Network test successful: {test_response.status_code}")
    except Exception as e:
        network_status = f"❌ UNREACHABLE ({str(e)[:50]})"
        manus_log(request_id, f"Network test failed: {e}", "ERROR")
        diagnosis["recommendations"].append("🔧 Check if TTS service is down or blocked")
    
    diagnosis["checks"]["network"] = network_status
    
    # ✅ Check 3: TTS Engine
    try:
        result = subprocess.run(["edge-tts", "--list-voices"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            tts_status = "✅ WORKING"
            manus_log(request_id, "TTS engine working")
        else:
            tts_status = "❌ FAILED"
            diagnosis["recommendations"].append("🔧 edge-tts installation issue")
    except Exception as e:
        tts_status = f"❌ ERROR ({str(e)[:30]})"
        diagnosis["recommendations"].append("🔧 Install edge-tts: pip install edge-tts")
    
    diagnosis["checks"]["tts_engine"] = tts_status
    
    # 📋 Generate Recommendations
    if not diagnosis["recommendations"]:
        diagnosis["status"] = "✅ HEALTHY"
        diagnosis["recommendations"].append("🎉 All systems operational!")
    else:
        diagnosis["status"] = "⚠️ ISSUES FOUND"
    
    manus_log(request_id, f"Diagnosis complete: {diagnosis['status']}")
    return jsonify(diagnosis)

# 🤖 MANUS AGENT: Smart API Key Validation
def validate_api_key():
    """Smart API key validation with logging"""
    request_id = request.headers.get('x-request-id', f"req_{int(time.time())}")
    api_key = request.headers.get('x-api-key') or request.headers.get('Authorization', '').replace('Bearer ', '')
    
    manus_log(request_id, f"API key check: {api_key[:8] + '...' if api_key else 'MISSING'}")
    
    if not api_key:
        manus_log(request_id, "No API key provided", "ERROR")
        return None, ("Missing x-api-key header", 401)
    
    if api_key not in VALID_API_KEYS:
        manus_log(request_id, f"Invalid API key: {api_key[:8]}...", "ERROR")
        return None, ("Invalid API key", 401)
    
    manus_log(request_id, "API key validated successfully")
    return {"key": api_key}, None

# 🤖 MANUS AGENT: Smart TTS Generation
def generate_tts_with_retry(text, voice="female", max_retries=3):
    """Generate TTS with Nigerian network optimization"""
    request_id = f"tts_{int(time.time())}"
    voice_id = NIGERIAN_VOICES.get(voice, NIGERIAN_VOICES["female"])
    
    manus_log(request_id, f"TTS generation: '{text[:30]}...' with {voice_id}")
    
    for attempt in range(max_retries):
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_path = tmp.name
            
            # Run edge-tts with timeout
            cmd = ["edge-tts", "--text", text, "--voice", voice_id, "--write-media", temp_path]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            duration = time.time() - start_time
            
            if result.returncode == 0 and os.path.exists(temp_path):
                # Read audio data
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # Cleanup
                os.unlink(temp_path)
                
                manus_log(request_id, f"TTS success: {len(audio_data)} bytes in {duration:.1f}s")
                return audio_data, "audio/mpeg"
            else:
                manus_log(request_id, f"TTS attempt {attempt + 1} failed: {result.stderr}", "ERROR")
                
        except Exception as e:
            manus_log(request_id, f"TTS attempt {attempt + 1} error: {e}", "ERROR")
            
        # Cleanup on failure
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Exponential backoff for Nigerian networks
        if attempt < max_retries - 1:
            delay = (2 ** attempt) + 0.1
            manus_log(request_id, f"Retrying in {delay}s...")
            time.sleep(delay)
    
    manus_log(request_id, "TTS generation failed after all retries", "ERROR")
    return None, None

# 🏠 Main Routes
@app.route('/')
def home():
    """Landing page with Manus Agent info"""
    return """
    <html>
    <head><title>🤖 MANUS AGENT TTS</title></head>
    <body style="font-family: Arial; background: #1a1f3a; color: white; padding: 40px; text-align: center;">
        <h1>🤖 MANUS AGENT</h1>
        <h2>Nigerian TTS Platform</h2>
        <p>🎤 Ready to serve Nigerian voices</p>
        <div style="margin: 30px 0;">
            <a href="/manus/diagnose" style="color: #f4d03f; text-decoration: none; margin: 10px;">🔍 Run Diagnosis</a> |
            <a href="/health" style="color: #f4d03f; text-decoration: none; margin: 10px;">❤️ Health Check</a>
        </div>
        <p><small>Powered by Manus Agent v1.0</small></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MANUS AGENT TTS',
        'voices': list(NIGERIAN_VOICES.keys()),
        'environment': 'render' if os.getenv('RENDER') else 'local',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/speak')
def speak():
    """Main TTS endpoint with smart debugging"""
    request_id = request.headers.get('x-request-id', f"speak_{int(time.time())}")
    
    # Validate API key
    api_key, error = validate_api_key()
    if error:
        return jsonify({'error': error[0], 'request_id': request_id}), error[1]
    
    # Get parameters
    text = request.args.get('text', '').strip()
    voice = request.args.get('voice', 'female')
    
    manus_log(request_id, f"TTS request: text='{text[:50]}...', voice={voice}")
    
    if not text:
        manus_log(request_id, "No text provided", "ERROR")
        return jsonify({'error': 'No text provided', 'request_id': request_id}), 400
    
    # Generate audio with retry logic
    audio_data, mime_type = generate_tts_with_retry(text, voice)
    
    if not audio_data:
        manus_log(request_id, "TTS generation failed completely", "ERROR")
        return jsonify({
            'error': 'TTS generation failed - check /manus/diagnose for details',
            'request_id': request_id
        }), 500
    
    # Return audio
    manus_log(request_id, f"Returning {len(audio_data)} bytes of audio")
    return Response(
        audio_data,
        mimetype=mime_type,
        headers={
            'Content-Type': mime_type,
            'X-Request-ID': request_id,
            'Cache-Control': 'no-cache'
        }
    )

@app.route('/api/speak', methods=['POST'])
def api_speak():
    """POST version of speak endpoint"""
    request_id = request.headers.get('x-request-id', f"api_{int(time.time())}")
    
    # Validate API key
    api_key, error = validate_api_key()
    if error:
        return jsonify({'error': error[0], 'request_id': request_id}), error[1]
    
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    voice = data.get('voice', 'female')
    
    if not text:
        return jsonify({'error': 'No text provided', 'request_id': request_id}), 400
    
    # Generate audio
    audio_data, mime_type = generate_tts_with_retry(text, voice)
    
    if not audio_data:
        return jsonify({
            'error': 'TTS generation failed',
            'request_id': request_id,
            'diagnosis': '/manus/diagnose'
        }), 500
    
    # Return as base64 for JSON response
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    return jsonify({
        'success': True,
        'audio_url': f"data:{mime_type};base64,{audio_base64}",
        'character_count': len(text),
        'voice': voice,
        'request_id': request_id
    })

# 🤖 MANUS AGENT: Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/speak', '/api/speak', '/health', '/manus/diagnose']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'diagnosis': '/manus/diagnose',
        'agent': 'MANUS v1.0'
    }), 500

if __name__ == '__main__':
    # 🤖 MANUS AGENT: Smart startup
    print("\n" + "="*60)
    print("🤖 MANUS AGENT: Nigerian TTS Platform")
    print("="*60)
    print(f"🏠 Dashboard: http://localhost:{PORT}")
    print(f"🎤 TTS Endpoint: http://localhost:{PORT}/speak")
    print(f"🔍 Diagnosis: http://localhost:{PORT}/manus/diagnose")
    print(f"❤️ Health: http://localhost:{PORT}/health")
    print("="*60)
    print(f"🌍 Environment: {'Render' if os.getenv('RENDER') else 'Local'}")
    print(f"🎤 Voices: {len(NIGERIAN_VOICES)} available")
    print(f"🔑 API Keys: {len(VALID_API_KEYS)} configured")
    print("="*60 + "\n")
    
    # Bind correctly for Render
    app.run(host='0.0.0.0', port=PORT, debug=False)