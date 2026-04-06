import os

from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()
username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

cl = Client()
try:
    print(f"Logging in as {username}...")
    cl.login(username, password)
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
