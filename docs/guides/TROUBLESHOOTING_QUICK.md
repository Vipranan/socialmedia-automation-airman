# Quick Troubleshooting Guide

## Issue: `/forcefestival` command not working

### ✅ Solution Checklist

#### 1. Is the bot running?
```bash
# Check if bot is running
ps aux | grep "python.*main.py" | grep -v grep

# If not running, start it:
python main.py
```

#### 2. Check the logs
```bash
# View recent logs
tail -50 logs/bot.log

# Watch logs in real-time
tail -f logs/bot.log
```

#### 3. Test the command
In Telegram, send:
```
/forcefestival Diwali
```

You should see:
1. "🚀 Generating special festival post for 'Diwali'..."
2. Progress updates
3. "✅ Festival post published to Instagram!"
4. The caption used

#### 4. Common Issues

**Bot not responding at all**
- ❌ Bot is not running
- ✅ Start with: `python main.py`

**Error: "GEMINI_API key not found"**
- ❌ Missing API key in .env
- ✅ Check `.env` file has `GEMINI_API=your_key`

**Error: "Failed to login to Instagram"**
- ❌ Instagram credentials invalid
- ✅ Check `.env` has correct `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`

**Error: "Image generation failed"**
- ❌ Imagen API issue
- ✅ Test with: `python tests/api_test.py`
- ✅ Check API quota at https://aistudio.google.com/

**Command seems stuck**
- ⏳ Image generation takes 15-30 seconds
- ⏳ Be patient, check logs for progress

---

## Quick Test Commands

### Test Gemini API
```bash
python tests/api_test.py
```

### Test Instagram Login
```bash
python tests/test_ig.py
```

### Test Telegram Bot
```bash
python tests/test_tg.py
```

---

## Running the Bot

### Start Bot
```bash
python main.py
```

### Stop Bot
Press `Ctrl+C` in the terminal

### Run in Background (macOS/Linux)
```bash
nohup python main.py > logs/bot_output.log 2>&1 &
```

### Check if Running
```bash
ps aux | grep "python.*main.py" | grep -v grep
```

### Kill Background Bot
```bash
pkill -f "python.*main.py"
```

---

## Improved Error Handling

The code has been updated with better error handling:

✅ More detailed logging  
✅ Better error messages  
✅ Step-by-step progress logs  
✅ Exception details in logs  

Now when you run `/forcefestival Diwali`, you'll see detailed logs in `logs/bot.log`:
- "Force festival command received for: Diwali"
- "Starting festival post generation for: Diwali"
- "Generating caption with Gemini..."
- "Caption generated successfully. Title: [title]"
- "Generating image with Imagen 4.0..."
- "Image generated: [path]"
- "Formatting image for Instagram..."
- "Attempting to post festival Diwali to Instagram."
- "Successfully posted to Instagram. Media ID: [id]"

---

## Next Steps

1. **Start the bot**: `python main.py`
2. **Open Telegram** and find your bot
3. **Send command**: `/forcefestival Diwali`
4. **Watch logs**: `tail -f logs/bot.log` (in another terminal)
5. **Wait 15-30 seconds** for generation
6. **Check Instagram** for the post

---

## Still Having Issues?

Check the full documentation:
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Setup guide
- [docs/CODEBASE_DOCUMENTATION.md](docs/CODEBASE_DOCUMENTATION.md) - Section 13: Troubleshooting

Or check logs for specific error messages:
```bash
grep -i "error\|exception\|failed" logs/bot.log | tail -20
```
