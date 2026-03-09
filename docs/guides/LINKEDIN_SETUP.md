# LinkedIn Integration Setup Guide

## ⚠️ IMPORTANT SECURITY NOTICE

**NEVER share your API credentials publicly or commit them to git!**

The credentials you shared should be:
1. ✅ Stored in `.env` file (which is gitignored)
2. ❌ NEVER committed to git
3. ❌ NEVER shared in chat/messages
4. ❌ NEVER posted publicly

---

## 🔐 Step 1: Add Credentials to .env File

Open your `.env` file and add these lines:

```env
# Existing credentials
TELEGRAM_BOT_TOKEN=your_existing_token
INSTAGRAM_USERNAME=your_existing_username
INSTAGRAM_PASSWORD=your_existing_password
GEMINI_API=your_existing_api_key

# LinkedIn API Credentials
LINKEDIN_CLIENT_ID=862bzxgrofi7oq
LINKEDIN_CLIENT_SECRET=WPL_AP1.yNfu7MmVzHqPBNOH.IFgRIA==
LINKEDIN_ACCESS_TOKEN=AQU6n3dlf1gzY8R-spVG2Kyc0diTzNqJ0jENMz49At2f07Jgf13VZVj1W04460taF-IQdb2Jkgy8Ui0qh29Nd-4wkfi_cVyOWZRkYP0ickPZda41qVawn85gCHvK1GSLiETUDZPat1ciXx3Lrk-Mm-1p7YQeYdEveEQ_ZqDU7a910F8xsh_sTQRHPxHrB7MasVk8gp234HDqLo66xhODuNoAy55zdQQxUElUWOP_TdOW5ThrBtO26omCBMbmlvzH29o2JN7ptrbcQTFLAClMNw-FJTCn86_B-5zNJGrpnb38TFOJa-Xe5_dLeDyQzA7aI64TL7bRs9C5_mA5albVX62EWIb4GA
```

**Command to edit .env:**
```bash
nano .env
# or
vim .env
# or
code .env
```

---

## 🔄 Step 2: Revoke and Regenerate (RECOMMENDED)

Since you shared these credentials publicly, it's best to revoke them and generate new ones:

1. Go to https://www.linkedin.com/developers/apps
2. Select your app
3. Go to "Auth" tab
4. Click "Regenerate" for Client Secret
5. Go to "Access tokens" and revoke the current token
6. Generate a new access token
7. Update your `.env` file with the new credentials

---

## 📋 Step 3: Verify .env File

Make sure your `.env` file:
- ✅ Is in the project root directory
- ✅ Is listed in `.gitignore`
- ✅ Has all required credentials
- ✅ Has no extra spaces or quotes around values

**Check .gitignore:**
```bash
grep ".env" .gitignore
```

Should show:
```
.env
```

---

## 🧪 Step 4: Test Credentials

After adding to `.env`, test that they load correctly:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('LinkedIn Client ID:', os.getenv('LINKEDIN_CLIENT_ID'))"
```

Should output:
```
LinkedIn Client ID: 862bzxgrofi7oq
```

---

## 🔒 Security Best Practices

### DO:
✅ Store credentials in `.env` file
✅ Add `.env` to `.gitignore`
✅ Use environment variables in code
✅ Rotate credentials regularly
✅ Use different credentials for dev/prod
✅ Revoke unused tokens

### DON'T:
❌ Commit `.env` to git
❌ Share credentials in chat/email
❌ Hardcode credentials in code
❌ Post credentials publicly
❌ Use production credentials in development
❌ Share credentials across multiple apps

---

## 📝 Access Token Expiration

LinkedIn access tokens typically expire after 60 days. You'll need to:

1. **Monitor expiration** - Check token validity regularly
2. **Refresh tokens** - Implement OAuth refresh flow (advanced)
3. **Manual renewal** - Generate new token when expired

**Signs of expired token:**
- API returns 401 Unauthorized
- Posts fail with authentication error
- Bot logs show "Invalid access token"

---

## 🔗 LinkedIn API Documentation

- **Developer Portal**: https://www.linkedin.com/developers/
- **API Docs**: https://learn.microsoft.com/en-us/linkedin/
- **OAuth Guide**: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication

---

## ✅ Checklist

Before proceeding:
- [ ] Added credentials to `.env` file
- [ ] Verified `.env` is in `.gitignore`
- [ ] Tested credentials load correctly
- [ ] (Recommended) Revoked and regenerated credentials
- [ ] Understood token expiration (60 days)
- [ ] Ready to integrate LinkedIn posting

---

**Once you've completed these steps, I can proceed with implementing LinkedIn posting functionality!** 🚀
