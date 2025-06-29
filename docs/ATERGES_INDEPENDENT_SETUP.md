# Aterges Independent Setup Guide

## 🎯 **Making Aterges Completely Independent**

This guide will help you create a dedicated Google Cloud setup for Aterges, completely separate from any existing projects.

---

## **Step 1: Create Dedicated Gmail Account for Aterges**

1. **Create new Gmail account** (recommended pattern):
   - `aterges.platform@gmail.com`
   - `your-name.aterges@gmail.com`
   - `aterges@your-domain.com` (if you have a custom domain)

2. **Use this account for all Aterges services**:
   - Google Cloud Console
   - Google Analytics
   - Any other Google services

---

## **Step 2: Create New Google Cloud Project**

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Sign in** with your new Aterges Gmail account
3. **Create new project**:
   - Project name: `Aterges Platform`
   - Project ID: `aterges-platform-prod` (or similar unique ID)
   - Location: Leave as default

4. **Enable required APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable analyticsdata.googleapis.com
   gcloud services enable run.googleapis.com
   ```

---

## **Step 3: Create Service Account**

1. **Go to IAM & Admin > Service Accounts**
2. **Create service account**:
   - Name: `aterges-ai-service`
   - Description: `Service account for Aterges AI platform`

3. **Grant roles**:
   - `AI Platform User` (for Vertex AI)
   - `Analytics Data Viewer` (for GA4 API)
   - `Cloud Run Invoker` (for deployment)

4. **Create and download key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - **Download the file** and rename it to `aterges-service-account.json`

---

## **Step 4: Set Up Google Analytics 4 Property**

1. **Go to Google Analytics**: https://analytics.google.com
2. **Sign in** with your Aterges Gmail account
3. **Create new account**:
   - Account name: `Aterges Platform`
   - Country/Region: Your location

4. **Create new property**:
   - Property name: `Aterges Demo Website` (or your actual website)
   - Time zone: Your timezone
   - Currency: Your currency

5. **Set up data stream** (for testing):
   - Choose "Web"
   - Website URL: `https://aterges.vercel.app`
   - Stream name: `Aterges Production`

6. **Copy the Property ID**:
   - Format: `properties/123456789`
   - You'll need this for configuration

---

## **Step 5: Configure Aterges Backend**

1. **Place service account file**:
   ```bash
   # Copy your downloaded service account file to:
   C:\Users\jrodeiro\Desktop\aterges\backend\aterges-service-account.json
   ```

2. **Update environment variables** in `backend/.env`:
   ```bash
   # Replace with your actual values
   GOOGLE_CLOUD_PROJECT=aterges-platform-prod
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=./aterges-service-account.json
   GA4_PROPERTY_ID=properties/123456789
   ```

3. **Verify configuration**:
   ```bash
   cd backend
   python test_phase1.py
   ```

---

## **Step 6: Test the Setup**

1. **Start the backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Test health endpoints**:
   ```bash
   # Basic health
   curl http://localhost:8000/health

   # AI status (requires authentication)
   curl -H "Authorization: Bearer <your-jwt>" http://localhost:8000/api/ai/status
   ```

3. **Test AI conversation**:
   - Go to https://aterges.vercel.app
   - Sign up/login
   - Ask: "What were my sessions last week?"

---

## **Step 7: Deploy to Production**

1. **Build and deploy**:
   ```bash
   cd backend
   gcloud run deploy aterges-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --set-env-vars GOOGLE_CLOUD_PROJECT=aterges-platform-prod \
     --set-env-vars GA4_PROPERTY_ID=properties/123456789 \
     --allow-unauthenticated
   ```

2. **Update frontend** to use production backend URL

---

## **🔐 Security Checklist**

- ✅ **Service account has minimal required permissions**
- ✅ **Service account file is gitignored**
- ✅ **Environment variables are properly configured**
- ✅ **No hardcoded credentials in code**
- ✅ **Separate Google account for Aterges**
- ✅ **Dedicated Google Cloud project**

---

## **💰 Cost Management**

**Expected monthly costs:**
- **Vertex AI (Gemini)**: $10-30 (100-1000 queries)
- **Google Analytics API**: Free (up to 200k requests/day)
- **Cloud Run**: $5-20 (depending on usage)
- **Total**: $15-50/month for moderate usage

**Cost optimization:**
- Monitor usage in Google Cloud Console
- Set up billing alerts
- Use caching to reduce API calls

---

## **🚀 Going Live**

Once everything is working:

1. **Point your actual website** GA4 property to Aterges
2. **Update GA4_PROPERTY_ID** with your real property
3. **Test with real data**
4. **Monitor performance and costs**

---

## **🔧 Troubleshooting**

**Common issues:**

1. **"Service account not found"**
   - Ensure file path in `.env` is correct
   - Check file exists and has proper permissions

2. **"GA4 property not found"**
   - Verify property ID format: `properties/123456789`
   - Ensure service account has Analytics Data Viewer role

3. **"Vertex AI permission denied"**
   - Check service account has AI Platform User role
   - Verify APIs are enabled

4. **"No data returned"**
   - Check if GA4 property has data
   - Try with a broader date range

---

## **✅ Independence Verification**

Your Aterges setup is completely independent when:

- ✅ Uses dedicated Gmail account
- ✅ Has separate Google Cloud project
- ✅ Uses its own service account
- ✅ Has dedicated GA4 property
- ✅ No dependencies on other directories/projects
- ✅ All credentials are Aterges-specific

---

**Your Aterges platform is now completely independent! 🎉**
