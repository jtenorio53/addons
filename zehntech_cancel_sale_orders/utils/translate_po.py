import os
import re
from deep_translator import GoogleTranslator

# Define language mappings based on the filenames
language_codes = {
    "fr.po": "fr",      # French
    "es.po": "es",      # Spanish
    "ja_JP.po": "ja",   # Japanese
    "de.po": "de"       # German
}

# Path to the i18n folder
i18n_folder = "i18n"

# Function to translate text
def translate_text(text, lang_code):
    try:
        return GoogleTranslator(source='auto', target=lang_code).translate(text)
    except Exception as e:
        print(f"Error translating '{text}' to {lang_code}: {e}")
        return text  # Return original text if translation fails

# Process each .po file in the i18n directory
for file_name, lang_code in language_codes.items():
    file_path = os.path.join(i18n_folder, file_name)

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        continue

    print(f"🔄 Translating: {file_name} ({lang_code.upper()})")

    # Read the PO file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Regex pattern to find msgid and empty msgstr
    pattern = r'msgid\s*"([^"]+)"\s*\nmsgstr\s*""'

    # Replace msgstr with the translated msgid
    translated_content = re.sub(
        pattern, 
        lambda match: f'msgid "{match.group(1)}"\nmsgstr "{translate_text(match.group(1), lang_code)}"', 
        content
    )

    # Overwrite the same file with translated content
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(translated_content)

    print(f"✅ Translated & saved: {file_path}")

print("\n🎉 Translation completed for all languages!")
