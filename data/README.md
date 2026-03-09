# Data Directory

This directory stores application data files and post history.

## Files

### post_history.csv
Tracks all Instagram posts made by the bot.

**Columns:**
- `timestamp` - ISO format timestamp (e.g., 2026-03-09T12:41:01.811000)
- `date` - Date of post (YYYY-MM-DD)
- `time` - Time of post (HH:MM:SS)
- `post_type` - Type of post: "News" or "Festival"
- `content` - News headline or festival name
- `media_id` - Instagram media ID

**Example:**
```csv
timestamp,date,time,post_type,content,media_id
2026-03-09T12:41:01.811000,2026-03-09,12:41:01,News,Renewed search for missing Flight MH370 comes up empty,3848863092407619848
2026-03-09T12:25:26.177000,2026-03-09,12:25:26,Festival,Diwali,3848855244957123034
```

### shown_news.txt
Tracks previously shown headlines to prevent duplicates.

### posted_festivals_[YEAR].txt
Tracks posted festivals per year to ensure each festival posts only once annually.

---

## Usage

### View Post History
```bash
# View all posts
cat data/post_history.csv

# View recent posts
tail -20 data/post_history.csv

# Count total posts
wc -l data/post_history.csv

# View only news posts
grep "News" data/post_history.csv

# View only festival posts
grep "Festival" data/post_history.csv
```

### Analyze Posts
```bash
# Posts by date
cut -d',' -f2 data/post_history.csv | sort | uniq -c

# Posts by type
cut -d',' -f4 data/post_history.csv | sort | uniq -c
```

### Import to Excel/Google Sheets
Simply open `post_history.csv` in Excel or Google Sheets for analysis and visualization.

---

## Backup

It's recommended to backup this file regularly:
```bash
cp data/post_history.csv data/post_history_backup_$(date +%Y%m%d).csv
```
