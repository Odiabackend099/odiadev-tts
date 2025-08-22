#!/usr/bin/env python3
"""
MANUS AGENT: Fixed Nigerian TTS API
SINGLE STRATEGY: Pure edge-tts with proper error handling
"""

import os
import secrets
import subprocess
import tempfile
import base64
import time
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# 🤖 MANUS AGENT: Auto-configuration
app = Flask(__name__)
CORS(app, origins="*")

# Environment variables with smart defaults
PORT = int(os.getenv("PORT", 5000))
VALID_API_KEYS = os.getenv("VALID_API_KEYS", "my_key,test_key,demo_key").split(",")
ADMIN_KEY = os.getenv("ADMIN_KEY", "manus_admin_2025")

# 🎤 Nigerian Voice Mapping (ONLY edge-tts voices)
NIGERIAN_VOICES = {
    "female": "en-NG-EzinneNeural",
    "male": "en-NG-AbeoNeural", 
    "ezinne": "en-NG-EzinneNeural",
    "abeo": "en-NG-AbeoNeural",
    "aria": "en-US-AriaNeural",
    "guy": "en-US-GuyNeural",
    "jenny": "en-US-JennyNeural"
}

# 🤖 MANUS AGENT: Enhanced Logging
def manus_log(request_id, message, level="INFO"):
    """Smart logging with request tracking"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] [{request_id}] {message}")

# 🤖 MANUS AGENT: REAL Diagnosis with Audio Testing
@app.route('/manus/diagnose')
def manus_diagnose():
    """REAL auto-diagnosis with actual TTS testing"""
    request_id = f"diag_{int(time.time())}"
    manus_log(request_id, "🤖 MANUS AGENT: Starting REAL diagnosis")
    
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "agent": "MANUS v2.0 - FIXED",
        "status": "diagnosing",
        "checks": {},
        "recommendations": [],
        "test_results": {}
    }
    
    # ✅ Check 1: Environment Variables
    env_check = {
        "VALID_API_KEYS": "✅ SET" if VALID_API_KEYS else "❌ MISSING", 
        "PORT": f"✅ {PORT}",
        "RENDER": "✅ YES" if os.getenv("RENDER") else "❌ LOCAL",
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "Unknown")
    }
    diagnosis["checks"]["environment"] = env_check
    manus_log(request_id, f"Environment check: {env_check}")
    
    # ✅ Check 2: Edge-TTS Installation
    edge_tts_status = "❌ NOT INSTALLED"
    try:
        result = subprocess.run(["edge-tts", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            edge_tts_status = f"✅ INSTALLED ({result.stdout.strip()})"
            manus_log(request_id, "edge-tts installation verified")
        else:
            edge_tts_status = "❌ COMMAND FAILED"
            diagnosis["recommendations"].append("🔧 edge-tts command failing")
    except FileNotFoundError:
        edge_tts_status = "❌ COMMAND NOT FOUND"
        diagnosis["recommendations"].append("🔧 Install edge-tts: pip install edge-tts")
    except Exception as e:
        edge_tts_status = f"❌ ERROR ({str(e)[:30]})"
        diagnosis["recommendations"].append("🔧 edge-tts installation corrupted")
    
    diagnosis["checks"]["edge_tts"] = edge_tts_status
    
    # ✅ Check 3: ACTUAL TTS Generation Test
    audio_test_status = "❌ NOT TESTED"
    try:
        manus_log(request_id, "Testing actual TTS generation...")
        test_audio, test_mime = generate_tts_with_retry("Test diagnosis audio", "female")
        
        if test_audio and len(test_audio) > 1000:  # Reasonable MP3 size
            audio_test_status = f"✅ WORKING ({len(test_audio)} bytes generated)"
            diagnosis["test_results"]["audio_size"] = len(test_audio)
            diagnosis["test_results"]["audio_format"] = test_mime
            manus_log(request_id, f"TTS test successful: {len(test_audio)} bytes")
        else:
            audio_test_status = "❌ GENERATION FAILED"
            diagnosis["recommendations"].append("🔧 TTS generation producing no/small output")
    except Exception as e:
        audio_test_status = f"❌ CRASHED ({str(e)[:50]})"
        diagnosis["recommendations"].append(f"🔧 TTS crashed: {str(e)[:100]}")
        manus_log(request_id, f"TTS test crashed: {e}", "ERROR")
    
    diagnosis["checks"]["tts_generation"] = audio_test_status
    
    # ✅ Check 4: Voice Availability Test
    voices_available = []
    for voice_name, voice_id in NIGERIAN_VOICES.items():
        try:
            # Quick test to see if voice exists
            result = subprocess.run(
                ["edge-tts", "--voice", voice_id, "--text", "test", "--write-media", "/dev/null"],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                voices_available.append(voice_name)
        except:
            pass
    
    if voices_available:
        diagnosis["checks"]["voices"] = f"✅ {len(voices_available)} working: {', '.join(voices_available[:3])}"
    else:
        diagnosis["checks"]["voices"] = "❌ NO VOICES WORKING"
        diagnosis["recommendations"].append("🔧 No Nigerian voices available")
    
    # 📋 Generate Final Status
    critical_checks = ["edge_tts", "tts_generation"]
    failures = [check for check in critical_checks 
               if diagnosis["checks"][check].startswith("❌")]
    
    if not failures:
        diagnosis["status"] = "✅ FULLY OPERATIONAL"
        if not diagnosis["recommendations"]:
            diagnosis["recommendations"].append("🎉 All systems working perfectly!")
    else:
        diagnosis["status"] = f"❌ {len(failures)} CRITICAL FAILURES"
        diagnosis["recommendations"].insert(0, f"🚨 Fix these: {', '.join(failures)}")
    
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

# 🤖 MANUS AGENT: FIXED TTS Generation (Pure edge-tts)
def generate_tts_with_retry(text, voice="female", max_retries=3):
    """Generate TTS using ONLY edge-tts with comprehensive error handling"""
    request_id = f"tts_{int(time.time())}"
    voice_id = NIGERIAN_VOICES.get(voice, NIGERIAN_VOICES["female"])
    
    manus_log(request_id, f"TTS generation: '{text[:30]}...' with {voice_id}")
    
    for attempt in range(max_retries):
        temp_path = None
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_path = tmp.name
            
            manus_log(request_id, f"Attempt {attempt + 1}: temp file {temp_path}")
            
            # Run edge-tts with comprehensive options
            cmd = [
                "edge-tts",
                "--text", text,
                "--voice", voice_id,
                "--write-media", temp_path
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60  # Increased timeout for Render
            )
            duration = time.time() - start_time
            
            manus_log(request_id, f"edge-tts completed in {duration:.1f}s, return code: {result.returncode}")
            
            if result.returncode != 0:
                manus_log(request_id, f"edge-tts error: {result.stderr}", "ERROR")
                continue
            
            # Verify file exists and has content
            if not os.path.exists(temp_path):
                manus_log(request_id, "Output file not created", "ERROR")
                continue
                
            file_size = os.path.getsize(temp_path)
            if file_size < 1000:  # Minimum reasonable MP3 size
                manus_log(request_id, f"Output file too small: {file_size} bytes", "ERROR")
                continue
            
            # Read audio data
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Verify audio data
            if len(audio_data) < 1000:
                manus_log(request_id, f"Audio data too small: {len(audio_data)} bytes", "ERROR")
                continue
            
            # Check for MP3 magic numbers
            if not (audio_data[:3] == b'ID3' or 
                   (audio_data[0] == 0xFF and (audio_data[1] & 0xE0) == 0xE0)):
                manus_log(request_id, "Invalid MP3 format detected", "ERROR")
                continue
            
            # Success!
            manus_log(request_id, f"TTS SUCCESS: {len(audio_data)} bytes in {duration:.1f}s")
            return audio_data, "audio/mpeg"
            
        except subprocess.TimeoutExpired:
            manus_log(request_id, f"Attempt {attempt + 1}: timeout after 60s", "ERROR")
        except Exception as e:
            manus_log(request_id, f"Attempt {attempt + 1}: exception {e}", "ERROR")
        finally:
            # Always cleanup temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
        
        # Exponential backoff for retries
        if attempt < max_retries - 1:
            delay = (2 ** attempt) + 0.5
            manus_log(request_id, f"Retrying in {delay}s...")
            time.sleep(delay)
    
    manus_log(request_id, "TTS generation failed after all retries", "ERROR")
    return None, None

# 🏠 Main Routes
@app.route('/')
def home():
    """Landing page with enhanced info"""
    return f"""
    <html>
    <head><title>🤖 MANUS AGENT TTS v2.0</title></head>
    <body style="font-family: Arial; background: #1a1f3a; color: white; padding: 40px; text-align: center;">
        <h1>🤖 MANUS AGENT v2.0</h1>
        <h2>Nigerian TTS Platform - FIXED</h2>
        <p>🎤 Pure edge-tts implementation</p>
        <div style="margin: 30px 0;">
            <a href="/manus/diagnose" style="color: #f4d03f; text-decoration: none; margin: 10px;">🔍 REAL Diagnosis</a> |
            <a href="/health" style="color: #f4d03f; text-decoration: none; margin: 10px;">❤️ Health Check</a> |
            <a href="/test" style="color: #f4d03f; text-decoration: none; margin: 10px;">🧪 Quick Test</a>
        </div>
        <p><small>Fixed Architecture • {len(NIGERIAN_VOICES)} Voices Available</small></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Enhanced health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'MANUS AGENT TTS v2.0 - FIXED',
        'voices': list(NIGERIAN_VOICES.keys()),
        'environment': 'render' if os.getenv('RENDER') else 'local',
        'architecture': 'pure-edge-tts',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test')
