# 🎤 ODIADEV TTS Platform

Nigerian Language Text-to-Speech API Platform powered by Microsoft Edge TTS

## 🚀 Deploy to Render via GitHub

### Step 1: Create GitHub Repository

1. Create a new repository on GitHub (e.g., `odiadev-tts`)
2. Clone it locally:
```bash
git clone https://github.com/YOUR_USERNAME/odiadev-tts.git
cd odiadev-tts
```

### Step 2: Add Project Files

Add these files to your repository:
- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `.gitignore` - Git ignore file
- `runtime.txt` - Python version (optional)
- `README.md` - This file

### Step 3: Initial Commit & Push

```bash
git add .
git commit -m "Initial ODIADEV TTS deployment"
git push origin main
```

### Step 4: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Render will auto-detect the configuration from `render.yaml`
5. Click **Create Web Service**

### Step 5: Environment Variables (Optional)

After deployment, go to your service's **Environment** tab and add:

- `SECRET_KEY`: (auto-generated)
- `ADMIN_TOKEN`: (auto-generated)

### Step 6: Database Setup (Optional)

If you need persistent API keys:
1. Create a PostgreSQL database on Render
2. Copy the Internal Database URL
3. Add it as `DATABASE_URL` environment variable

## 🔗 API Endpoints

Once deployed, your API will be available at:
```
https://odiadev-tts.onrender.com
```

### Endpoints:
- `GET /` - Web dashboard
- `GET /health` - Health check
- `POST /speak` - Generate TTS audio
- `GET /test-audio` - Test audio sample

### API Usage:

```python
import requests

response = requests.post(
    "https://odiadev-tts.onrender.com/speak",
    json={
        "text": "Hello from ODIADEV!",
        "voice": "female"  # Options: female, male, lexi, atlas
    }
)

with open("speech.mp3", "wb") as f:
    f.write(response.content)
```

## 🎤 Available Voices

| Voice | Description | Voice ID |
|-------|-------------|----------|
| female | Nigerian Female (Ezinne) | en-NG-EzinneNeural |
| male | Nigerian Male (Abeo) | en-NG-AbeoNeural |
| lexi | American Female | en-US-AriaNeural |
| atlas | American Male | en-US-GuyNeural |

## 🔄 Continuous Deployment

Any push to the `main` branch will automatically deploy to Render!

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main
# Auto-deploys to Render!
```

## 🛠️ Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/odiadev-tts.git
cd odiadev-tts

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Visit http://localhost:5000

## 📝 Notes

- Free Render tier may sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- For production, consider upgrading to paid tier

## 🤝 Support

For issues or questions, create an issue on GitHub.

---

**ODIADEV** - Voice Technology for Africa 🇳🇬