"""CSV logging utilities."""
import os
import csv
from datetime import datetime
from src.logger import logger
from src.config import POST_LOG_FILE


def log_post_to_csv(post_type: str, content: str, media_id: str = None):
    """Log post details to CSV file."""
    try:
        file_exists = os.path.exists(POST_LOG_FILE)
        
        with open(POST_LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'date', 'time', 'post_type', 'content', 'media_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            now = datetime.now()
            writer.writerow({
                'timestamp': now.isoformat(),
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S'),
                'post_type': post_type,
                'content': content,
                'media_id': media_id or 'N/A'
            })
            logger.info(f"Logged post to CSV: {post_type} - {content[:50]}...")
    except Exception as e:
        logger.error(f"Failed to log post to CSV: {e}")
