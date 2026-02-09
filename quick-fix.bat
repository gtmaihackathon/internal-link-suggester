@echo off
REM Quick Fix Script for Streamlit Cloud Deployment Error (Windows)
REM Run this to fix the "installer returned a non-zero exit code" error

echo ========================================
echo 🔧 Streamlit Cloud Deployment Fix
echo ========================================
echo.

REM Check if we're in a git repository
if not exist .git (
    echo ❌ Error: Not in a git repository
    echo Please run this script from your project root directory
    pause
    exit /b 1
)

echo ✅ Git repository detected
echo.

REM Backup old requirements.txt
if exist requirements.txt (
    echo 📦 Backing up old requirements.txt...
    copy requirements.txt requirements-backup.txt >nul
    echo ✅ Backup saved as requirements-backup.txt
) else (
    echo ⚠️  No existing requirements.txt found
)
echo.

REM Create new minimal requirements.txt
echo 📝 Creating new requirements.txt...
(
echo streamlit
echo sentence-transformers
echo scikit-learn
echo pandas
) > requirements.txt

echo ✅ New requirements.txt created with 4 packages
echo.

REM Show the new file
echo 📄 New requirements.txt content:
echo ================================
type requirements.txt
echo ================================
echo.

REM Ask to commit and push
set /p confirm="🚀 Ready to commit and push to GitHub? (y/n): "

if /i "%confirm%"=="y" (
    echo 📤 Adding changes...
    git add requirements.txt
    
    echo 💾 Committing...
    git commit -m "Fix: Updated requirements.txt for Streamlit Cloud compatibility"
    
    echo 🚀 Pushing to GitHub...
    git push origin main
    
    echo.
    echo ✅ SUCCESS!
    echo ================================
    echo Changes pushed to GitHub
    echo.
    echo Next steps:
    echo 1. Wait 30 seconds
    echo 2. Go to https://share.streamlit.io
    echo 3. Your app will auto-redeploy
    echo 4. Wait 5-8 minutes for deployment
    echo.
    echo 🎉 Your app should now deploy successfully!
) else (
    echo.
    echo ❌ Cancelled
    echo You can manually commit later with:
    echo   git add requirements.txt
    echo   git commit -m "Fix: Update requirements.txt"
    echo   git push origin main
)

echo.
echo 📚 For more help, see DEPLOYMENT_FIX.md
echo.
pause
