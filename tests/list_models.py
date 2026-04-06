import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API")
client = genai.Client(api_key=api_key)

print("\n--- Listing Models ---")
models = client.models.list()
for m in models:
    if "imagen" in m.name.lower():
        print(f"Found Imagen Model: {m.name}")