def quick_test():
    """Quick TTS test endpoint"""
    request_id = f"test_{int(time.time())}"
    
    try:
        # Generate a quick test
        audio_data, mime_type = generate_tts_with_retry("MANUS AGENT test successful!", "female")
        
        if audio_data:
            return Response(
                audio_data,
                mimetype=mime_type,
                headers={
                    'Content-Type': mime_type,
                    'X-Request-ID': request_id,
                    'X-Test-Status': 'SUCCESS'
                }
            )
        else:
            return jsonify({
                'error': 'Test failed - check /manus/diagnose',
                'request_id': request_id
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Test crashed: {str(e)}',
            'request_id': request_id
        }), 500

@app.route('/speak')
def speak():
    """Fixed TTS endpoint"""
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
    
    if len(text) > 1000:
        return jsonify({'error': 'Text too long (max 1000 chars)', 'request_id': request_id}), 400
    
    # Generate audio
    audio_data, mime_type = generate_tts_with_retry(text, voice)
    
    if not audio_data:
        manus_log(request_id, "TTS generation failed completely", "ERROR")
        return jsonify({
            'error': 'TTS generation failed - check /manus/diagnose for details',
            'request_id': request_id,
            'diagnosis_url': '/manus/diagnose'
        }), 500
    
    # Return audio
    manus_log(request_id, f"Returning {len(audio_data)} bytes of audio")
    return Response(
        audio_data,
        mimetype=mime_type,
        headers={
            'Content-Type': mime_type,
            'X-Request-ID': request_id,
            'X-Audio-Size': str(len(audio_data)),
            'Cache-Control': 'no-cache'
        }
    )

