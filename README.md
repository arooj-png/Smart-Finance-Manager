💸 Smart Finance Manager (Pakistan Edition)

“Rozana hisaab, modern tareeqay se!”
This is my student project where I mix AI, finance tracking, and Urdu-English advice to solve a very real problem in Pakistan:
Most shopkeepers & students don’t have a proper system to track daily income/expense, and when they do, it’s usually in registers (khaata) that are easy to forget.

So… I built Smart Finance Manager ✨

🚀 Features

📊 Track Income & Expenses
Simple add-entry form, supports categories like food, rent, utilities.

💼 Balance & Goals
Shows current balance, progress towards savings goals, and warns about debt.

🤖 AI Financial Advice (Roman-Urdu mix)
LLM (Gemini/OpenAI) generates short, SMS-friendly tips like:

“Rozana sales ka hisaab rakho. Save 5% daily.”

🌍 Urdu Translation Button
One click = your AI advice converted into Urdu script (اُردو) so you can share via WhatsApp or SMS.

📉 Inflation Awareness
Shows how much your balance will shrink after 6 months of inflation (20% annual assumption).
Because… real life.

🔥 Modern UI
Tailwind + React cards, pie charts, progress bars → not a boring spreadsheet, but an actual app.

🛠️ Stack

Frontend: React + Tailwind CSS (modern dashboard vibes ✨)

Backend: Flask (Python) + Flask-CORS

AI: Gemini (via LangChain) → fallback to static Roman-Urdu advice if no API key

Storage: Local JSON (so even students with no DB setup can run it)

⚡ Installation

Clone repo

Create venv & install dependencies:

python -m venv venv
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
pip install flask flask-cors python-dotenv langchain langchain-google-genai


Add .env with your API key:

GOOGLE_API_KEY=your_gemini_api_key_here


Run backend:

python backend.py


Open http://127.0.0.1:8000/ in your browser.

💡 Why this matters in Pakistan?

Shopkeepers mostly rely on registers (khaata), not apps.

People don’t understand English-only financial apps.

Inflation eats into savings, but no one calculates it.

Urdu/Urdu-English advice makes finance accessible for small shopkeepers & students.

This project bridges that gap with AI + bilingual support + modern dashboard.

🤔 Future Ideas

📱 Mobile-friendly PWA

📤 Export khaata (ledger) as PDF in Urdu/English

📲 WhatsApp bot for daily expense entry

💳 Micro-finance loan repayment reminders

🎓 Note (student disclaimer)

This is a learning project I made as a Computer Engineering student.
If it crashes, gives weird advice, or yells at you about saving money… that’s just the AI acting desi. 😅
