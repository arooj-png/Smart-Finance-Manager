from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, date
import os, json
import math

# Load .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Storage Files ---
LEDGER_FILE = "ledger.json"
GOALS_FILE = "goals.json"

# Initialize files if they don't exist
def init_files():
    if not os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- AI Advice Helper ---
def get_ai_advice(income, expense, balance, goals):
    """Generate AI advice with fallback to static tips"""
    try:
        # Try to use LangChain if available
        from langchain.prompts import PromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.chains import LLMChain
        
        if os.environ.get("GOOGLE_API_KEY"):
            llm = ChatGoogleGenerativeAI(model="gemini-flash-2.5", temperature=0.3)
            template = """
            You are a Pakistani financial advisor for small business owners.
            Income: {income} PKR
            Expense: {expense} PKR  
            Balance: {balance} PKR
            Goals: {goals}
            
            Give 3 short, practical tips in Urdu-English mix for Pakistani context.
            Focus on: savings, inflation, business growth, zakat if applicable.
            """
            prompt = PromptTemplate(template=template, input_variables=["income", "expense", "balance", "goals"])
            chain = LLMChain(llm=llm, prompt=prompt)
            return chain.run(income=income, expense=expense, balance=balance, goals=goals)
    except Exception:
        pass
    
    # Fallback advice
    advice_parts = []
    
    if balance > 0:
        advice_parts.append("✅ Aapka balance positive hai! Bachat karne ka plan banayein.")
        if balance > 100000:
            advice_parts.append("💰 Zakat calculate karein (2.5% of savings above 135,000 PKR)")
    else:
        advice_parts.append("⚠️ Expenses zyada hain. Roz ka budget banayein.")
    
    advice_parts.append("📈 Mahangai 20% hai - prices review karte rahein.")
    advice_parts.append("🎯 Financial goals set karein aur progress track karein.")
    
    return "\n".join(advice_parts)

# --- Inflation Calculator ---
def calculate_inflation_impact(balance, months=6, inflation_rate=0.20):
    """Calculate how inflation affects balance over time"""
    monthly_inflation = inflation_rate / 12
    future_balance = balance * ((1 - monthly_inflation) ** months)
    loss = balance - future_balance
    return {
        "current_balance": balance,
        "future_balance": round(future_balance, 2),
        "inflation_loss": round(loss, 2),
        "months": months
    }

# --- Routes ---
@app.route("/")
def serve_frontend():
    return send_file("frontend.html")

@app.route("/add-entry/", methods=["POST"])
def add_entry():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ["description", "amount", "type"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate amount
        try:
            amount = float(data["amount"])
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount format"}), 400
        
        # Validate type
        if data["type"] not in ["income", "expense"]:
            return jsonify({"error": "Type must be 'income' or 'expense'"}), 400
        
        ledger = load_json(LEDGER_FILE)
        record = {
            "id": len(ledger) + 1,
            "description": data["description"],
            "amount": amount,
            "type": data["type"],
            "category": data.get("category", "General"),
            "date": str(datetime.now().date()),
            "timestamp": datetime.now().isoformat()
        }
        
        ledger.append(record)
        save_json(LEDGER_FILE, ledger)
        
        return jsonify({"message": "Entry added successfully", "data": record}), 201
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/summary/", methods=["GET"])
def get_summary():
    try:
        ledger = load_json(LEDGER_FILE)
        goals = load_json(GOALS_FILE)
        
        # Calculate totals
        income = sum(x["amount"] for x in ledger if x["type"] == "income")
        expense = sum(x["amount"] for x in ledger if x["type"] == "expense")
        balance = income - expense
        
        # Category breakdown
        categories = {}
        for entry in ledger:
            cat = entry.get("category", "General")
            if cat not in categories:
                categories[cat] = {"income": 0, "expense": 0}
            categories[cat][entry["type"]] += entry["amount"]
        
        # Calculate goal progress
        total_goal_amount = sum(goal["target_amount"] for goal in goals)
        goal_progress = (balance / total_goal_amount * 100) if total_goal_amount > 0 else 0
        
        # Inflation impact
        inflation_data = calculate_inflation_impact(balance)
        
        # AI Advice
        goals_text = ", ".join([f"{g['name']} ({g['target_amount']} PKR)" for g in goals])
        advice = get_ai_advice(income, expense, balance, goals_text)
        
        # Debt analysis
        debt_advice = ""
        if balance < 0:
            debt_advice = f"⚠️ Aapka debt hai {abs(balance)} PKR. Roz ka {abs(balance)/30:.0f} PKR save karein to 1 month mein clear ho jayega."
        
        return jsonify({
            "income": income,
            "expense": expense,
            "balance": balance,
            "categories": categories,
            "goals": goals,
            "goal_progress": round(goal_progress, 2),
            "inflation_impact": inflation_data,
            "advice": advice,
            "debt_advice": debt_advice,
            "total_entries": len(ledger)
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/add-goal/", methods=["POST"])
def add_goal():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ["name", "target_amount", "target_date"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        try:
            target_amount = float(data["target_amount"])
            if target_amount <= 0:
                return jsonify({"error": "Target amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid target amount format"}), 400
        
        goals = load_json(GOALS_FILE)
        goal = {
            "id": len(goals) + 1,
            "name": data["name"],
            "target_amount": target_amount,
            "target_date": data["target_date"],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        goals.append(goal)
        save_json(GOALS_FILE, goals)
        
        return jsonify({"message": "Goal added successfully", "data": goal}), 201
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/notify/", methods=["GET"])
def daily_notification():
    try:
        ledger = load_json(LEDGER_FILE)
        goals = load_json(GOALS_FILE)
        
        # Today's entries
        today = str(date.today())
        today_entries = [entry for entry in ledger if entry.get("date") == today]
        
        today_income = sum(entry["amount"] for entry in today_entries if entry["type"] == "income")
        today_expense = sum(entry["amount"] for entry in today_entries if entry["type"] == "expense")
        
        # Overall summary
        total_income = sum(entry["amount"] for entry in ledger if entry["type"] == "income")
        total_expense = sum(entry["amount"] for entry in ledger if entry["type"] == "expense")
        balance = total_income - total_expense
        
        # Generate notification
        if today_entries:
            notification = f"📊 Aaj: +{today_income:.0f} PKR income, -{today_expense:.0f} PKR expense. Total balance: {balance:.0f} PKR"
        else:
            notification = f"📊 Aaj koi entry nahi. Total balance: {balance:.0f} PKR"
        
        if goals:
            active_goals = [g for g in goals if g["status"] == "active"]
            if active_goals:
                notification += f" | 🎯 {len(active_goals)} active goals"
        
        return jsonify({"notification": notification, "today_entries": len(today_entries)})
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/entries/", methods=["GET"])
def get_entries():
    try:
        ledger = load_json(LEDGER_FILE)
        # Return last 50 entries
        return jsonify({"entries": ledger[-50:]})
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Initialize files on startup
init_files()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)