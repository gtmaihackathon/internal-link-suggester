# 🚀 Deployment Guide

Complete step-by-step guide to deploy your Internal Link Suggester app.

## Option 1: Deploy to Streamlit Cloud (Recommended - FREE)

### Prerequisites
- GitHub account
- Git installed on your computer

### Step-by-Step Instructions

#### 1. Prepare Your Repository

**Create a new repository on GitHub:**
1. Go to [github.com](https://github.com)
2. Click the "+" icon → "New repository"
3. Name it: `internal-link-suggester`
4. Keep it Public (required for free Streamlit hosting)
5. Don't initialize with README (we already have files)
6. Click "Create repository"

**Push your code to GitHub:**
```bash
# Navigate to your project folder
cd path/to/internal-link-suggester

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Internal Link Suggester"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/internal-link-suggester.git

# Push to GitHub
git branch -M main
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud

**Sign up and deploy:**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up with GitHub"
3. Authorize Streamlit to access your GitHub
4. Click "New app"
5. Fill in the form:
   - **Repository**: `YOUR_USERNAME/internal-link-suggester`
   - **Branch**: `main`
   - **Main file path**: `app.py`
6. Click "Deploy!"

**Wait for deployment:**
- Initial deployment takes 3-5 minutes
- The AI model (~80MB) will be downloaded
- You'll see a progress bar

**Your app is live! 🎉**
- URL: `https://YOUR_USERNAME-internal-link-suggester.streamlit.app`
- Share this URL with anyone

#### 3. Post-Deployment

**Test your app:**
1. Add a few URLs to the database
2. Paste sample content
3. Generate suggestions
4. Accept/reject links
5. Download the final document

**Monitor usage:**
- Streamlit Cloud dashboard shows app usage
- Check logs if something goes wrong

---

## Option 2: Run Locally

### For Development and Testing

#### Windows

```bash
# Install Python 3.9 or higher
# Download from python.org

# Clone repository
git clone https://github.com/YOUR_USERNAME/internal-link-suggester.git
cd internal-link-suggester

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

#### Mac/Linux

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/internal-link-suggester.git
cd internal-link-suggester

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

**Access the app:**
- Open browser: `http://localhost:8501`

---

## Option 3: Deploy to Other Platforms

### Heroku

**1. Create `setup.sh`:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**2. Create `Procfile`:**
```
web: sh setup.sh && streamlit run app.py
```

**3. Deploy:**
```bash
heroku create your-app-name
git push heroku main
```

### Google Cloud Run

**1. Create `Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0
```

**2. Deploy:**
```bash
gcloud run deploy internal-link-suggester \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### AWS Elastic Beanstalk

**1. Install EB CLI:**
```bash
pip install awsebcli
```

**2. Initialize and deploy:**
```bash
eb init -p python-3.9 internal-link-suggester
eb create internal-link-env
eb deploy
```

---

## 🔧 Configuration

### Environment Variables

If you need to add environment variables on Streamlit Cloud:

1. Go to your app dashboard
2. Click "Settings"
3. Click "Secrets"
4. Add variables in TOML format:
```toml
# Example secrets
api_key = "your_api_key"
database_url = "your_db_url"
```

### Custom Domain

**Streamlit Cloud:**
1. App settings → General
2. Add custom domain
3. Configure DNS CNAME record

---

## 📊 Performance Optimization

### For Streamlit Cloud

**Free tier limits:**
- 1 GB RAM
- 1 CPU core
- Unlimited apps (public)

**Optimization tips:**
1. Use `@st.cache_resource` for model loading
2. Limit max_suggestions to 15
3. Keep URL database under 1000 entries
4. Use efficient data structures

### For High Traffic

If you expect >1000 users/day:
1. Upgrade to Streamlit Cloud Pro ($20/month)
2. Deploy to dedicated hosting
3. Add caching layer (Redis)
4. Implement rate limiting

---

## 🐛 Troubleshooting

### Common Issues

**1. Model download timeout**
```
Solution: Redeploy the app. First deployment might timeout.
```

**2. Memory errors**
```
Solution: Reduce max_suggestions or upgrade plan
```

**3. Database not persisting**
```
Solution: Check file permissions, ensure url_database.json is writable
```

**4. App crashes on large content**
```
Solution: Split content into smaller chunks (<5000 words)
```

### Debugging

**Check logs:**
- Streamlit Cloud: Dashboard → Logs
- Local: Check terminal output

**Enable debug mode:**
```python
# In app.py
import streamlit as st
st.set_option('client.showErrorDetails', True)
```

---

## 🔄 Updating Your App

### Deploy Updates

**Method 1: Push to GitHub**
```bash
git add .
git commit -m "Update: Added new features"
git push origin main
```
Streamlit Cloud auto-deploys on push!

**Method 2: Manual redeploy**
1. Go to app dashboard
2. Click "Reboot app"

---

## 📈 Monitoring

### Streamlit Cloud Analytics

**Available metrics:**
- Daily active users
- Session duration
- Error rates
- Resource usage

**Access analytics:**
1. App dashboard
2. Click "Analytics"
3. View charts and logs

### Custom Analytics

Add Google Analytics:
```python
# In app.py
st.components.v1.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", height=0)
```

---

## 💰 Cost Estimation

### Streamlit Cloud
- **Free tier**: $0/month
  - Unlimited public apps
  - 1 GB RAM per app
  - Community support

- **Pro tier**: $20/month
  - Private apps
  - 4 GB RAM
  - Priority support

### Other Platforms
- **Heroku**: $7-25/month
- **Google Cloud Run**: Pay-per-use (~$5-20/month)
- **AWS**: $10-50/month (depends on usage)

---

## 🔐 Security Best Practices

1. **Keep dependencies updated**
```bash
pip install --upgrade -r requirements.txt
```

2. **Don't commit secrets**
   - Use `.gitignore`
   - Use environment variables
   - Use Streamlit secrets

3. **Validate user input**
   - Already implemented in the app
   - Add rate limiting for production

4. **HTTPS only**
   - Streamlit Cloud provides free HTTPS
   - Configure SSL for custom domains

---

## 📞 Support

**Getting help:**
- 📧 GitHub Issues
- 💬 Streamlit Community Forum
- 📖 Streamlit Documentation

**Useful links:**
- [Streamlit Docs](https://docs.streamlit.io)
- [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Community Forum](https://discuss.streamlit.io)

---

## ✅ Deployment Checklist

Before going live:

- [ ] Test all features locally
- [ ] Add sample data
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Test deployed app
- [ ] Add custom domain (optional)
- [ ] Set up monitoring
- [ ] Share URL with users
- [ ] Gather feedback
- [ ] Iterate and improve

---

**Need help? Open an issue on GitHub!**

Happy deploying! 🚀
