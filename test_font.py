import sys
import PIL.ImageFont
try:
    font = PIL.ImageFont.truetype("Futura.ttc", 20)
    print("Futura loaded")
except Exception as e:
    print(e)
