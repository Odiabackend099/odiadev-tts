#!/usr/bin/env python3
"""
ODIADEV TTS API - Production Ready for Render
Nigerian Voice Technology Platform
"""

import os
import subprocess
import tempfile
import time
import secrets
import hashlib
from datetime import datetime, timezone
from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration from environment variables
PORT = int(os.getenv("PORT", "5000"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./odiadev.db")
SECRET_KEY = os.getenv("SECRET_KEY", "odiadev-secret-key-2025")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "odiadev-admin-2025")

# Fix for Render PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config.update(
    SQLALCHEMY_DATABASE_URI=DATABASE_URL,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=SECRET_KEY
)

CORS(app, origins="*")
db = SQLAlchemy(app)

# Nigerian Voices
VOICES = {
    "female": "en-NG-EzinneNeural",
    "male": "en-NG-AbeoNeural",
    "ezinne": "en-NG-EzinneNeural", 
    "abeo": "en-NG-AbeoNeural",
    "lexi": "en-US-AriaNeural",
    "atlas": "en-US-GuyNeural"
}

# Database Models
class APIKey(db.Model):
    __tablename__ = "api_keys"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    key_hash = db.Column(db.String(64), nullable=False, unique=True)
    key_prefix = db.Column(db.String(16), nullable=False)
    usage_count = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Initialize database
with app.app_context():
    db.create_all()

