# Railway Volumes Guide - When to Use Them

## ⚠️ Important: Your Current Database Issue is NOT About Volumes

**The database connection error you're experiencing is because migrations haven't run.** Railway's managed PostgreSQL already handles data persistence automatically - **you don't need a volume for the database.**

---

## ✅ When You DON'T Need Volumes

### 1. PostgreSQL Database (Managed Service)
- **Railway's managed PostgreSQL handles data persistence automatically**
- Data is stored in Railway's infrastructure
- You **cannot** and **should not** mount `/var/lib/postgresql/data`
- The database connection issue is about **migrations not running**, not volumes

### 2. Static Files (CSS, JavaScript)
- Currently: `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- **No volume needed** - Static files are:
  - Collected during build (`python manage.py collectstatic`)
  - Served by WhiteNoise middleware
  - Included in the container image
  - Don't need persistence (they're regenerated on each deploy)

---

## ✅ When You DO Need Volumes

### Media Files (User Uploads) - **YOU SHOULD USE A VOLUME**

**Current Setup:**
```python
MEDIA_ROOT = BASE_DIR / 'media'  # This is ephemeral!
```

**Problem:** 
- Media files (uploaded images, documents, etc.) are stored in `/app/media`
- Railway containers are **ephemeral** - files are lost on restart/redeploy
- If users upload files, they'll disappear when the container restarts

**Solution: Use Railway Volume**

#### Step 1: Create Volume in Railway
1. Go to Railway Dashboard → Your Project
2. Right-click on project canvas OR use Command Palette (⌘K)
3. Select **"Add Volume"**
4. Name it: `media-files` (or similar)
5. Select your **Django service** (not PostgreSQL)
6. Set mount path: `/app/media`
7. Choose size (based on your plan)

#### Step 2: Update Django Settings (Optional)
Your current settings already use `BASE_DIR / 'media'`, which will work with the volume mount. But you can make it explicit:

```python
# In webcrm/settings.py
import os

# Media files - use volume mount path
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')
MEDIA_URL = '/media/'
```

Or keep it as-is - Railway will mount the volume to `/app/media` and Django will use it automatically.

#### Step 3: Verify Volume is Working
After mounting the volume, files uploaded to `/app/media` will persist across restarts.

---

## 📋 Volume Setup Checklist

### For Media Files (Recommended):

- [ ] Create Railway volume named `media-files`
- [ ] Mount to Django service at `/app/media`
- [ ] Verify `MEDIA_ROOT` in settings points to `/app/media` (it already does)
- [ ] Test by uploading a file and restarting the service

### For Database (NOT NEEDED):

- [ ] ❌ **Don't create a volume for PostgreSQL** - Railway manages it
- [ ] ✅ Focus on running migrations instead

---

## 🔍 Current Issue: Database Connection Error

**This is NOT a volume issue.** The problem is:

1. **Migrations haven't run** → Tables don't exist → Connection errors
2. **Solution:** Run migrations (see `DATABASE_CONNECTION_TROUBLESHOOTING.md`)

**You don't need a volume to fix the database connection error.**

---

## 📊 Volume Use Cases Summary

| Data Type | Need Volume? | Why |
|-----------|--------------|-----|
| **PostgreSQL Database** | ❌ NO | Railway manages persistence automatically |
| **Static Files** | ❌ NO | Collected during build, served by WhiteNoise |
| **Media Files** (uploads) | ✅ YES | User uploads need persistence across restarts |
| **Log Files** | ⚠️ Maybe | If you want persistent logs (usually not needed) |
| **Cache Files** | ❌ NO | Can be regenerated, or use Redis |

---

## 🛠️ How to Create Volume for Media Files

### Via Railway Dashboard:

1. **Open Railway Dashboard** → Your Project
2. **Right-click** on project canvas OR press **⌘K** (Command Palette)
3. Select **"Add Volume"** or **"New Volume"**
4. **Configure:**
   - **Name:** `media-files`
   - **Service:** Select your Django service
   - **Mount Path:** `/app/media`
   - **Size:** Choose based on your plan (Free tier has limits)
5. **Create**

### Verify It Works:

After creating the volume:
1. Upload a file via your Django app
2. Check if it's in `/app/media` (via Railway shell or logs)
3. Restart your Django service
4. File should still be there ✅

---

## 💡 Alternative: Use S3 for Media Files

For production, consider using AWS S3 instead of volumes:

**Advantages:**
- ✅ No size limits (volumes have plan limits)
- ✅ Better performance for large files
- ✅ CDN integration possible
- ✅ Backups handled by AWS

**Setup:** See `RAILWAY_DEPLOYMENT.md` for S3 configuration

---

## ⚠️ Important Notes

1. **Volume Size Limits:**
   - Free tier: Limited storage
   - Check your Railway plan limits
   - Consider S3 for large files

2. **Volume I/O:**
   - Volumes have read/write IOPS limits
   - For high-traffic apps, S3 might be better

3. **Backup:**
   - Railway volumes are backed up, but consider your own backups
   - S3 has better backup/redundancy options

4. **Database:**
   - **Never** create a volume for PostgreSQL data directory
   - Railway manages database persistence automatically
   - Your database connection issue is about migrations, not volumes

---

## 🎯 Action Items

**For your current database connection error:**
1. ❌ **Don't create a volume for PostgreSQL**
2. ✅ **Run migrations** (see troubleshooting guides)
3. ✅ **Check if tables exist** (use `check_database_state.py`)

**For media files persistence (later):**
1. ✅ **Create volume** for `/app/media` when you need user uploads
2. ✅ **Or configure S3** for production

---

## Summary

- **Database:** Railway manages it - NO volume needed
- **Static files:** Collected during build - NO volume needed  
- **Media files:** User uploads - YES, use volume (or S3)
- **Your current issue:** Migrations not running - NOT a volume problem

