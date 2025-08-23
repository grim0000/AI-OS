# 📧 Gmail Integration Setup Guide

## 🎯 **What You Need**

To use the Gmail feature in your AI-OS system, you need to set up Google Cloud credentials.

## 📋 **Step-by-Step Setup**

### **Step 1: Go to Google Cloud Console**
1. Visit: https://console.cloud.google.com/
2. Sign in with your Google account
3. Create a new project or select existing one

### **Step 2: Enable Gmail API**
1. In the left sidebar, click "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and click "Enable"

### **Step 3: Configure OAuth Consent Screen** ⚠️ **REQUIRED FIRST!**
1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace organization)
3. Fill in the required information:
   - **App name**: "AI-OS Gmail Integration"
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click "Save and Continue"
5. On "Scopes" page, click "Save and Continue"
6. **On "Test users" page, ADD YOUR EMAIL as a test user:**
   - Click "Add Users"
   - Add your email address (e.g., `yourname@gmail.com`)
   - Click "Save"
7. Click "Save and Continue"
8. Click "Back to Dashboard"

**⚠️ IMPORTANT:** You MUST add yourself as a test user, or you'll get "Access blocked" errors!

### **Step 4: Create OAuth 2.0 Credentials**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose **"Desktop application"** as the application type
4. Give it a name (e.g., "AI-OS Gmail Integration")
5. Click "Create"

### **Step 5: Download Credentials**
1. After creating, click the download button (⬇️)
2. Save the file as `gmail_credentials.json`
3. Move this file to your `AI-OS-500pm/Data/` folder

clientid:1000923975333-btmffquo71q4m4p8lqoj587jn9eqig8o.apps.googleusercontent.com
secretclientid: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

### **Step 6: Test the Integration**
1. Run your AI-OS system
2. Say: **"setup gmail"**
3. The system will open a browser window for authentication
4. Sign in with your Google account
5. Grant permissions to send emails

## 🚀 **How to Use Gmail Features**

### **Send a Simple Email**
```
"send email to john@example.com with subject 'Meeting' saying 'Let's meet tomorrow at 2 PM'"
```

### **Draft and Send Content**
1. First draft content: **"draft an email to my boss about project update"**
2. Then send it: **"send it to boss@company.com"**

### **Auto-Send Generated Content**
```
"send the generated content to client@example.com with subject 'Project Proposal'"
```

## 🔒 **Security Notes**

- Your credentials are stored locally in the `Data` folder
- The system only requests permission to **send emails** (not read them)
- You can revoke access anytime in your Google Account settings

## 🧪 **Testing Commands**

Try these commands in your AI-OS system:

1. **Setup**: "setup gmail"
2. **Test Send**: "send email to test@example.com with subject 'Test' saying 'This is a test email'"
3. **Check Status**: "gmail status"

## ❌ **Common Issues & Solutions**

### **"Credentials not found"**
- Make sure `gmail_credentials.json` is in the `Data` folder
- Check the file name spelling

### **"Authentication failed"**
- Try running "setup gmail" again
- Check your internet connection
- Make sure you're signed into the correct Google account

### **"Permission denied"**
- Make sure you granted "Send email" permission
- Check if Gmail API is enabled in your Google Cloud project

### **"To create an OAuth client ID, you must first configure your consent screen"**
- **This is the issue you're seeing!**
- You MUST complete Step 3 (Configure OAuth Consent Screen) before creating credentials
- The consent screen is required for any OAuth 2.0 application

## 📁 **File Structure**

After setup, you should have these files in your `Data` folder:
```
Data/
├── gmail_credentials.json  ← Your Google Cloud credentials
├── gmail_token.json        ← Generated after authentication
└── ... (other files)
```

## 🎉 **You're Ready!**

Once setup is complete, you can:
- ✅ Send emails directly through voice commands
- ✅ Auto-send generated content
- ✅ Draft emails and send them later
- ✅ Use natural language to compose emails

**Example**: "Send an email to my team about the meeting tomorrow at 3 PM"

---

**Need Help?** Say "help gmail" in your AI-OS system for assistance!
