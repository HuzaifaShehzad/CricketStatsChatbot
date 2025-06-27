import streamlit as st
import pandas as pd
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ✅ Load CSV
def load_cricket_data(csv_path):
    return pd.read_csv(csv_path)

# ✅ Convert DataFrame into string context
def get_context_from_df(df):
    context = ""
    for _, row in df.iterrows():
        sr = (row["Runs"] / row["Balls Faced"]) * 100 if row["Balls Faced"] > 0 else 0
        avg = (row["Runs"] / row["Innings"]) if row["Innings"] > 0 else 0
        context += (
            f"{row['Name']} | Matches: {row['Matches Played']}, Innings: {row['Innings']}, Runs: {row['Runs']}, "
            f"Balls Faced: {row['Balls Faced']}, 4s: {row['4s']}, 6s: {row['6s']}, "
            f"Highest Score: {row['Highest Score']}, 100s: {row['100s']}, 50s: {row['50s']}, Not Outs: {row['Not Outs']}, "
            f"Strike Rate: {sr:.2f}, Batting Average: {avg:.2f}, Favorite Shot: {row['Favorite Shot']}, "
            f"Is Keeper: {row['Is Keeper']}, Team: {row['Team']}, Batting Style: {row['Batting Style']}, "
            f"Bowling Style: {row['Bowling Style']}, Role: {row['Role']}, Overs Bowled: {row['Overs Bowled']}, "
            f"Wickets: {row['Wickets']}, Best Bowling: {row['Best Bowling']}, Economy: {row['Economy']}, "
            f"5W Hauls: {row['5W Hauls']}, Pace: {row['Pace']} km/h\n"
        )
    return context

# ✅ Build and send prompt to Gemini Flash
def query_gemini_flash(context, question):
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    full_prompt = f"""
You are a professional cricket statistics assistant designed to analyze structured player data and respond to natural language queries. Your goal is to provide clear, accurate, and meaningful answers using the statistical information provided below.

You are given a table of player statistics that includes both **batting** and **bowling** performance data. Interpret user queries and map their intent to the appropriate stats below:

---

🔹 BATSMAN DATA FIELD MAPPING:
- **Centuries** → `100s`
- **Half-centuries** → `50s`
- **Balls faced**, **deliveries played** → `Balls Faced`
- **Fours**, **4s** → `4s`
- **Sixes**, **6s** → `6s`
- **Highest score**, **top score** → `Highest Score`
- **Favorite shot**, **preferred shot** → `Favorite Shot`
- **Strike rate** → calculate as `(Runs / Balls Faced) * 100`
- **Batting average** → calculate as `(Runs / Innings)`
- **Consistency** → look at average, 50s, and 100s
- **Finisher** → prioritize `Strike Rate`, `6s`, `Not Outs`
- **Aggressive player** → `Strike Rate`, `6s`, `4s`

---

🔹 BOWLER DATA FIELD MAPPING:
- **Overs bowled** → `Overs Bowled`
- **Wickets taken** → `Wickets`
- **Economy rate** → `Economy`
- **5-wicket hauls** → `5W Hauls`
- **Best bowling figures** → `Best Bowling`
- **Bowling pace**, **fastest bowler** → `Pace` (in km/h)
  - Note: Players with pace close to or above 135 km/h are considered fastest.
  - If user asks for “fastest bowler” or “most pace”, sort by `Pace`.

---

🔹 FIELDING INFO
- **Wicketkeeper** → check `Is Keeper` column
- **Role** → column `Role` (Allrounder, Batsman, etc.)
- **Team**, **Batting/Bowling Style** → mapped directly

---

🔹 SINGLE PLAYER QUERIES:
If the user asks about one player, respond with specific, stat-based information.
> Example: “Moiz has taken 61 wickets with a best of 4/25 and an economy of 6.4.”

---

🔹 MULTI-PLAYER COMPARISONS:
Handle queries like:
- “Top 3 bowlers by wickets”
- “Top 3 highest score”
- “Who has the best economy?”
→ Sort and respond with the top results and a summary (e.g., “Mustufa leads with 90 wickets”).

---

🔹 VAGUE / INDIRECT QUESTIONS:
Infer intelligently:
- “Best finisher?” → `Strike Rate`, `Not Outs`, `6s`
- “Consistent player?” → `Average`, `100s`, `50s`
- “Fastest bowler?” → `Pace`
- “Most dangerous batsman?” → `Strike Rate`, `6s`, `4s`

---

🔹 MULTI-PART QUERIES:
Split and answer each part of the query clearly in a single response.
> “What’s Huzaifa’s strike rate and how many wickets did he take?”

---

🔹 MISSING DATA:
If data is missing for any stat:
> "Sorry, the data for this specific metric is not available for Ahmed."

---

🔹 RESPONSE STYLE:
Answer clearly in a helpful, professional tone.
- Always include player names, stat values, and insights.
- Use line breaks or bullets for clarity when listing multiple players.

---

Now use the data below to answer the user’s question:

DATA:
{context}

Question:
{question}

Answer:
"""
    response = model.generate_content(full_prompt)
    return response.text.strip()
