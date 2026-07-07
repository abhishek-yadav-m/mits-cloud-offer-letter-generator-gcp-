# 📄 MITS Cloud Offer Letter Generator

A cloud-based web application that automates internship offer letter generation by reading applicant details from Google Forms, generating a professional PDF offer letter, and emailing it to the applicant automatically.

---

## 🚀 Features

- 📄 Automatically generates internship offer letters in PDF format
- 📬 Sends personalized offer letters via SendGrid
- 📊 Reads applicant data from Google Forms / Google Sheets
- 📅 Automatically calculates internship start and end dates
- ☁️ Deployable on Google Cloud Run
- 🎨 Professionally designed HTML offer letter
- 🔒 Secure integration using Google Service Account

---

## 🛠️ Technologies Used

### Backend
- Python
- Flask
- Gunicorn

### Google Cloud
- Google Cloud Run
- Google Sheets API
- Service Account Authentication

### Libraries
- pdfkit
- gspread
- google-auth
- SendGrid API

---

## 📂 Project Structure

```
MITS-Cloud-Offer-Letter-Generator/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
├── .gitignore
├── service_account.json      # Local only (ignored by Git)
└── screenshots/
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/MITS-Cloud-Offer-Letter-Generator.git

cd MITS-Cloud-Offer-Letter-Generator
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Configure the following environment variables before running the application.

```
SENDGRID_API_KEY
SENDER_EMAIL
SHEET_ID
SERVICE_ACCOUNT_FILE
```

---

## ▶️ Run Locally

```bash
python app.py
```

The application will start on

```
http://localhost:8080
```

---

## ☁️ Deploy to Google Cloud Run

Build the container

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/mits-offer
```

Deploy

```bash
gcloud run deploy mits-offer \
--image gcr.io/PROJECT_ID/mits-offer \
--platform managed \
--region asia-south1 \
--allow-unauthenticated
```

---

## 📸 Screenshots

### Offer Letter

Add the generated offer letter image here.

```
screenshots/offer-letter.png
```

---

## 📄 Workflow

```
Google Form
      │
      ▼
Google Sheets
      │
      ▼
Flask Application
      │
      ▼
Generate HTML
      │
      ▼
Generate PDF
      │
      ▼
SendGrid
      │
      ▼
Applicant receives Offer Letter
```

---

## 📦 Dependencies

```
Flask
gspread
google-auth
pdfkit
SendGrid
Gunicorn
```

---

## 🔒 Security

This repository does **not** include:

- Service Account JSON
- API Keys
- Environment Variables

These must be configured locally or through Google Cloud Run environment variables.

---

## 👨‍💻 Author

**Abhishek Yadav M**

Computer Science Engineering Student

GitHub:
https://github.com/abhishek-yadav-m

LinkedIn:
(Add your LinkedIn URL)

---

## 📜 License

This project is intended for educational and portfolio purposes.