def generate_tts_cli(text, voice="female"):
    """Generate TTS using edge-tts CLI (most reliable method)"""
    voice_id = VOICES.get(voice, VOICES["female"])
    
    # Create unique temp file
    timestamp = str(int(time.time() * 1000))
    temp_file = f"/tmp/temp_audio_{timestamp}.mp3"
    
    try:
        print(f"🎤 Generating: '{text[:50]}...' with {voice_id}")
        
        # Run edge-tts command
        cmd = [
            "edge-tts",
            "--text", text,
            "--voice", voice_id,
            "--write-media", temp_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and os.path.exists(temp_file):
            # Read the audio file
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
            
            print(f"✅ Generated {len(audio_data)} bytes of audio")
            return audio_data
        else:
            print(f"❌ edge-tts failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout - edge-tts took too long")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        # Clean up temp file if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

# Beautiful HTML Dashboard (the UI you like)
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>ODIADEV TTS Platform</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .tagline {
            font-size: 18px;
            opacity: 0.9;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        h2 {
            margin-bottom: 20px;
            color: #fff;
        }
        textarea, select, button {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }
        textarea, select {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }
        button {
            background: #4CAF50;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        audio {
            width: 100%;
            margin-top: 15px;
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            text-align: center;
        }
        .success { background: rgba(76, 175, 80, 0.2); }
        .error { background: rgba(244, 67, 54, 0.2); }
        .info { background: rgba(33, 150, 243, 0.2); }
        pre {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 14px;
        }
        .voice-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        .voice-btn {
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        .voice-btn:hover, .voice-btn.active {
            background: rgba(255, 255, 255, 0.2);
            border-color: #4CAF50;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎤 ODIADEV</div>
            <div class="tagline">Nigerian Language Text-to-Speech Platform</div>
        </div>
        
        <div class="card">
            <h2>Voice Synthesis Studio</h2>
            <textarea id="text" rows="4" placeholder="Enter text to convert to speech...">Welcome to ODIADEV! Nigeria's premier voice technology platform.</textarea>
            
            <div class="voice-grid">
                <div class="voice-btn active" onclick="selectVoice(this, 'female')">
                    <strong>Ezinne</strong><br>
                    <small>Nigerian Female</small>
                </div>
                <div class="voice-btn" onclick="selectVoice(this, 'male')">
                    <strong>Abeo</strong><br>
                    <small>Nigerian Male</small>
                </div>
                <div class="voice-btn" onclick="selectVoice(this, 'lexi')">
                    <strong>Lexi</strong><br>
                    <small>WhatsApp Style</small>
                </div>
                <div class="voice-btn" onclick="selectVoice(this, 'atlas')">
                    <strong>Atlas</strong><br>
                    <small>Professional</small>
                </div>
            </div>
            
            <button onclick="generateSpeech()">🔊 Generate Speech</button>
            <div id="status"></div>
            <audio id="player" controls style="display:none;"></audio>
        </div>
        
        <div class="card">
            <h2>Quick Test</h2>
            <button onclick="testAudio()">🎵 Play Test Audio</button>
            <p style="margin-top: 10px; opacity: 0.9;">Click to hear a sample of ODIADEV TTS</p>
        </div>
        
        <div class="card">
            <h2>API Usage</h2>
            <pre>
# Python Example
import requests

response = requests.post(
    "https://your-app.onrender.com/speak",
    json={
        "text": "Hello from ODIADEV!",
        "voice": "female"  # or male, lexi, atlas
    }
)

# Save the audio
with open("odiadev_speech.mp3", "wb") as f:
    f.write(response.content)

# cURL Example
curl -X POST https://your-app.onrender.com/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello ODIADEV","voice":"male"}' \
  --output speech.mp3
            </pre>
        </div>
        
        <div class="card" style="text-align: center;">
            <p>© 2025 ODIADEV - Voice Technology for Africa</p>
        </div>
    </div>
    
    <script>
        let selectedVoice = 'female';
        
        function selectVoice(btn, voice) {
            document.querySelectorAll('.voice-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedVoice = voice;
        }
        
        async function generateSpeech() {
            const text = document.getElementById('text').value;
            const status = document.getElementById('status');
            const player = document.getElementById('player');
            
            if (!text) {
                status.innerHTML = '<div class="status error">Please enter some text!</div>';
                return;
            }
            
            status.innerHTML = '<div class="status info">🎵 Generating speech...</div>';
            
            try {
                const response = await fetch('/speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, voice: selectedVoice})
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    player.src = URL.createObjectURL(blob);
                    player.style.display = 'block';
                    player.play();
                    status.innerHTML = '<div class="status success">✅ Speech generated successfully!</div>';
                } else {
                    status.innerHTML = '<div class="status error">❌ Failed to generate speech</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="status error">❌ Error: ' + error + '</div>';
            }
        }
        
        async function testAudio() {
            window.open('/test-audio', '_blank');
        }
    </script>
</body>
</html>
'''

@app.route("/")
def home():
    return HTML

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ODIADEV TTS Platform",
        "voices": list(VOICES.keys()),
        "environment": "production" if os.getenv("RENDER") else "development"
    })

@app.route("/speak", methods=["GET", "POST"])
def speak():
    """Generate TTS audio"""
    if request.method == "POST":
        data = request.get_json() or {}
        text = data.get("text", "")
        voice = data.get("voice", "female")
    else:
        text = request.args.get("text", "")
        voice = request.args.get("voice", "female")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Generate audio using CLI (most reliable)
    audio_data = generate_tts_cli(text, voice)
    
    if audio_data:
        return Response(
            audio_data,
            mimetype="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Cache-Control": "no-cache"
            }
        )
    else:
        return jsonify({"error": "TTS generation failed"}), 500

@app.route("/test-audio")
def test_audio():
    """Generate a test audio file"""
    test_text = "Welcome to ODIADEV! This is a test of the Nigerian Text-to-Speech system."
    
    audio_data = generate_tts_cli(test_text, "female")
    
    if audio_data:
        return Response(
            audio_data,
            mimetype="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Content-Disposition": "inline; filename=odiadev_test.mp3"
            }
        )
    else:
        return jsonify({"error": "Test audio generation failed"}), 500

@app.route("/api/create-key", methods=["POST"])
def create_api_key():
    """Create a new API key (admin only)"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    name = data.get("name", "API Key")
    
    key_id = secrets.token_hex(8)
    raw_key = "odiadev_" + secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    new_key = APIKey(
        id=key_id,
        name=name,
        key_hash=key_hash,
        key_prefix=raw_key[:12]
    )
    db.session.add(new_key)
    db.session.commit()
    
    return jsonify({
        "id": key_id,
        "name": name,
        "api_key": raw_key,
        "message": "Save this key securely!"
    })

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 ODIADEV TTS Platform")
    print("="*60)
    print(f"📍 Running on port: {PORT}")
    print(f"📍 Environment: {'Production' if os.getenv('RENDER') else 'Development'}")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
