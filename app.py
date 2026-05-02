from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import sqlite3
import re
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Get the absolute path to the directory this file is in
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Force Flask to use the exact 'static' folder next to app.py
app = Flask(__name__, static_folder=os.path.join(basedir, 'static'))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    
    pitch_data = data.get("pitch_data")

    if not pitch_data or pitch_data.strip() == "":
        pitch_data = "A modern AI-powered SaaS tool for local businesses to automate tasks."

    # THE BRUTALLY HONEST VC PROMPT
    system_prompt = """
You are FOUNDERLENS, an elite, ruthlessly objective Venture Capital analyst and technical architect.
The user will provide a brief "Startup Pitch". 

CRITICAL INSTRUCTIONS:
1. DO NOT complain about insufficient data. Extrapolate their brief idea into a full concept so you can properly evaluate it.
2. BE BRUTALLY HONEST. Do not sugarcoat. Act like a ruthless investor whose own money is on the line. 
3. DETECT OVER-ENGINEERING. Heavily penalize ideas that are "solutions looking for a problem" or unnecessarily use AI just for the sake of hype.
4. EVALUATE PROBLEM-SOLUTION FIT. Focus on actual business viability, unit economics, market friction, and customer acquisition. If the idea is fundamentally flawed, tear it apart constructively in the summary and weaknesses.
5. You MUST invent realistic MARKET_DATA and VISUAL_DATA arrays based on the industry to populate the frontend charts.

OUTPUT FORMAT:
You MUST output your response in this EXACT text format. Do not use markdown code blocks, just raw text.

PROBLEM_SCORE: [Number 1-100. Be harsh. Only severe, burning problems get 80+]
SOLUTION_SCORE: [Number 1-100. Penalize over-engineering and bloated features]
FIT_SCORE: [Number 1-100. True problem-solution fit]

MARKET_DATA:
TAM: [e.g., $12.5B]
USERS: [e.g., 4.2M SMBs]
GROWTH: [e.g., 18.5%]

VISUAL_DATA:
demand_curve: [comma separated list of 10 numbers between 0-100]
competition_curve: [comma separated list of 10 numbers between 0-100]
growth_projection: [comma separated list of 10 numbers progressively increasing or decreasing based on viability]

SUMMARY:
[1 paragraph delivering a brutally honest, no-nonsense evaluation of the business viability and problem-solution fit. State clearly if it will fail.]

STRENGTHS:
- [Objective strength 1 - or state if there are none]
- [Objective strength 2]
- [Objective strength 3]

WEAKNESSES:
- [Brutal risk 1 - focus on over-engineering, market apathy, or lack of friction]
- [Brutal risk 2 - business/revenue model flaw]
- [Brutal risk 3 - technical execution or churn risk]

RECOMMENDATIONS:
- [Hard pivot or actionable step 1]
- [Actionable step 2 for achieving true problem-solution fit]
- [Actionable step 3]
"""

    try:
        # 1. Call the Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pitch_data}
            ],
            temperature=0.6 
        )
        
        ai_result = response.choices[0].message.content

        # 2. DATABASE SAVING PROTOCOL
        try:
            # Extract the scores from the AI's text using regex
            prob_match = re.search(r"PROBLEM_SCORE:\s*(\d+)", ai_result)
            sol_match = re.search(r"SOLUTION_SCORE:\s*(\d+)", ai_result)
            fit_match = re.search(r"FIT_SCORE:\s*(\d+)", ai_result)
            
            p_score = float(prob_match.group(1)) if prob_match else 0.0
            s_score = float(sol_match.group(1)) if sol_match else 0.0
            f_score = float(fit_match.group(1)) if fit_match else 0.0

            # Connect to SQLite and save the data
            conn = sqlite3.connect("founderlens.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO telemetry_logs (pitch_text, problem_score, solution_score, fit_score) VALUES (?, ?, ?, ?)", 
                (pitch_data, p_score, s_score, f_score)
            )
            conn.commit()
            idea_id = cursor.lastrowid
            conn.close()
            print(f"✅ Idea #{idea_id} saved to database with Fit Score: {f_score}")
        except Exception as db_err:
            print(f"⚠️ Database save failed: {db_err}")
            idea_id = None

        # 3. Return the result to the React frontend
        return jsonify({"result": ai_result, "idea_id": idea_id})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Diagnostics failed."}), 500

if __name__ == "__main__":
    app.run(debug=True)