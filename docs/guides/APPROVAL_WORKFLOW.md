# Post Approval Workflow

The bot now requires user approval before posting! You can preview content and choose which platforms to post to.

---

## 📋 New Workflow

### Step 1: Fetch News
```
User: /news
Bot: 🔎 Fetching top 5 Aviation News...
Bot: [Shows 5 headline options]
```

### Step 2: Select Headline
```
User: [Clicks Option 1]
Bot: ✅ You selected: [headline]
Bot: ✍️ Generating caption and image... Hang tight!
```

### Step 3: Preview & Approve
```
Bot: [Shows generated image with caption preview]
Bot: 📝 Preview: [caption]
Bot: 👇 Choose where to post:

Buttons:
✅ Post to Both (Instagram + LinkedIn)
📷 Instagram Only
💼 LinkedIn Only
❌ Cancel
```

### Step 4: Post
```
User: [Clicks desired option]
Bot: 📤 Publishing...
Bot: ✅ Successfully posted to [platforms]!
Bot: 📝 Caption used: [full caption]
```

---

## 🎯 Approval Options

| Button | Action | Platforms |
|--------|--------|-----------|
| **✅ Post to Both** | Post to Instagram AND LinkedIn | Both |
| **📷 Instagram Only** | Post only to Instagram | Instagram |
| **💼 LinkedIn Only** | Post only to LinkedIn | LinkedIn |
| **❌ Cancel** | Don't post, discard content | None |

---

## ✨ Benefits

✅ **Preview Before Posting** - See exactly what will be posted  
✅ **Platform Control** - Choose which platforms to use  
✅ **Quality Check** - Review AI-generated content  
✅ **Flexibility** - Cancel if content isn't right  
✅ **No Mistakes** - Prevent accidental posts  

---

## 📝 What You See in Preview

- **Image**: The AI-generated poster
- **Caption**: First 1000 characters of the caption
- **Buttons**: 4 options to choose from

---

## 🔄 Example Flow

### News Post:
```
1. /news
2. Select "Boeing unveils new aircraft"
3. Preview shows image + caption
4. Click "✅ Post to Both"
5. Posted to Instagram + LinkedIn!
```

### Festival Post:
```
1. /forcefestival Diwali
2. Preview shows image + caption
3. Click "📷 Instagram Only"
4. Posted to Instagram only!
```

---

## ⚠️ Important Notes

### Session Timeout
- Preview is valid for current session only
- If bot restarts, you'll need to start over
- Don't wait too long to approve

### Image Cleanup
- Images are automatically deleted after posting
- Cancelled posts also clean up images
- No manual cleanup needed

### Caption Length
- Preview shows first 1000 characters
- Full caption is posted
- Full caption shown after posting

---

## 🚀 Commands Affected

All posting commands now have approval:

| Command | Approval Required |
|---------|-------------------|
| `/news` | ✅ Yes |
| `/forcefestival [Name]` | ✅ Yes (coming soon) |
| `/startauto` | ❌ No (auto-posts without approval) |

**Note**: Auto-pilot mode (`/startauto`) posts automatically without approval for convenience.

---

## 🎨 Customization

Want to change the approval buttons? Edit `process_news_selection()` in `main.py`:

```python
keyboard = [
    [
        InlineKeyboardButton("✅ Post to Both", callback_data="approve_both"),
        InlineKeyboardButton("📷 Instagram Only", callback_data="approve_instagram")
    ],
    [
        InlineKeyboardButton("💼 LinkedIn Only", callback_data="approve_linkedin"),
        InlineKeyboardButton("❌ Cancel", callback_data="approve_cancel")
    ]
]
```

---

## 📊 CSV Logging

Posts are logged with the platforms used:

```csv
timestamp,date,time,post_type,content,media_id
2026-03-09T14:30:00,2026-03-09,14:30:00,News,Boeing news,IG:123456|LI:N/A
2026-03-09T14:35:00,2026-03-09,14:35:00,News,SpaceX news,IG:N/A|LI:urn:li:share:789
2026-03-09T14:40:00,2026-03-09,14:40:00,News,NASA news,IG:123789|LI:urn:li:share:456
```

- `IG:N/A` = Not posted to Instagram
- `LI:N/A` = Not posted to LinkedIn

---

**Enjoy the new approval workflow!** 🎉
