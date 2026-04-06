"""
Curated Google Fonts available for poster text.

Each entry maps a user-facing label to:
  - 'google_font': the exact Google Fonts family name (for display / reference)
  - 'description': visual traits used in the Imagen prompt — describes appearance
    without naming the font (avoids the model rendering the font name as text)
  - 'preview': short example shown in Telegram so the user can imagine the style
"""

FONT_STYLES: dict[str, dict] = {
    "anton": {
        "label": "Anton  —  Ultra Bold Condensed",
        "google_font": "Anton",
        "description": "ultra-bold condensed display sans-serif, extremely heavy strokes, very tight letter-spacing, all-caps only, monumental impact — do NOT write the font name",
        "preview": "IMPACT HEADLINES",
    },
    "oswald": {
        "label": "Oswald  —  Bold Condensed",
        "google_font": "Oswald",
        "description": "bold condensed humanist sans-serif, medium-heavy strokes, slightly open letter-spacing, modern editorial feel — do NOT write the font name",
        "preview": "Modern Editorial",
    },
    "bebas_neue": {
        "label": "Bebas Neue  —  Cinematic Caps",
        "google_font": "Bebas Neue",
        "description": "tall narrow all-caps display sans-serif, uniform stroke weight, wide tracking, cinematic poster feel — do NOT write the font name",
        "preview": "CINEMATIC POSTER",
    },
    "montserrat": {
        "label": "Montserrat  —  Geometric Bold",
        "google_font": "Montserrat",
        "description": "geometric bold sans-serif, perfectly circular curves, balanced letter-spacing, clean and modern — do NOT write the font name",
        "preview": "Clean & Modern",
    },
    "playfair": {
        "label": "Playfair Display  —  Elegant Serif",
        "google_font": "Playfair Display",
        "description": "high-contrast elegant serif, thin hairline strokes with thick stems, classical editorial newspaper feel, mixed case — do NOT write the font name",
        "preview": "Elegant Serif",
    },
    "raleway": {
        "label": "Raleway  —  Thin Elegant",
        "google_font": "Raleway",
        "description": "thin-weight elegant sans-serif, wide open letter-spacing, airy and minimal luxury feel — do NOT write the font name",
        "preview": "Airy & Minimal",
    },
    "barlow": {
        "label": "Barlow Condensed  —  Clean Condensed",
        "google_font": "Barlow Condensed",
        "description": "semi-condensed clean grotesque sans-serif, moderate stroke weight, balanced proportions, technical and neutral — do NOT write the font name",
        "preview": "Technical & Clean",
    },
    "space_grotesk": {
        "label": "Space Grotesk  —  Tech Futuristic",
        "google_font": "Space Grotesk",
        "description": "quirky geometric grotesque sans-serif, slightly irregular terminals, tech-forward futuristic feel, medium-bold weight — do NOT write the font name",
        "preview": "Tech Futuristic",
    },
}

# Default used before user picks a preference
DEFAULT_FONT_KEY = "anton"


def get_font_description(font_key: str) -> str:
    """Return the prompt-safe visual description for the given font key."""
    style = FONT_STYLES.get(font_key, FONT_STYLES[DEFAULT_FONT_KEY])
    return style["description"]


def font_keyboard_rows() -> list[tuple[str, str]]:
    """
    Return (label, callback_data) pairs for building a Telegram inline keyboard.
    callback_data format: 'font_<key>'
    """
    return [(v["label"], f"font_{k}") for k, v in FONT_STYLES.items()]