@app.route('/api/speak', methods=['POST'])
def api_speak():
    """POST version with JSON response"""
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
            'diagnosis_url': '/manus/diagnose'
        }), 500
    
    # Return as base64 for JSON response
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    return jsonify({
        'success': True,
        'audio_url': f"data:{mime_type};base64,{audio_base64}",
        'character_count': len(text),
        'voice': voice,
        'audio_size': len(audio_data),
        'request_id': request_id
    })

# 🤖 MANUS AGENT: Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/speak', '/api/speak', '/health', '/manus/diagnose', '/test'],
        'agent': 'MANUS v2.0'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'diagnosis': '/manus/diagnose',
        'agent': 'MANUS v2.0'
    }), 500

if __name__ == '__main__':
    # 🤖 MANUS AGENT: Enhanced startup
    print("\n" + "="*60)
    print("🤖 MANUS AGENT v2.0: Nigerian TTS Platform - FIXED")
    print("="*60)
    print(f"🏠 Dashboard: http://localhost:{PORT}")
    print(f"🎤 TTS Endpoint: http://localhost:{PORT}/speak")
    print(f"🔍 REAL Diagnosis: http://localhost:{PORT}/manus/diagnose")
    print(f"🧪 Quick Test: http://localhost:{PORT}/test")
    print("="*60)
    print(f"🌍 Environment: {'Render' if os.getenv('RENDER') else 'Local'}")
    print(f"🎤 Voices: {len(NIGERIAN_VOICES)} available")
    print(f"🔑 API Keys: {len(VALID_API_KEYS)} configured")
    print(f"🏗️ Architecture: Pure edge-tts (FIXED)")
    print("="*60 + "\n")
    
    # Bind correctly for Render
    app.run(host='0.0.0.0', port=PORT, debug=False)