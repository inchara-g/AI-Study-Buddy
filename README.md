\# 📚 AI Study Buddy



AI Study Buddy is an AI-powered study assistant built with Streamlit and Gemini.



It helps students:

\- Ask academic questions through chat

\- Upload a photo or screenshot of a question

\- Get simple explanations and answers

\- Continue asking follow-up questions

\- Generate a study summary

\- Send the study summary to email



\## ✨ Features



\- 💬 AI study chat

\- 🖼️ Question image upload

\- 🤖 Gemini AI assistance

\- 📖 Simple explanations

\- 📧 Study summary through Gmail

\- 📝 Conversation-based study support



\## 🛠️ Technologies Used



\- Python

\- Streamlit

\- Google Gemini API

\- Gmail SMTP

\- Git \& GitHub




## 📁 Project Structure

```text
AI-Study-Buddy/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
└── .gitignore

⚙️ Installation
1. Clone the repository
git clone https://github.com/inchara-g/AI-Study-Buddy.git
cd AI-Study-Buddy

2.Create a virtual environment
python -m venv venv

3.Activate the virtual environment
For Windows PowerShell:
venv\Scripts\Activate.ps1

4. Install dependencies
pip install -r requirements.txt

5. Run the application
python -m streamlit run app.py


add this:

```markdown
## 🔐 Configure Secrets

Create this file:

```text
.streamlit/secrets.toml

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GMAIL_ADDRESS = "YOUR_GMAIL_ADDRESS"
GMAIL_APP_PASSWORD = "YOUR_GMAIL_APP_PASSWORD"
