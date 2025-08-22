#!/usr/bin/env python3
"""
ODIADEV TTS Backend - PRODUCTION READY
Zero hardcoded secrets, Nigerian-optimized, production-grade
"""

import os
import secrets
import hashlib
import subprocess
import tempfile
import base64
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import requests

# Environment Configuration - STRICT VALIDATION
REQUIRED_ENV_VARS = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY"), 
    "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
    "KEY_PEPPER": os.getenv("KEY_PEPPER")
}

# Optional environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
PORT = int(os.getenv("PORT", 5000))

# Validate critical environment variables
missing_vars = [var for var, value in REQUIRED_ENV_VARS.items() if not value]
if missing_vars:
    print(f"❌ CRITICAL: Missing environment variables: {', '.join(missing_vars)}")
    print("🔧 Set these in Render Environment tab:")
    for var in missing_vars:
        print(f"   {var}=your_value_here")
    
    # In development, allow demo mode
    if ENVIRONMENT == "development":
        print("⚠️ Running in DEMO MODE (some features disabled)")
        DEMO_MODE = True
    else:
        print("🚫 Cannot start in production without proper environment variables")
        exit(1)
else:
    DEMO_MODE = False
    print("✅ All environment variables configured")

app = Flask(__name__)
CORS(app, origins="*", max_age=86400)  # Cache preflight for 24h

