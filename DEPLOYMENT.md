# 🔧 Deployment Error Fix Guide

## Error: "installer returned a non-zero exit code"

This error occurs during Streamlit Cloud deployment when dependencies fail to install.

## ✅ SOLUTION - Updated requirements.txt

I've created **3 versions** of requirements.txt. Use them in this order:

### Option 1: Minimal (Recommended for Streamlit Cloud) ⭐
**File: `requirements.txt` (already updated)**

```
streamlit
sentence-transformers
scikit-learn
pandas
```

This version:
- ✅ Lets pip auto-resolve compatible versions
- ✅ Works on Streamlit Cloud free tier
- ✅ Installs in ~3-5 minutes
- ✅ ~500MB total size

### Option 2: With Version Ranges (If Option 1 fails)
**File: `requirements-with-versions.txt`**

```
streamlit>=1.28.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
pandas>=2.0.0
```

### Option 3: Exact Versions (For local development)
**File: `requirements-exact.txt`**

```
streamlit==1.31.0
sentence-transformers==2.3.1
torch==2.1.2
numpy==1.24.3
scikit-learn==1.3.2
pandas==2.1.4
```

---

## 🚀 How to Fix Your Deployment

### Step 1: Update Your GitHub Repository

**Replace your requirements.txt with the minimal version:**

```bash
# In your local project folder
# Delete old requirements.txt
rm requirements.txt

# Copy the new one (it's already in your downloads)
# Or create it manually with these 4 lines:
echo "streamlit" > requirements.txt
echo "sentence-transformers" >> requirements.txt
echo "scikit-learn" >> requirements.txt
echo "pandas" >> requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Fix: Updated requirements.txt for Streamlit Cloud"
git push origin main
```

### Step 2: Redeploy on Streamlit Cloud

**Streamlit Cloud auto-deploys when you push to GitHub!**

1. Wait 30 seconds for GitHub to process your push
2. Go to your Streamlit Cloud dashboard: https://share.streamlit.io
3. Your app will automatically start redeploying
4. Watch the logs - should succeed in 3-5 minutes

**OR manually trigger redeploy:**

1. Go to your app dashboard
2. Click the ⋮ menu (three dots)
3. Click "Reboot app"
4. Wait for deployment

---

## 📊 Deployment Timeline

```
✅ Push to GitHub                    (30 seconds)
✅ Streamlit detects change          (30 seconds)
✅ Install dependencies              (3-5 minutes)
   ├─ streamlit                     (~1 min)
   ├─ sentence-transformers         (~2 min)
   ├─ scikit-learn                  (~1 min)
   └─ pandas                        (~30 sec)
✅ Download AI model                 (~1 minute)
✅ App starts                        (~30 seconds)

Total: 5-8 minutes
```

---

## 🐛 Common Errors & Solutions

### Error 1: Memory Limit Exceeded
```
Error: Your app has exceeded the memory limit
```

**Solution:**
```python
# Add to app.py at the top
import streamlit as st
st.set_page_config(layout="wide")

# Reduce max_suggestions default
max_suggestions = st.slider("Max suggestions", 5, 15, 10)  # Changed from 15 to 10
```

### Error 2: Torch Installation Timeout
```
Error: Could not install torch
```

**Solution:** Remove version constraints (already done in new requirements.txt)

### Error 3: Model Download Fails
```
Error downloading sentence-transformers model
```

**Solution:** Model downloads automatically on first run. Just wait or redeploy.

---

## 🔍 Check Deployment Logs

**To see detailed error messages:**

1. Go to https://share.streamlit.io
2. Click on your app
3. Look at the right side: "Logs" section
4. Find the exact error line

**Common log messages:**

```
✅ "Collecting streamlit"              - Installing dependencies
✅ "Successfully installed"            - Dependencies installed
✅ "Downloading model"                 - AI model downloading
✅ "You can now view your app"         - SUCCESS!

❌ "ERROR: Could not install"          - Dependency conflict
❌ "MemoryError"                       - Out of memory
❌ "TimeoutError"                      - Installation too slow
```

---

## 💡 Prevention Tips

### For Streamlit Cloud Deployment

**DO:**
- ✅ Use minimal requirements (no version numbers)
- ✅ Test locally first
- ✅ Keep repository clean
- ✅ Use .gitignore properly

**DON'T:**
- ❌ Pin exact versions unless necessary
- ❌ Include large files in repo
- ❌ Use GPU-specific packages
- ❌ Commit virtual environments

---

## 🆘 Still Not Working?

### Try These Steps in Order:

**1. Clear Streamlit Cache**
```
Dashboard → Your App → ⋮ → Clear cache
```

**2. Completely Redeploy**
```
Dashboard → Your App → ⋮ → Delete app
Then: New app → Select repository again
```

**3. Check Python Version**
Streamlit Cloud uses Python 3.9-3.11. Your code should work on these versions.

**4. Test Locally First**
```bash
# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install from new requirements.txt
pip install -r requirements.txt

# Test
streamlit run app.py

# If works locally, will work on cloud
```

---

## 📞 Get Help

**If still failing after trying all solutions:**

1. **Check Streamlit Status**
   - Go to: https://status.streamlit.io
   - See if there are platform issues

2. **Post on Forum**
   - Go to: https://discuss.streamlit.io
   - Title: "Deployment Error: installer returned non-zero exit code"
   - Include: Your requirements.txt and error logs

3. **GitHub Issue**
   - Check: https://github.com/streamlit/streamlit/issues
   - Search for similar errors

---

## ✅ Verification Checklist

After updating requirements.txt, verify:

- [ ] Only 4 lines in requirements.txt
- [ ] No version numbers (just package names)
- [ ] Committed to GitHub
- [ ] Pushed to main branch
- [ ] Streamlit Cloud detected change
- [ ] Logs show "Successfully installed"
- [ ] App starts without errors

---

## 🎯 Expected Success

With the new **minimal requirements.txt**, you should see:

```
[Logs]
Collecting streamlit
  Downloading streamlit-1.32.0...
Successfully installed streamlit-1.32.0

Collecting sentence-transformers
  Downloading sentence_transformers-2.5.1...
Successfully installed sentence-transformers-2.5.1

Collecting scikit-learn
  Downloading scikit_learn-1.4.0...
Successfully installed scikit-learn-1.4.0

Collecting pandas
  Downloading pandas-2.2.0...
Successfully installed pandas-2.2.0

Installing dependencies... ✅
Starting app... ✅
Downloading model 'all-MiniLM-L6-v2'... ✅
Your app is now running! ✅
```

Then your app will be live at:
```
https://YOUR_USERNAME-internal-link-suggester.streamlit.app
```

---

## 📝 Summary

**What Changed:**
- Old: 6 packages with exact versions
- New: 4 packages without version constraints

**Why This Fixes It:**
- Streamlit Cloud can auto-select compatible versions
- Reduces dependency conflicts
- Faster installation
- Better compatibility

**Next Steps:**
1. Use new requirements.txt
2. Push to GitHub
3. Wait 5-8 minutes
4. App should deploy successfully ✅

---

**Your deployment should work now! 🚀**

Questions? Check the logs and refer back to this guide.
