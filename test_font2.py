import sys
import PIL.ImageFont
try:
    font = PIL.ImageFont.truetype("Avenir.ttc", 20)
    print("Avenir loaded")
except Exception as e:
    print("Avenir failed:", e)
    
try:
    font2 = PIL.ImageFont.truetype("SFPro-Regular.ttf", 20)
    print("SFPro loaded")
except Exception as e:
    print("SFPro failed:", e)
