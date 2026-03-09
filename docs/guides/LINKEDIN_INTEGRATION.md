# LinkedIn Integration - Complete Guide

The bot now automatically posts to **both Instagram AND LinkedIn**! 🎉

---

## ✨ Features

✅ **Dual Platform Posting** - Every post goes to Instagram AND LinkedIn  
✅ **Automatic Image Upload** - Images are uploaded to LinkedIn  
✅ **Platform-Optimized Captions** - Different formatting for each platform  
✅ **Error Handling** - If LinkedIn fails, Instagram post still succeeds  
✅ **CSV Logging** - Tracks both Instagram and LinkedIn post IDs  

---

## 🚀 How It Works

### When You Post:

1. **Generate Content** - AI creates caption and image
2. **Post to Instagram** - Image + caption posted
3. **Post to LinkedIn** - Same image + optimized caption posted
4. **Log to CSV** - Both post IDs recorded

### Platforms:
- **Instagram**: Full caption with emojis
- **LinkedIn**: Professional caption with hashtags

---

## 📝 Caption Differences

### Instagram Caption:
```
[AI-generated content with emojis ✈️ 🚀 ☁️]

#AviationNews #AIRMAN #FutureOfFlight

🌐 https://www.theairman.org/
```

### LinkedIn Caption:
```
[AI-generated content - professional tone]

#AIRMAN #Aviation #AviationNews #FutureOfFlight

Learn more: https://www.theairman.org/
```

---

## 🎯 Commands That Post to Both Platforms

All these commands now post to Instagram AND LinkedIn:

| Command | What It Does |
|---------|--------------|
| `/news` | Select and post aviation news |
| `/forcefestival [Name]` | Post festival content |
| `/startauto` | Auto-post news + festivals hourly |

---

## 📊 CSV Logging Format

Posts are logged with both platform IDs:

```csv
timestamp,date,time,post_type,content,media_id
2026-03-09T12:41:01,2026-03-09,12:41:01,News,Flight MH370 search,IG:3848863092|LI:urn:li:share:7123456789
```

**Format**: `IG:[instagram_id]|LI:[linkedin_id]`

---

## 🔧 Configuration

### Required in `.env`:
```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
```

### Optional - Disable LinkedIn:
If you want to post only to Instagram, remove or comment out the LinkedIn credentials in `.env`:

```env
# LINKEDIN_ACCESS_TOKEN=...
```

The bot will automatically skip LinkedIn posting if credentials are missing.

---

## ⚠️ LinkedIn API Limits

### Rate Limits:
- **Posts per day**: 100 (LinkedIn limit)
- **Image uploads**: 100 per day
- **API calls**: 500 per day

### Access Token:
- **Expires**: After 60 days
- **Renewal**: Generate new token at https://www.linkedin.com/developers/apps
- **Signs of expiration**: 401 Unauthorized errors

---

## 🐛 Troubleshooting

### LinkedIn Post Fails

**Error**: `401 Unauthorized`
- **Cause**: Access token expired
- **Fix**: Generate new token and update `.env`

**Error**: `403 Forbidden`
- **Cause**: App doesn't have posting permissions
- **Fix**: Check app permissions at LinkedIn Developer Portal

**Error**: `429 Too Many Requests`
- **Cause**: Hit rate limit
- **Fix**: Wait and reduce posting frequency

### Image Upload Fails

**Error**: `Image upload failed`
- **Cause**: Image too large or wrong format
- **Fix**: Images are auto-formatted to 1080x1080 JPEG

### Both Platforms Fail

**Check**:
1. Internet connection
2. API credentials in `.env`
3. Instagram login status
4. LinkedIn token validity

---

## 📈 Success Indicators

### In Telegram:
```
✅ Post successfully published to Instagram!
✅ Successfully posted to LinkedIn
```

### In Logs:
```
INFO - Successfully posted to Instagram. Media ID: 3848863092
INFO - Successfully posted to LinkedIn. Post ID: urn:li:share:7123456789
INFO - Logged post to CSV: News - Flight MH370...
```

### In CSV:
```csv
...,News,Flight MH370,IG:3848863092|LI:urn:li:share:7123456789
```

---

## 🔄 Workflow Example

### Manual Post:
```
User: /news
Bot: 🔎 Fetching top 5 Aviation News...
Bot: [Shows 5 options]
User: [Clicks Option 1]
Bot: ✍️ Generating caption and image...
Bot: ✅ Posted to Instagram!
Bot: ✅ Posted to LinkedIn!
Bot: 📝 Caption used: [shows caption]
```

### Auto-Pilot:
```
[Every hour]
Bot: ⚙️ Auto-pilot: Posting new aviation news...
Bot: ✅ Posted to Instagram!
Bot: ✅ Posted to LinkedIn!
```

---

## 🎨 Customization

### Change LinkedIn Caption Format

Edit `generate_and_post()` in `main.py`:

```python
# Current format
linkedin_caption = caption.replace("🌐 https://www.theairman.org/", "").strip()
linkedin_caption += "\n\n#AIRMAN #Aviation #AviationNews #FutureOfFlight"
linkedin_caption += "\n\nLearn more: https://www.theairman.org/"

# Custom format
linkedin_caption = f"🚀 {caption}\n\n#YourHashtags\n\nVisit: your-url.com"
```

### Post to LinkedIn Only

Create a new command that skips Instagram (advanced - requires code modification).

---

## 📚 LinkedIn API Resources

- **Developer Portal**: https://www.linkedin.com/developers/
- **API Documentation**: https://learn.microsoft.com/en-us/linkedin/
- **Share API**: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- **Image Upload**: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/images-api

---

## ✅ Testing

### Test LinkedIn Connection:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Token:', os.getenv('LINKEDIN_ACCESS_TOKEN')[:20] + '...')"
```

### Test Post:
1. Start bot: `python main.py`
2. Send: `/forcefestival Test`
3. Check both Instagram and LinkedIn for the post

---

## 🎉 You're All Set!

The bot now automatically posts to both Instagram and LinkedIn with every command. No additional steps needed - just use the bot as normal!

**Happy posting!** 🚀✈️
