# 🎤 ODIA.dev - Nigerian TTS Platform

## ✅ INSTANT DEPLOYMENT (2 Minutes!)

### Step 1: Update Your GitHub
```bash
# Copy these 4 files to your repo folder:
# - app.py
# - requirements.txt
# - render.yaml
# - README.md

# Then run:
git add .
git commit -m "Ready to deploy ODIA.dev"
git push
```

### Step 2: Deploy on Render
1. Go to **[Render.com](https://dashboard.render.com)**
2. Click **"New +" → "Web Service"**
3. Connect your repo: **Odiabackend099/odiadev-tts**
4. Click **"Create Web Service"**
5. **DONE!** Wait 2-3 minutes for deployment

## 🌐 Your Live App

Once deployed, your app will be at:
```
https://odia-tts-platform.onrender.com
```

## 🎯 Features

- ✅ **9 Nigerian Languages** - English, Yoruba, Hausa, Igbo, etc.
- ✅ **18 Voice Options** - Male & Female for each language
- ✅ **Beautiful Dashboard** - Professional gradient UI
- ✅ **API Access** - Generate API keys instantly
- ✅ **No Database Needed** - Works immediately
- ✅ **Free Hosting** - Runs on Render free tier

## 📱 Test Your API

```python
import requests

# Your deployed app URL
url = "https://odia-tts-platform.onrender.com/api/speak"

response = requests.post(url, json={
    "text": "Hello Nigeria!",
    "voice": "female"
})

# Save the audio
with open("speech.mp3", "wb") as f:
    f.write(response.content)
```

## 🚨 Troubleshooting

If audio generation fails:
1. Wait 30 seconds and try again (server might be waking up)
2. Use shorter text (under 500 characters)
3. Try the default "female" voice first

## 💡 That's It!

No database setup, no complex configuration. Just deploy and use!

---
**ODIA.dev** - Voice Technology for Nigeria 🇳🇬
