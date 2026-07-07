import os
import json
import base64
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
import pdfkit
import gspread
import traceback
import re
from google.oauth2.service_account import Credentials
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

def parse_duration_to_days(duration_str):
    """
    Converts a string like '1 Month (30 Days)' or '1.5 Months (45 Days)' to integer days.
    """
    match = re.search(r'\((\d+)\s*Days?\)', duration_str)
    if match:
        return int(match.group(1))
    else:
        # fallback: parse first number and unit
        number = float(duration_str.split()[0])
        unit = duration_str.split()[1].lower()
        if "month" in unit:
            return int(number * 30)
        elif "week" in unit:
            return int(number * 7)
        elif "day" in unit:
            return int(number)
        else:
            raise ValueError(f"Unknown duration format: {duration_str}")

app = Flask(__name__)

# === Config ===
SHEET_ID = "sheetid"
SENDGRID_API_KEY = "sendgrid"
SENDER_EMAIL = "mailid"
RECIPIENT_FALLBACK = SENDER_EMAIL

SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "service_account.json")

if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise RuntimeError(f"Service account JSON not found at {SERVICE_ACCOUNT_FILE}")

# Google Sheets auth
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)

# SendGrid client
sg_client = SendGridAPIClient(SENDGRID_API_KEY)

# pdfkit config
WKHTMLTOOL_PATHS = ["/usr/local/bin/wkhtmltopdf", "/usr/bin/wkhtmltopdf", "/usr/bin/wkhtmltopdf-binary"]
wkpath = next((p for p in WKHTMLTOOL_PATHS if os.path.exists(p)), None)
pdf_config = pdfkit.configuration(wkhtmltopdf=wkpath) if wkpath else None

def make_offer_html(data):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Offer Letter - CodeOG</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {{
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
  background: #f9fafb;
}}

.page-container {{
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem 3rem;
  position: relative;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}}

.page-container::before {{
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 400px;
  height: 400px;
  background: url('https://uploads.onecompiler.io/43wyt2f5a/43x2vrn6x/new.png') no-repeat center center;
  background-size: contain;
  opacity: 0.08;
  transform: translate(-50%, -50%);
  z-index: 0;
}}

.header {{
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 1.5rem;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}}

.header img {{
  height: 100px;
  width: auto;
}}

.header-text {{
  flex: 1;
  text-align: center;
  position: relative;
  z-index: 1;
}}

.header-text h1 {{
  font-size: 2.8rem;
  font-weight: 700;
  color: #4f46e5;
  margin: 0;
}}

.header-text h2 {{
  font-size: 1rem;
  font-weight: 500;
  color: #4338ca;
  margin-top: 0.25rem;
}}

.header-line {{
  height: 2px;
  background-color: #c7d2fe;
  margin-top: 1rem;
}}

.letter-body {{
  padding: 1rem 0;
  position: relative;
  z-index: 1;
}}

.letter-body p {{
  line-height: 1.7;
  color: #111827;
}}

.letter-body h2 {{
  font-size: 1.5rem;
  font-weight: 600;
  color: #4f46e5;
  margin-top: 1rem;
  margin-bottom: 0.75rem;
}}

.extra-content {{
  margin-top: 1.5rem;
}}

.extra-content h3 {{
  font-size: 1.2rem;
  font-weight: 600;
  color: #4f46e5;
  margin-bottom: 0.5rem;
}}

.extra-content ul {{
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}}

.extra-content ul li {{
  margin-bottom: 0.5rem;
}}

.footer {{
  margin-top: 0.5rem;
  text-align: left;
  position: relative;
  z-index: 1;
}}

.footer img {{
  height: 60px;
  margin-bottom: 0.5rem;
}}

.footer p {{
  margin: 0;
  color: #1e1b4b;
}}
</style>
</head>
<body>
  <div class="page-container">

    <!-- Header -->
    <div class="header">
      <img src="https://uploads.onecompiler.io/43wyt2f5a/43x2vrn6x/new.png" alt="CodeOG Logo">
      <div class="header-text">
        <h1>Offer Letter</h1>
        <h2>CodeOG | Forge Your Future</h2>
        <div class="header-line"></div>
      </div>
    </div>

    <!-- Body -->
    <div class="letter-body">
      <p style="text-align:right; font-size:0.85rem; color:#6b7280;">Date: {data['date']}</p>

      <h2>Dear {data['name']},</h2>

      <p>
        We are pleased to offer you an internship as <strong>{data['domain']}</strong> intern in <strong>CodeOG</strong>
        for a period of <strong>{data['duration']}</strong>, starting from <strong>{data['start_date']}</strong> and ending on <strong>{data['end_date']}</strong>.
      </p>

      <p>
        During this internship, you will work on projects aligned with your learning objectives under the guidance of your mentor, Ms. Anshika Singh. You will gain practical skills and professional experience in a dynamic, collaborative environment.
      </p>

      <div class="extra-content">
        <h3>Position and Terms</h3>
        <ul>
          <li>Role: {data['domain']} Intern</li>
          <li>Start Date: {data['start_date']}</li>
          <li>End Date: {data['end_date']}</li>
          <li>Schedule: Flexible hours, typically 3–5 hours/day</li>
          <li>Mode: Fully remote internship</li>
          <li>Collaboration: Regular online meetings with mentor and team</li>
        </ul>

        <h3>Responsibilities and Mentorship</h3>
        <ul>
          <li>Complete assigned tasks and submit deliverables on time.</li>
          <li>Participate in team meetings and progress reviews.</li>
          <li>Collaborate with your mentor on learning objectives.</li>
          <li>Maintain proper documentation for all work.</li>
          <li>Follow coding and project guidelines provided.</li>
        </ul>

        <h3>Policies and Conditions</h3>
        <ul>
          <li>All work is confidential and property of CodeOG.</li>
          <li>Intellectual Property (IP) of work produced belongs to CodeOG.</li>
          <li>Acceptable use of company resources and data is mandatory.</li>
          <li>Early termination may occur if terms are violated.</li>
        </ul>

        <h3>Acceptance</h3>
        <p>Please confirm your acceptance by <strong>{data['acceptance_deadline']}</strong>. You may acknowledge by replying to this email or signing and returning the attached acknowledgment form.</p>
      </div>

      <p style="margin-bottom:0.5rem;">Sincerely,</p>
    </div>

    <!-- Footer -->
    <div class="footer">
      <img src="https://uploads.onecompiler.io/43wyt2f5a/43wyvf7r7/1000128892.png" alt="CEO Signature">
      <p><strong>Abhishek Yadav M</strong></p>
      <p style="font-size:0.85rem;color:#4338ca;">CEO, CodeOG</p>
      <p style="font-size:0.8rem; color:#6b7280; margin-top:1rem;">Contact: info@codeog.com | (264) 280-17168</p>
    </div>

  </div>
