import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API")

if not api_key:
    print("❌ Error: GEMINI_API is not set in .env")
    exit(1)

print("✅ Found GEMINI_API key in .env")
client = genai.Client(api_key=api_key)

print("\n--- Testing Text Generation (Gemini 2.5 Flash) ---")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Write a very short, 1-sentence aviation fact.',
    )
    print("Success! Response from Gemini:")
    print(response.text)
except Exception as e:
    print("❌ Text Generation Failed:", e)


print("\n--- Testing Image Generation (Imagen 4.0) ---")
try:
    result = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A beautiful modern private jet flying in a cinematic sunset',
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1"
        )
    )
    if result.generated_images:
        for i, generated_image in enumerate(result.generated_images):
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(generated_image.image.image_bytes))
            image.save(f"gemini_test_output.jpg")
            print("Success! Image saved as gemini_test_output.jpg")
    else:
        print("Image generation returned no result.")
except Exception as e:
    print("❌ Image Generation Failed:", e)
