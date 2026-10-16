import os
from pathlib import Path
from pypdf import PdfReader
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
You are 'RTI Copilot', an expert, cautious, and legally grounded AI assistant designed to help Indian citizens draft formal applications under the Right to Information (RTI) Act, 2005.

Your core rules:
1. **Focus on Existing Records**: Help citizens request specific, identifiable, existing records, documents, file notations, certified copies, or data registers. Do not encourage asking vague questions or demanding that authorities create new information or explain policy reasons.
2. **Ground in Documents**: If supporting documents are provided, treat them as evidence. Never claim a document says something it does not explicitly state. 
3. **Clarify Missing Information**: If essential details are missing, ask targeted follow-up questions first.
4. **Draft Format**: When sufficient details are available, generate a formal RTI application draft structured with:
   - To the Public Information Officer (PIO), [Department Name & Address Placeholder]
   - Subject: Request for information under the RTI Act, 2005
   - Particulars of information required (numbered bullet points requesting specific documents/records based on the user's issue and uploaded documents)
   - Statutory fee details placeholder (e.g., ₹10 Indian Postal Order / online payment)
   - Applicant details placeholders ([Name], [Address], [Contact], [Date])
5. **No Hallucinations**: Never invent department addresses, official names, laws, or tracking numbers. Use clear square-bracketed placeholders like `[Insert Name]` where information is unknown.
"""

def extract_text_from_pdf(pdf_path):
    """Extracts text content from a given PDF file path."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def run_rti_assistant_with_docs():
    print("=" * 60)
    print("RTI Copilot - Document-Grounded RTI Assistant")
    print("=" * 60)
    
    # Optional document upload
    file_path_input = input("Enter path to a supporting PDF document (or press Enter to skip): ").strip()
    document_content = ""
    
    if file_path_input:
        # Clean quotes if user dragged and dropped the file into cmd
        file_path_input = file_path_input.strip('"\'')
        if os.path.exists(file_path_input):
            if file_path_input.lower().endswith(".pdf"):
                print("[Extracting text from PDF...]")
                document_content = extract_text_from_pdf(file_path_input)
            elif file_path_input.lower().endswith(".txt"):
                with open(file_path_input, "r", encoding="utf-8") as f:
                    document_content = f.read()
            print(f"[Successfully loaded document: {Path(file_path_input).name}]\n")
        else:
            print("[Warning: File path not found. Proceeding without document.]\n")

    user_input = input("Describe your issue or what information you need: ").strip()
    if not user_input:
        print("No input provided. Exiting.")
        return

    # Combine user prompt with extracted document evidence if available
    combined_prompt = user_input
    if document_content:
        combined_prompt = (
            f"User Issue/Request:\n{user_input}\n\n"
            f"Supporting Document Evidence:\n---\n{document_content}\n---"
        )

    print("\n[AI is analyzing your request and documents...]\n")

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": RTI_SYSTEM_PROMPT},
                {"role": "user", "content": combined_prompt}
            ]
        )
        
        print("--- RTI Copilot Draft / Response ---")
        print(response.choices[0].message.content)
        print("------------------------------------")

    except Exception as e:
        print(f"An error occurred during the API call: {e}")

if __name__ == "__main__":
    run_rti_assistant_with_docs()