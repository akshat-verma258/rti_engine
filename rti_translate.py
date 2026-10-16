import os
from pathlib import Path
from sarvamai import SarvamAI

# 1. Load .env file automatically
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

api_key = os.environ.get("SARVAM_API_KEY")
if not api_key or api_key == "YOUR_REAL_API_KEY":
    print("ERROR: SARVAM_API_KEY is missing or invalid in your .env file.")
    exit(1)

client = SarvamAI(api_subscription_key=api_key)

RTI_SYSTEM_PROMPT = """
You are 'RTI Copilot', an expert and legally grounded AI assistant designed to help Indian citizens draft formal applications under the Right to Information (RTI) Act, 2005.
Generate a formal RTI application draft structured with:
- To the Public Information Officer (PIO), [Department Name & Address Placeholder]
- Subject: Request for information under the RTI Act, 2005
- Particulars of information required (numbered bullet points requesting specific documents/records)
- Statutory fee details placeholder (e.g., ₹10 Indian Postal Order)
- Applicant details placeholders ([Name], [Address], [Contact], [Date])
Keep placeholders clear using square brackets.
"""

# Dictionary of all 22 scheduled languages + English with BCP-47 codes
SUPPORTED_LANGUAGES = {
    "1": ("English", "en-IN"),
    "2": ("Hindi - हिन्दी", "hi-IN"),
    "3": ("Telugu - తెలుగు", "te-IN"),
    "4": ("Tamil - தமிழ்", "ta-IN"),
    "5": ("Bengali - বাংলা", "bn-IN"),
    "6": ("Marathi - मराठी", "mr-IN"),
    "7": ("Gujarati - ગુજરાતી", "gu-IN"),
    "8": ("Kannada - ಕನ್ನಡ", "kn-IN"),
    "9": ("Malayalam - മലയാളം", "ml-IN"),
    "10": ("Punjabi - ਪੰਜਾਬੀ", "pa-IN"),
    "11": ("Odia - ଓଡ଼ିଆ", "od-IN"),
    "12": ("Assamese - অসমীয়া", "as-IN"),
    "13": ("Urdu - اردو", "ur-IN"),
    "14": ("Nepali - नेपाली", "ne-IN"),
    "15": ("Sindhi - سنڌي", "sd-IN"),
    "16": ("Kashmiri - कॉशुर", "ks-IN"),
    "17": ("Konkani - कोंकणी", "kok-IN"),
    "18": ("Maithili - मैथिली", "mai-IN"),
    "19": ("Manipuri - মৈতৈলোন্", "mni-IN"),
    "20": ("Dogri - डोगरी", "doi-IN"),
    "21": ("Bodo - बड़ो", "brx-IN"),
    "22": ("Santali - ᱥᱟᱱᱛᱟᱲᱤ", "sat-IN"),
    "23": ("Sanskrit - संस्कृतम्", "sa-IN")
}

def run_translation_workflow():
    print("=" * 60)
    print("RTI Copilot - Multilingual RTI Drafting & Translation (23 Languages)")
    print("=" * 60)
    
    user_input = input("Describe your issue for the RTI application: ").strip()
    if not user_input:
        print("No input provided. Exiting.")
        return

    print("\nSelect Target Language:")
    for key, (lang_name, code) in SUPPORTED_LANGUAGES.items():
        print(f"{key:>2}. {lang_name} ({code})")
    
    choice = input("\nEnter choice number (1-23): ").strip()
    selected_lang = SUPPORTED_LANGUAGES.get(choice, ("Hindi - हिन्दी", "hi-IN"))
    target_lang_name, target_lang_code = selected_lang

    print(f"\n[1/2] Generating English RTI Draft via Sarvam Chat API...")
    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": RTI_SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        english_draft = response.choices[0].message.content
        print("\n--- Generated English Draft ---")
        print(english_draft)
        print("-------------------------------")

        # Translate if target language is not English
        if target_lang_code != "en-IN":
            print(f"\n[2/2] Translating draft to {target_lang_name} [{target_lang_code}] using Sarvam Translate API...")
            
            translation_response = client.text.translate(
                input=english_draft,
                source_language_code="en-IN",
                target_language_code=target_lang_code,
                model="sarvam-translate:v1"
            )
            
            translated_text = getattr(translation_response, "translated_text", str(translation_response))
            
            print(f"\n--- Translated RTI Draft ({target_lang_name}) ---")
            print(translated_text)
            print("-----------------------------------------------")
        else:
            print("\n[Skipping translation as English was selected.]")

    except Exception as e:
        print(f"An error occurred during API execution: {e}")

if __name__ == "__main__":
    run_translation_workflow()