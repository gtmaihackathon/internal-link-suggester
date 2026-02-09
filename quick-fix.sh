#!/bin/bash

# Quick Fix Script for Streamlit Cloud Deployment Error
# Run this to fix the "installer returned a non-zero exit code" error

echo "🔧 Streamlit Cloud Deployment Fix"
echo "=================================="
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from your project root directory"
    exit 1
fi

echo "✅ Git repository detected"
echo ""

# Backup old requirements.txt
if [ -f requirements.txt ]; then
    echo "📦 Backing up old requirements.txt..."
    cp requirements.txt requirements-backup.txt
    echo "✅ Backup saved as requirements-backup.txt"
else
    echo "⚠️  No existing requirements.txt found"
fi
echo ""

# Create new minimal requirements.txt
echo "📝 Creating new requirements.txt..."
cat > requirements.txt << EOF
streamlit
sentence-transformers
scikit-learn
pandas
EOF

echo "✅ New requirements.txt created with 4 packages"
echo ""

# Show the new file
echo "📄 New requirements.txt content:"
echo "================================"
cat requirements.txt
echo "================================"
echo ""

# Ask to commit and push
read -p "🚀 Ready to commit and push to GitHub? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Adding changes..."
    git add requirements.txt
    
    echo "💾 Committing..."
    git commit -m "Fix: Updated requirements.txt for Streamlit Cloud compatibility"
    
    echo "🚀 Pushing to GitHub..."
    git push origin main
    
    echo ""
    echo "✅ SUCCESS!"
    echo "================================"
    echo "Changes pushed to GitHub"
    echo ""
    echo "Next steps:"
    echo "1. Wait 30 seconds"
    echo "2. Go to https://share.streamlit.io"
    echo "3. Your app will auto-redeploy"
    echo "4. Wait 5-8 minutes for deployment"
    echo ""
    echo "🎉 Your app should now deploy successfully!"
else
    echo ""
    echo "❌ Cancelled"
    echo "You can manually commit later with:"
    echo "  git add requirements.txt"
    echo "  git commit -m 'Fix: Update requirements.txt'"
    echo "  git push origin main"
fi

echo ""
echo "📚 For more help, see DEPLOYMENT_FIX.md"