</body>
</html>
"""




@app.route("/")
def home():
    return "CodeOG Cloud Project running."

@app.route("/process-latest", methods=["POST", "GET"])
@app.route("/process-latest/", methods=["POST", "GET"])
def process_latest():
    if request.method == "GET":
        return "Use POST with JSON payload to generate offer letter.", 200

    try:
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet("Form Responses 1")
        records = ws.get_all_records()
        if not records:
            return jsonify({"status": "error", "message": "No submissions yet."}), 404
        latest = records[-1]

        def find_key(possible_names):
            for k in latest.keys():
                kn = k.strip().lower()
                for p in possible_names:
                    if p.lower() == kn or p.lower() in kn or kn in p.lower():
                        return k
            return None

        name = latest.get(find_key(["name", "full name", "your name"]), "Candidate")
        gender = latest.get(find_key(["gender"]), "")
        contact = latest.get(find_key(["contact number", "phone", "contact"]), "")
        college = latest.get(find_key(["college", "college name"]), "")
        domain = latest.get(find_key(["domain", "internship domain"]), "")
        duration = latest.get(find_key(["internship duration", "duration"]), "1 Month")

        # --- Calculate dates ---
        def get_internship_dates(duration_str):
            days = parse_duration_to_days(duration_str)
            today = datetime.now().date()
    
            # Acceptance deadline
            acceptance_deadline = today + timedelta(days=7)
    
            # Default next month start
            next_month = today.month + 1 if today.month < 12 else 1
            next_year = today.year + 1 if today.month == 12 else today.year
            start_dt = datetime(next_year, next_month, 1).date()
    
            # If acceptance deadline is after the 1st, move start to 15th
            if acceptance_deadline >= start_dt:
                start_dt = datetime(next_year, next_month, 15).date()
    
            end_dt = start_dt + timedelta(days=days)
            return start_dt, end_dt, acceptance_deadline


        start_dt, end_dt, acceptance_deadline = get_internship_dates(duration)

        # --- Add acceptance deadline (7 days from today) ---
        acceptance_deadline = (datetime.now() + timedelta(days=7)).strftime("%d %B %Y")

        # --- Build data dictionary ---
        data = {
            "name": str(name).strip(),
            "gender": str(gender).strip(),
            "contact": str(contact).strip(),
            "college": str(college).strip(),
            "domain": str(domain).strip(),
            "duration": str(duration).strip(),
            "date": datetime.now().strftime("%d %B %Y"),
            "start_date": start_dt.strftime("%d %B %Y"),
            "end_date": end_dt.strftime("%d %B %Y"),
            "acceptance_deadline": acceptance_deadline,
            "submission_row": latest
        }

        # --- Build PDF ---
        html = make_offer_html(data)
        pdf_path = "/tmp/offer_letter.pdf"
        if pdf_config:
            pdfkit.from_string(html, pdf_path, configuration=pdf_config)
        else:
            pdfkit.from_string(html, pdf_path)

        with open(pdf_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        recipient_email = latest.get('Email') or latest.get('Email Address') or latest.get('email') or RECIPIENT_FALLBACK

        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=recipient_email,
            subject=f"Offer Letter - {data['name']} - {data['domain']}",
            plain_text_content=(
                f"Dear {data['name']},\n\n"
                "Please find your Offer Letter attached.\n\n"
                "Regards,\n"
                "CodeOG Internship Team\n\n"
                "Some very important points you have to remember during this internship:\n"
                "1. Update your LinkedIn Profile and share all your achievements (Offer Letter / Internship Completion Certificate) which you got from us and tag @CodeOG, also use #CodeOG.\n"
                "2. If your project/code is found copied, your internship will be terminated and you will be banned from further opportunities from us.\n"
                "3. Share video of the completed task on LinkedIn and tag @CodeOG, also use #CodeOG.\n"
                "4. For Tech Internship, maintain a separate GitHub repository (name it CODEOG for all the tasks) and share the link of the GitHub repo in the task submission form (it will be given later through email).\n"
            )
        )

        attachment = Attachment(
            FileContent(encoded),
            FileName("Offer_Letter.pdf"),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        message.attachment = attachment

        resp = sg_client.send(message)
        return jsonify({"status": "success", "sendgrid_status": resp.status_code, "recipient": recipient_email})

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
