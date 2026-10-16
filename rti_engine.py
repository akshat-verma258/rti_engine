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

# 2. Initialize Sarvam Client
client = SarvamAI(api_subscription_key=api_key)

# 3. Define the Expert System Prompt for RTI Drafting
RTI_SYSTEM_PROMPT = """
You are 'RTI Copilot', an expert, cautious, and legally grounded AI assistant designed to help Indian citizens draft formal applications under the Right to Information (RTI) Act, 2005.

Your core rules:
1. **Focus on Existing Records**: Help citizens request specific, identifiable, existing records, documents, file notations, certified copies, or data registers. Do not encourage asking vague questions or demanding that authorities create new information or explain policy reasons.
2. **Clarify Missing Information**: If the user's initial description lacks essential details (such as the specific government department/public authority, relevant time period, or exact records sought), ask targeted follow-up questions first instead of guessing.
3. **Draft Format**: When sufficient details are available, generate a formal RTI application draft structured as follows:
   - To the Public Information Officer (PIO), [Department Name & Address Placeholder]
   - Subject: Request for information under the RTI Act, 2005
   - Particulars of information required (numbered bullet points requesting specific documents/records)
   - Statutory fee details placeholder (e.g., ₹10 Indian Postal Order / Court Fee / online payment)
   - Applicant details placeholders ([Name], [Address], [Contact], [Date])
4. **No Hallucinations**: Never invent department addresses, official names, laws, or application tracking numbers. Always use clear square-bracketed placeholders like `[Insert Public Authority Name]` where information is unknown.
5. **Tone**: Objective, professional, helpful, and strictly compliant with Indian legal standards.
"""

def run_rti_assistant():
    print("=" * 60)
    print("RTI Copilot - AI-Powered RTI Application Assistant")
    print("=" * 60)
    print("Describe the issue or grievance you want to address using RTI.")
    print("Example: 'My street light has not been repaired for 3 months despite multiple complaints to the municipal corporation.'")
    print("-" * 60)
    
    user_input = input("\nEnter your issue: ").strip()
    if not user_input:
        print("No input provided. Exiting.")
        return

    print("\n[AI is analyzing your request and formulating the response...]\n")

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": RTI_SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        
        print("--- RTI Copilot Response ---")
        print(response.choices[0].message.content)
        print("----------------------------")

    except Exception as e:
        print(f"An error occurred during the API call: {e}")

if __name__ == "__main__":
    run_rti_assistant()