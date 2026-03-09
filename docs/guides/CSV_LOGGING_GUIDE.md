# CSV Post Logging - Quick Guide

The bot now automatically logs all Instagram posts to a CSV file for easy tracking and analysis!

## 📊 What Gets Logged

Every post (news or festival) is automatically recorded with:
- **Timestamp** - Exact date and time (ISO format)
- **Date** - YYYY-MM-DD format
- **Time** - HH:MM:SS format
- **Post Type** - "News" or "Festival"
- **Content** - News headline or festival name
- **Media ID** - Instagram post ID

## 📁 File Location

`data/post_history.csv`

## 📝 Example Data

```csv
timestamp,date,time,post_type,content,media_id
2026-03-09T12:41:01.811000,2026-03-09,12:41:01,News,Renewed search for missing Flight MH370 comes up empty,3848863092407619848
2026-03-09T12:25:26.177000,2026-03-09,12:25:26,Festival,Diwali,3848855244957123034
2026-03-09T12:16:12.478000,2026-03-09,12:16:12,Festival,Diwali,3848850591771090669
```

## 🔍 Quick Analysis

### View All Posts
```bash
cat data/post_history.csv
```

### View Last 10 Posts
```bash
tail -10 data/post_history.csv
```

### Count Total Posts
```bash
# Subtract 1 for header row
wc -l data/post_history.csv
```

### Filter by Type
```bash
# Only news posts
grep "News" data/post_history.csv

# Only festival posts
grep "Festival" data/post_history.csv
```

### Posts by Date
```bash
cut -d',' -f2 data/post_history.csv | tail -n +2 | sort | uniq -c
```

### Posts Today
```bash
grep "$(date +%Y-%m-%d)" data/post_history.csv
```

## 📊 Excel/Google Sheets

Simply open `data/post_history.csv` in Excel or Google Sheets for:
- Sorting and filtering
- Charts and graphs
- Pivot tables
- Data analysis

## 🔄 Automatic Backup

Create a backup before important operations:
```bash
cp data/post_history.csv data/post_history_backup_$(date +%Y%m%d).csv
```

## 📈 Analytics Ideas

1. **Posting Frequency** - How many posts per day/week/month?
2. **Content Mix** - Ratio of news vs festival posts
3. **Peak Times** - What times do you post most?
4. **Content Tracking** - Which headlines were posted?
5. **Instagram Links** - Use media_id to link back to posts

## 🔗 Instagram Post URL

To view a post on Instagram:
```
https://www.instagram.com/p/[SHORT_CODE]/
```

Note: You'll need to convert the media_id to Instagram's short code format.

## ⚠️ Important Notes

- File is created automatically on first post
- CSV format is compatible with all spreadsheet software
- UTF-8 encoding supports all characters
- Timestamps are in ISO 8601 format
- File grows over time - consider periodic archiving

## 🗄️ Archiving Old Data

Archive posts older than 30 days:
```bash
# Create archive
head -1 data/post_history.csv > data/archive_$(date +%Y%m).csv
grep "2026-02" data/post_history.csv >> data/archive_$(date +%Y%m).csv

# Remove from main file (keep header + recent posts)
head -1 data/post_history.csv > data/post_history_temp.csv
grep -v "2026-02" data/post_history.csv | tail -n +2 >> data/post_history_temp.csv
mv data/post_history_temp.csv data/post_history.csv
```

---

**The CSV file is automatically maintained - no manual intervention needed!** 🎉
