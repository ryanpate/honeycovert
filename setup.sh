#!/bin/bash

echo "🚀 HEIC to PNG Converter - Quick Setup"
echo "======================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: HEIC to PNG converter"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "🎯 Next Steps:"
echo ""
echo "Option 1 - Deploy to Render.com (Recommended, Free):"
echo "  1. Push to GitHub: git remote add origin YOUR_GITHUB_URL"
echo "  2. Push: git push -u origin main"
echo "  3. Go to https://render.com → New Web Service"
echo "  4. Connect your GitHub repo"
echo "  5. Done! Your app will be live in 2-3 minutes"
echo ""
echo "Option 2 - Deploy to Railway (Free $5 credit):"
echo "  1. Push to GitHub (same as above)"
echo "  2. Go to https://railway.app → New Project"
echo "  3. Select 'Deploy from GitHub'"
echo "  4. Choose your repo"
echo "  5. Done! Auto-deployed"
echo ""
echo "Option 3 - Run Locally:"
echo "  1. Install: pip install -r requirements.txt"
echo "  2. Run: python app.py"
echo "  3. Visit: http://localhost:5000"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
