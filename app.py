import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from sarvamai import SarvamAI
from pypdf import PdfReader
import io

# 1. Load .env file automatically using standard libraries
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
    raise ValueError("SARVAM_API_KEY is missing or invalid in your .env file.")

# 2. Initialize Sarvam Client and Flask App
client = SarvamAI(api_subscription_key=api_key)
app = Flask(__name__)

# 3. Expert System Prompt for RTI Drafting
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate_rti():
    try:
        issue = ""
        target_lang = "en-IN"
        doc_text = ""

        # Support both JSON requests and multipart/form-data (with file uploads)
        if request.is_json:
            data = request.json or {}
            issue = data.get("issue", "")
            target_lang = data.get("target_lang", "en-IN")
            doc_text = data.get("doc_text", "")
        else:
            issue = request.form.get("issue", "")
            target_lang = request.form.get("target_lang", "en-IN")
            
            uploaded_file = request.files.get("file")
            if uploaded_file:
                filename = uploaded_file.filename.lower()
                file_bytes = uploaded_file.read()
                if filename.endswith(".pdf"):
                    try:
                        reader = PdfReader(io.BytesIO(file_bytes))
                        for page in reader.pages:
                            extracted = page.extract_text()
                            if extracted:
                                doc_text += extracted + "\n"
                    except Exception as pdf_err:
                        print(f"PDF extraction error: {pdf_err}")
                elif filename.endswith(".txt"):
                    doc_text = file_bytes.decode("utf-8", errors="ignore")

        if not issue:
            return jsonify({"error": "Issue description is required."}), 400

        # 1. Combine issue description with document context if available
        combined_prompt = issue
        if doc_text:
            combined_prompt = f"User Issue / Grievance:\n{issue}\n\nSupporting Document Evidence:\n---\n{doc_text}\n---"

        # 2. Generate English Draft via Sarvam Chat Completion
        chat_resp = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": RTI_SYSTEM_PROMPT},
                {"role": "user", "content": combined_prompt}
            ]
        )
        english_draft = chat_resp.choices[0].message.content

        # 3. Translate if target language is not English
        final_draft = english_draft
        if target_lang != "en-IN":
            trans_resp = client.text.translate(
                input=english_draft,
                source_language_code="en-IN",
                target_language_code=target_lang,
                model="sarvam-translate:v1"
            )
            final_draft = getattr(trans_resp, "translated_text", str(trans_resp))

        return jsonify({"draft": final_draft})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)