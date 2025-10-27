# Deployment Guide for HEIC to PNG Converter

## ⚠️ Why Netlify Doesn't Work

**Netlify is for static sites only.** Your Flask application needs a server that can:
- Run Python code continuously
- Process uploaded files
- Handle dynamic requests

Netlify only serves static HTML/CSS/JS files and serverless functions (which have strict limits).

## ✅ Recommended Platforms (Free Options Available)

Here are the best platforms for deploying this Flask app, ranked by ease of use:

---

## Option 1: Render.com (Recommended) ⭐

**Pros:** Free tier, automatic deployments, very easy setup
**Cons:** Free tier spins down after inactivity (15 min to restart)

### Deploy to Render:

1. **Create a Render account** at https://render.com

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Name:** heic-converter (or your choice)
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
     - **Instance Type:** Free

3. **Click "Create Web Service"**

4. Your app will be live at `https://heic-converter.onrender.com` (or your chosen name)

**Note:** The free tier sleeps after 15 minutes of inactivity, so first load may take 30-60 seconds.

---

## Option 2: Railway.app

**Pros:** Simple deployment, generous free tier, fast
**Cons:** Free tier credit limit ($5/month)

### Deploy to Railway:

1. **Create account** at https://railway.app

2. **Click "New Project"** → "Deploy from GitHub repo"

3. **Select your repository**

4. **Railway will auto-detect settings** from `railway.json`

5. **Add environment variables if needed** (none required for basic setup)

6. Your app will be automatically deployed!

---

## Option 3: Heroku

**Pros:** Well-documented, reliable
**Cons:** No free tier anymore (minimum $5/month)

### Deploy to Heroku:

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from heroku.com
   ```

2. **Login and create app:**
   ```bash
   heroku login
   heroku create heic-converter-app
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

4. **Open your app:**
   ```bash
   heroku open
   ```

---

## Option 4: PythonAnywhere

**Pros:** Python-specific, good free tier
**Cons:** More manual configuration required

### Deploy to PythonAnywhere:

1. **Create account** at https://www.pythonanywhere.com

2. **Upload your code** via Git or file upload

3. **Install dependencies** in a Bash console:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Web app:**
   - Go to "Web" tab
   - Add a new web app
   - Choose Flask
   - Set WSGI configuration to point to your app

5. **Reload the web app**

---

## Option 5: Fly.io

**Pros:** Modern platform, good free tier
**Cons:** Requires Docker knowledge

### Deploy to Fly.io:

1. **Install flyctl CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create Dockerfile** (or I can create one for you)

3. **Deploy:**
   ```bash
   fly launch
   fly deploy
   ```

---

## 🔧 Local Development

For local testing (always works):

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Visit http://localhost:5000
```

---

## 📋 Quick Comparison

| Platform | Free Tier | Ease of Setup | Speed | Best For |
|----------|-----------|---------------|-------|----------|
| **Render** | ✅ Yes (sleeps) | ⭐⭐⭐⭐⭐ | Fast | Quick deploy |
| **Railway** | ✅ $5 credit | ⭐⭐⭐⭐⭐ | Very Fast | Personal use |
| **Heroku** | ❌ $5/month | ⭐⭐⭐⭐ | Fast | Production |
| **PythonAnywhere** | ✅ Yes (limited) | ⭐⭐⭐ | Medium | Python-focused |
| **Fly.io** | ✅ Yes (limited) | ⭐⭐ | Very Fast | Advanced users |

---

## 🚀 My Recommendation

**For you: Use Render.com**

1. Push your code to GitHub
2. Connect to Render
3. Done! (literally 2 minutes)

The free tier is perfect for personal use and testing. The app "sleeps" after 15 minutes of no use, but wakes up automatically when someone visits.

---

## Need Help?

If you run into issues with any platform, let me know which one you chose and I can help troubleshoot!