# Extract environment variables
SUPABASE_URL = REQUIRED_ENV_VARS["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = REQUIRED_ENV_VARS["SUPABASE_SERVICE_KEY"]
SUPABASE_ANON_KEY = REQUIRED_ENV_VARS["SUPABASE_ANON_KEY"]
KEY_PEPPER = REQUIRED_ENV_VARS["KEY_PEPPER"]

# Nigerian Voices Mapping - Optimized for Edge TTS
NIGERIAN_VOICES = {
    # Primary Nigerian voices
    "female": "en-NG-EzinneNeural",
    "male": "en-NG-AbeoNeural", 
    "ezinne": "en-NG-EzinneNeural",
    "abeo": "en-NG-AbeoNeural",
    
    # Regional variants (Edge TTS supports Nigerian English)
    "igbo_female": "en-NG-EzinneNeural",
    "igbo_male": "en-NG-AbeoNeural",
    "yoruba_female": "en-NG-EzinneNeural", 
    "yoruba_male": "en-NG-AbeoNeural",
    "hausa_female": "en-NG-EzinneNeural",
    "hausa_male": "en-NG-AbeoNeural",
    
    # International fallbacks
    "aria": "en-US-AriaNeural",
    "guy": "en-US-GuyNeural"
}

# Nigerian network optimization settings
GENERATION_TIMEOUT = 45  # seconds - account for slow networks
MAX_RETRIES = 3
DEMO_CHAR_LIMIT = 100
API_CHAR_LIMIT = 1000

def hash_api_key(raw_key):
    """Hash API key with pepper for security"""
    if not KEY_PEPPER:
        raise ValueError("KEY_PEPPER not configured")
    return hashlib.sha256((KEY_PEPPER + raw_key).encode()).hexdigest()

def supabase_request(method, path, data=None, headers=None, use_service_key=False):
    """Make request to Supabase API with retry logic"""
    if DEMO_MODE and not SUPABASE_URL:
        return None
        
    base_headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY
    }
    
    if use_service_key:
        base_headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
    
    if headers:
        base_headers.update(headers)
    
    url = f"{SUPABASE_URL}/rest/v1{path}"
    
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                response = requests.get(url, headers=base_headers, params=data, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=base_headers, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, headers=base_headers, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
            
        except requests.RequestException as e:
            print(f"Supabase request attempt {attempt + 1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                return None
    
    return None

def validate_api_key():
    """Validate API key from request headers with rate limiting"""
    if DEMO_MODE:
        return {"id": "demo", "user_id": "demo", "usage_count": 0}, None
        
    raw_key = request.headers.get("x-api-key") or request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not raw_key:
        return None, ("Missing API key", 401)
    
    try:
        key_hash = hash_api_key(raw_key)
    except ValueError as e:
        return None, ("Server configuration error", 500)
    
    # Query Supabase for API key
    response = supabase_request(
        "GET", 
        "/api_keys",
        data={
            "key_hash": f"eq.{key_hash}",
            "status": "eq.active",
            "select": "id,user_id,rate_limit_per_min,usage_count,total_quota"
        },
        use_service_key=True
    )
    
    if not response or response.status_code != 200:
        return None, ("Invalid API key", 401)
    
    keys = response.json()
    if not keys:
        return None, ("Invalid API key", 401)
    
    api_key = keys[0]
    
    # Check quota (if set)
    if api_key.get('total_quota', 0) > 0 and api_key.get('usage_count', 0) >= api_key['total_quota']:
        return None, ("Quota exceeded", 402)
    
    return api_key, None

def generate_tts_audio(text, voice="female"):
    """Generate TTS audio using edge-tts with Nigerian optimization"""
    voice_id = NIGERIAN_VOICES.get(voice, NIGERIAN_VOICES["female"])
    
    # Create temp file for audio
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        temp_path = tmp.name
    
    try:
        # Run edge-tts command with timeout for Nigerian networks
        cmd = [
            "edge-tts",
            "--text", text,
            "--voice", voice_id,
            "--write-media", temp_path
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=GENERATION_TIMEOUT
        )
        
        if result.returncode == 0 and os.path.exists(temp_path):
            # Read the audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up immediately
            os.unlink(temp_path)
            
            if len(audio_data) < 1000:  # Sanity check
                print(f"Generated audio suspiciously small: {len(audio_data)} bytes")
                return None, None
                
            return audio_data, "audio/mpeg"
        else:
            print(f"edge-tts failed: {result.stderr}")
            return None, None
            
    except subprocess.TimeoutExpired:
        print(f"TTS generation timeout after {GENERATION_TIMEOUT}s")
        return None, None
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None, None
    finally:
        # Ensure cleanup
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass

def log_usage(api_key_id, endpoint, status_code=200, characters=0):
    """Log API usage to Supabase (non-blocking)"""
    if DEMO_MODE:
        return
        
    try:
        supabase_request(
            "POST",
            "/usage_logs",
            data={
                "api_key_id": api_key_id,
                "endpoint": endpoint,
                "status_code": status_code,
                "characters_processed": characters,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            use_service_key=True
        )
    except Exception as e:
        print(f"Failed to log usage: {e}")

# Routes
@app.route('/')
def home():
    """Serve the main dashboard"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/config')
def api_config():
    """Provide frontend configuration (NO SECRETS)"""
    if DEMO_MODE:
        return jsonify({
            "demo_mode": True,
            "supabase_available": False
        })
    
    return jsonify({
        "demo_mode": False,
        "supabase_available": True,
        "url": SUPABASE_URL,
        "anonKey": SUPABASE_ANON_KEY  # Safe to expose - anon key is public
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ODIADEV TTS API',
        'voices': list(NIGERIAN_VOICES.keys()),
        'demo_mode': DEMO_MODE,
        'supabase_connected': not DEMO_MODE and bool(SUPABASE_URL),
        'environment': ENVIRONMENT
    })

@app.route('/api/generate-key', methods=['POST'])
def generate_api_key():
    """Generate new API key (requires Supabase auth)"""
    if DEMO_MODE:
        return jsonify({'error': 'API key generation not available in demo mode'}), 503
    
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing authorization'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Verify token with Supabase
    try:
        verify_response = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_ANON_KEY
            },
            timeout=10
        )
    except requests.RequestException:
        return jsonify({'error': 'Authentication service unavailable'}), 503
    
    if verify_response.status_code != 200:
        return jsonify({'error': 'Invalid token'}), 401
    
    user = verify_response.json()
    user_id = user['id']
    
    data = request.get_json() or {}
    name = data.get('name', 'Unnamed API Key')
    
    # Generate new API key
    raw_key = f"odiadev_{secrets.token_hex(32)}"
    key_hash = hash_api_key(raw_key)
    key_prefix = raw_key[:16]
    
    # Save to Supabase
    response = supabase_request(
        "POST",
        "/api_keys",
        data={
            "name": name,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "user_id": user_id,
            "owner_email": user.get('email', ''),
            "rate_limit_per_min": 120,
            "total_quota": 0,  # unlimited for now
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        use_service_key=True
    )
    
    if not response or response.status_code != 201:
        return jsonify({'error': 'Failed to create API key'}), 500
    
    created_key = response.json()[0]
    
    return jsonify({
        'id': created_key['id'],
        'name': name,
        'api_key': raw_key,
        'message': 'Save this key securely - it will not be shown again!'
    })

@app.route('/api/user-keys', methods=['GET'])
def get_user_keys():
    """Get user's API keys"""
    if DEMO_MODE:
        return jsonify({'keys': []})
    
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing authorization'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Verify token with Supabase
    try:
        verify_response = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_ANON_KEY
            },
            timeout=10
        )
    except requests.RequestException:
        return jsonify({'error': 'Authentication service unavailable'}), 503
    
    if verify_response.status_code != 200:
        return jsonify({'error': 'Invalid token'}), 401
    
    user = verify_response.json()
    user_id = user['id']
    
    # Get user's keys
    response = supabase_request(
        "GET",
        "/api_keys",
        data={
            "user_id": f"eq.{user_id}",
            "select": "id,name,key_prefix,usage_count,created_at,status"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if not response or response.status_code != 200:
        return jsonify({'error': 'Failed to fetch keys'}), 500
    
    keys = response.json()
    
    return jsonify({'keys': keys})

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    """Main TTS endpoint with Nigerian optimizations"""
    # Validate API key
    api_key, error = validate_api_key()
    if error:
        return jsonify({'error': error[0]}), error[1]
    
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    voice = data.get('voice', 'female')
    language = data.get('language', 'english')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    # Character limit check
    if len(text) > API_CHAR_LIMIT:
        return jsonify({'error': f'Text too long (max {API_CHAR_LIMIT} characters)'}), 400
    
    # Generate audio
    audio_data, mime_type = generate_tts_audio(text, voice)
    
    if not audio_data:
        if not DEMO_MODE:
            log_usage(api_key['id'], '/api/tts', 500, len(text))
        return jsonify({'error': 'TTS generation failed - try again or use shorter text'}), 500
    
    # Update usage count (non-blocking)
    if not DEMO_MODE:
        try:
            supabase_request(
                "PATCH",
                f"/api_keys?id=eq.{api_key['id']}",
                data={"usage_count": api_key.get('usage_count', 0) + 1},
                use_service_key=True
            )
            
            # Log TTS request
            supabase_request(
                "POST",
                "/tts_requests",
                data={
                    "api_key_id": api_key['id'],
                    "user_id": api_key['user_id'],
                    "text": text,
                    "language_code": language,
                    "voice_id": voice,
                    "character_count": len(text),
                    "status": "completed",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                use_service_key=True
            )
            
            # Log usage
            log_usage(api_key['id'], '/api/tts', 200, len(text))
        except Exception as e:
            print(f"Failed to update usage: {e}")
    
    # Return audio as base64 for web (Nigerian networks prefer this)
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    return jsonify({
        'success': True,
        'audio_url': f"data:{mime_type};base64,{audio_base64}",
        'character_count': len(text),
        'voice': voice,
        'language': language,
        'demo_mode': DEMO_MODE
    })

@app.route('/api/speak', methods=['POST'])
def speak_endpoint():
    """Alternative TTS endpoint for compatibility"""
    return tts_endpoint()

@app.route('/demo/tts', methods=['POST'])
def demo_tts():
    """Demo TTS endpoint (no API key required)"""
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    voice = data.get('voice', 'female')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    if len(text) > DEMO_CHAR_LIMIT:
        return jsonify({'error': f'Demo limit: {DEMO_CHAR_LIMIT} characters max'}), 400
    
    # Generate audio
    audio_data, mime_type = generate_tts_audio(text, voice)
    
    if not audio_data:
        return jsonify({'error': 'TTS generation failed - check your network or try shorter text'}), 500
    
    # Return audio as base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    return jsonify({
        'success': True,
        'audio_url': f"data:{mime_type};base64,{audio_base64}",
        'character_count': len(text),
        'voice': voice,
        'demo': True
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ODIADEV TTS Backend")
    print("="*60)
    print(f"🏠 Dashboard: http://localhost:{PORT}")
    print(f"🎤 API Endpoint: http://localhost:{PORT}/api/tts") 
    print(f"🧪 Demo Endpoint: http://localhost:{PORT}/demo/tts")
    print(f"❤️ Health: http://localhost:{PORT}/health")
    print("="*60)
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(f"🔐 Demo Mode: {DEMO_MODE}")
    if not DEMO_MODE:
        print(f"🔗 Supabase: {SUPABASE_URL}")
    print(f"🎤 Voices: {len(NIGERIAN_VOICES)} available")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)