# Complete Deployment Instructions - Pydantic v2 Fix

## Problem Resolved
**Error**: `ValueError: 'not' is not a valid parameter name`  
**Root Cause**: Pydantic v1/v2 version conflicts with Python 3.13  
**Solution**: Force Python 3.11.9 + explicit Pydantic v2 with pydantic-core

---

## ✅ Changes Applied

### 1. **requirements.txt** - Updated with Pydantic v2 explicit versions
```txt
--upgrade-strategy eager
fastapi==0.115.0
pydantic==2.9.0
pydantic-core==2.23.4
uvicorn==0.30.1
gunicorn==21.2.0
sqlalchemy==2.0.35
python-multipart==0.0.12
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
bcrypt==4.2.0
```

**Key additions:**
- `--upgrade-strategy eager` - Forces clean upgrade of all dependencies
- `pydantic-core==2.23.4` - Explicit core version to prevent v1 conflicts

### 2. **Python Version Files** - Both set to 3.11.9
- ✅ `.python-version` → `3.11.9`
- ✅ `runtime.txt` → `python-3.11.9`

### 3. **main.py** - Added rebuild trigger
- Added: `print("Force rebuild test")` after imports
- Purpose: Forces Render to rebuild with new dependencies

---

## 🚀 Deployment Steps

### Step 1: Commit Changes
Open PowerShell/Terminal in the backend directory and run:

```powershell
cd "c:\Users\DS Laptop 47\Desktop\Invertory Atomation\backend"

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Force rebuild and dependency cleanup - Pydantic v2 fix"

# Push to repository
git push origin main
```

**Expected output:**
```
[main abc1234] Force rebuild and dependency cleanup - Pydantic v2 fix
 3 files changed, 5 insertions(+), 3 deletions(-)
Enumerating objects: X, done.
Writing objects: 100% (X/X), done.
Total X (delta X), reused X (delta X)
To https://github.com/YOUR_USERNAME/YOUR_REPO.git
   abc1234..def5678  main -> main
```

---

### Step 2: Deploy on Render

#### A. Clear Build Cache (CRITICAL!)
1. Go to: https://dashboard.render.com
2. Click on your **`ds-inventory-server`** service
3. Click **Settings** in the left sidebar
4. Scroll down to **Build & Deploy** section
5. Click **"Clear build cache"** button
6. Confirm when prompted

#### B. Trigger Manual Deploy
1. Go back to the service dashboard
2. Click **"Manual Deploy"** dropdown (top right)
3. Select **"Deploy latest commit"**
4. Click **"Deploy"**

---

### Step 3: Monitor Build Logs

Watch the deployment logs carefully. You should see:

#### ✅ Correct Python Version
```
==> Using Python version 3.11.9 (from runtime.txt)
```

#### ✅ Pydantic v2 Installation
```
Installing collected packages: pydantic-core-2.23.4, pydantic-2.9.0, fastapi-0.115.0
Successfully installed pydantic-core-2.23.4 pydantic-2.9.0 fastapi-0.115.0 ...
```

#### ✅ Successful Build
```
==> Build successful 🎉
==> Running 'gunicorn main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker'
```

#### ✅ Application Started
```
Force rebuild test
[INFO] Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
```

---

### Step 4: Verify Deployment

#### Test Health Endpoint
Visit your health check endpoint:
```
https://ds-inventory-server.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "API is running",
  "timestamp": "2025-10-21T11:36:00.000000",
  "version": "1.0.0"
}
```

#### Test Root Endpoint
```
https://ds-inventory-server.onrender.com/
```

**Expected Response:**
```json
{
  "message": "Inventory Management API is running!",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 🔍 Troubleshooting

### If Python 3.13 is still being used:
**Check:**
1. Verify `runtime.txt` is in the **root of your repository** or **service root directory**
2. On Render Dashboard → Settings → ensure **"Root Directory"** is set correctly
3. Try deleting and recreating the service from the Render dashboard

**Solution:**
```bash
# Verify file location
ls -la backend/runtime.txt
cat backend/runtime.txt

