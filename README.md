# AIRMAN Social Media Automation

**An intelligent, fully-automated Instagram news-publication agent built for the AIRMAN brand.**

This Python project runs a Telegram bot that allows you to easily pull in the latest global aviation news, automatically synthesize a stunning ultra-realistic photograph using Google's unreleased **Imagen 4.0** model, generate a brand-aligned, educational caption using **Gemini 2.5 Flash**, apply premium marketing typography dynamically to the image (with Apple's Avenir/Futura fonts and the AIRMAN logo), and post the finalized creative directly to the [@we_are_airman](https://www.instagram.com/we_are_airman/) Instagram account—all from within a simple chat interface. 

---

## 🚀 Key Features

*   **1-Click News Scraping**: Command the bot via Telegram to scrape the top 5 trending aviation headlines off Google News instantly.
*   **Imagen 4.0 Image Synthesis**: Creates hyper-realistic 8k images matching the news story directly via Google's most advanced image generation models.
*   **Gemini AI Social Coordinator**: Contextually writes beautiful, highly-professional Instagram captions matching the 'Aviation Intelligence' AIRMAN brand guidelines exactly, populated with relevant hashtags.
*   **Dynamic Visual Rendering Studio**: Uses PIL to crop the generated artwork perfectly to a 1:1 format, burn a brand-aligned readability gradient overlay, append transparent custom logos, and print the headline across the image using sleek, minimalist UI typography. 
*   **Instagram API**: Securely pushes the final image and caption immediately to Instagram. 

## 📖 Quick Navigation

Please see [**QUICKSTART.md**](./QUICKSTART.md) for detailed instructions on:
1. Setting up prerequisites and your environment.
2. Filling out your `.env` keys (Telegram, Instagram, Gemini AI).
3. Using the bot!

## 🛠️ Stack

*   **Google GenAI** (`gemini-2.5-flash` & `imagen-4.0-generate-001`)
*   **Python Telegram Bot**
*   **Instagrapi** 
*   **Pillow** (Image Processing)
