import os
from pathlib import Path
from sarvamai import SarvamAI

# 1. Locate and load the .env file using standard libraries
env_path = Path(__file__).parent / ".env"

if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# 2. Retrieve and validate the API key
api_key = os.environ.get("SARVAM_API_KEY")

if not api_key or api_key == "YOUR_REAL_API_KEY":
    print("ERROR: SARVAM_API_KEY is missing or still set to the placeholder in your .env file.")
    print("Please open C:\\Users\\verma\\Desktop\\Sarvam\\.env and paste your actual API key.")
    exit(1)

# 3. Initialize the Sarvam client
client = SarvamAI(api_subscription_key=api_key)

# 4. Make a minimal chat completion request
try:
    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "user", "content": "Reply with a short greeting."}
        ]
    )
    
    # 5. Print only the model's reply text
    print("Model Response:", response.choices[0].message.content)

except Exception as e:
    print(f"An error occurred during the API call: {e}")