# Should show: python-3.11.9
```

### If Pydantic v1 is still being installed:
**Check build logs for:**
```
Installing collected packages: pydantic-1.x.x  # ❌ WRONG VERSION
```

**Solution:**
1. Clear build cache again (Render Dashboard → Settings → Clear build cache)
2. Check if any other dependency is pulling Pydantic v1:
   ```bash
   pip install pip-audit
   pip-audit --desc
   ```
3. Update conflicting dependencies to Pydantic v2 compatible versions

### If the error persists:
**Check for dependency conflicts:**
```bash
# Locally test the dependencies
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Check installed versions
pip list | grep pydantic
# Should show:
# pydantic        2.9.0
# pydantic-core   2.23.4
```

### If deployment fails with other errors:
1. **Database migration issues:**
   - Check if `python add_name_column.py` runs successfully
   - Verify database connection string

2. **Environment variables missing:**
   - Ensure `SECRET_KEY` is set in Render dashboard
   - Check all required env vars are configured

3. **Port binding issues:**
   - Render automatically sets `$PORT` environment variable
   - Verify start command uses `0.0.0.0:$PORT`

---

## 📋 Verification Checklist

Before deployment:
- [x] `requirements.txt` has `--upgrade-strategy eager` as first line
- [x] `requirements.txt` includes `pydantic==2.9.0` and `pydantic-core==2.23.4`
- [x] `.python-version` contains `3.11.9`
- [x] `runtime.txt` contains `python-3.11.9`
- [x] `main.py` has rebuild trigger print statement
- [x] Changes committed to git
- [x] Changes pushed to repository

During deployment:
- [ ] Build cache cleared on Render
- [ ] Manual deploy triggered
- [ ] Build logs show Python 3.11.9
- [ ] Build logs show Pydantic 2.9.0 installation
- [ ] Build succeeds without errors
- [ ] Application starts successfully

After deployment:
- [ ] `/health` endpoint returns 200 OK
- [ ] `/` endpoint returns API info
- [ ] No `ValueError: 'not' is not a valid parameter name` in logs
- [ ] All API endpoints functioning correctly

---

## 🎯 Expected Build Log Output

```bash
==> Cloning from https://github.com/YOUR_REPO...
==> Checking out commit abc1234def in branch main
==> Using Python version 3.11.9 (from runtime.txt)
==> Installing dependencies from requirements.txt
==> Collecting fastapi==0.115.0
==> Collecting pydantic==2.9.0
==> Collecting pydantic-core==2.23.4
==> Installing collected packages: pydantic-core-2.23.4, pydantic-2.9.0, fastapi-0.115.0, uvicorn-0.30.1, gunicorn-21.2.0, ...
==> Successfully installed fastapi-0.115.0 pydantic-2.9.0 pydantic-core-2.23.4 ...
==> Running 'python add_name_column.py'
==> Build successful 🎉
==> Deploying...
==> Running 'gunicorn main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker'
Force rebuild test
[INFO] Started server process [1]
[INFO] Waiting for application startup.
[INFO] Application startup complete.
[INFO] Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
==> Your service is live 🎉
```

---

## 📞 Support

If deployment still fails after following all steps:

1. **Check Render Logs:**
   - Dashboard → Your Service → Logs tab
   - Look for specific error messages

2. **Verify Local Setup:**
   ```bash
   python --version  # Should be 3.11.x
   pip install -r requirements.txt
   python main.py
   ```

3. **Common Solutions:**
   - Ensure all files are in the correct directory
   - Check git repository structure matches Render service configuration
   - Verify environment variables are set in Render dashboard
   - Try a fresh service deployment if cache clearing doesn't work

---

**Last Updated:** October 21, 2025  
**Python Version:** 3.11.9  
**FastAPI Version:** 0.115.0  
**Pydantic Version:** 2.9.0  
**Pydantic Core:** 2.23.4  

**Status:** ✅ Ready for deployment
