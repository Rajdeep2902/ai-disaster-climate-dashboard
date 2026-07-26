"""
chatbot_groq.py
----------------
Ye module Groq API (free & fast LLM inference) use karke ek chatbot banata hai
jo:
1. User ke plain-English/Hindi sawaal ko samajhta hai
2. Uss sawaal ka jawab dataset (pandas DataFrame) ke summary stats ke basis pe deta hai
3. Agar chart banana zaroori ho, to plotly chart bhi generate karta hai

Approach: Hum poora dataset LLM ko nahi bhejte (bahut bada ho sakta hai aur costly).
Iske bajaye hum dataset ka "summary" (jaise counts, top categories, date range)
LLM ko context ke roop mein dete hain, aur LLM sirf us summary ke basis pe
insights/answers deta hai. Chart banane ke liye hum khud pandas/plotly se
data prepare karte hain based on keywords jo user ne pucha.
"""

import os
import pandas as pd
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Groq ke free tier pe available fast model. Agar ye deprecated ho jaye
# to Groq console (console.groq.com) pe available models check kar lena.
MODEL_NAME = "llama-3.3-70b-versatile"


def build_dataset_summary(df: pd.DataFrame) -> str:
    """
    Dataset ka ek text summary banata hai jo LLM ko context ke roop mein
    diya jayega. Poora raw data bhejne ke bajaye sirf ye "high-level facts"
    bhejna zyada efficient aur accurate hota hai.
    """
    summary_lines = []
    summary_lines.append(f"Total records: {len(df)}")

    if "data_type" in df.columns:
        counts = df["data_type"].value_counts().to_dict()
        summary_lines.append(f"Records by type: {counts}")

    if "event_date" in df.columns:
        valid_dates = pd.to_datetime(df["event_date"], errors="coerce").dropna()
        if len(valid_dates) > 0:
            summary_lines.append(
                f"Date range: {valid_dates.min().date()} to {valid_dates.max().date()}"
            )

    if "details" in df.columns:
        # Sample kuch rows dikhado taaki LLM ko context mile ki data kaisa dikhta hai
        sample = df["details"].dropna().sample(min(5, len(df))).tolist()
        summary_lines.append(f"Sample records: {sample}")

    return "\n".join(summary_lines)

def find_relevant_rows(user_question: str, df: pd.DataFrame, max_rows: int = 15) -> str:
    """
    User ke sawaal mein agar koi specific city, disaster type, ya keyword ho,
    to dataset ke 'details' column mein usse match karne wali actual rows dhoondta hai.
    """
    if "details" not in df.columns:
        return "No specific row-level data available."

    question_lower = user_question.lower()
    stopwords = {"the", "is", "what", "how", "many", "show", "me", "of", "a", "an",
                 "in", "on", "for", "to", "and", "kya", "hai", "kaun", "kitna"}
    keywords = [w for w in question_lower.replace("?", "").split() if w not in stopwords and len(w) > 2]

    if not keywords:
        return "No specific keywords found in question."

    mask = df["details"].str.lower().apply(
        lambda text: any(kw in str(text) for kw in keywords)
    )
    matched = df[mask].head(max_rows)

    if matched.empty:
        return "No matching rows found for this question."

    return "\n".join(matched["details"].astype(str).tolist())

def ask_chatbot(user_question: str, df: pd.DataFrame) -> str:
    """
    User ka sawaal + dataset summary Groq LLM ko bhejta hai, aur plain text
    jawab return karta hai.
    """
    dataset_summary = build_dataset_summary(df)
    relevant_rows = find_relevant_rows(user_question, df)
    system_prompt = (
        "Tum ek data analytics assistant ho jo global disaster, weather aur "
        "air quality data ke baare mein sawaalon ka jawab deta hai. "
        "Neeche diye gaye dataset summary ke basis pe hi jawab do. "
        "Agar summary mein jawab nahi mil raha, to saaf bata do ki data available nahi hai. "
        "Jawab short, clear aur simple English/Hinglish mein do."
    )

    user_prompt = (
        f"Dataset summary:\n{dataset_summary}\n\n"
        f"Relevant matching records (agar koi mile):\n{relevant_rows}\n\n"
        f"User question: {user_question}"
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,  # Kam temperature = zyada factual, kam "creative" jawab
        max_tokens=500,
    )

    return response.choices[0].message.content


def generate_chart(user_question: str, df: pd.DataFrame):
    """
    Simple keyword-matching se decide karta hai ki kaunsa chart banana hai.
    (Beginner ke liye ye approach LLM se dynamic code generate karwane se
    zyada safe hai — LLM-generated code run karna risky ho sakta hai.)

    Returns: plotly figure object, ya None agar koi matching chart na mile.
    """
    question_lower = user_question.lower()

    if "data_type" not in df.columns:
        return None

    # Example 1: "disaster type" / "category" se related sawaal
    if "type" in question_lower or "category" in question_lower or "count" in question_lower:
        counts = df["data_type"].value_counts().reset_index()
        counts.columns = ["data_type", "count"]
        fig = px.bar(counts, x="data_type", y="count",
                     title="Record Count by Data Type",
                     labels={"data_type": "Data Type", "count": "Number of Records"})
        return fig

    # Example 2: "trend" / "over time" se related sawaal
    if "trend" in question_lower or "time" in question_lower or "date" in question_lower:
        df_copy = df.copy()
        df_copy["event_date"] = pd.to_datetime(df_copy["event_date"], errors="coerce")
        df_copy = df_copy.dropna(subset=["event_date"])
        if len(df_copy) == 0:
            return None
        daily_counts = df_copy.groupby(df_copy["event_date"].dt.date).size().reset_index()
        daily_counts.columns = ["date", "count"]
        fig = px.line(daily_counts, x="date", y="count",
                      title="Records Over Time")
        return fig

    # Example 3: "map" / "location" se related sawaal
    if "map" in question_lower or "location" in question_lower or "where" in question_lower:
        df_copy = df.dropna(subset=["lat", "lon"])
        if len(df_copy) == 0:
            return None
        fig = px.scatter_geo(df_copy, lat="lat", lon="lon", color="data_type",
                             title="Geographic Distribution of Records",
                             hover_name="details")
        return fig

    return None  # Koi matching keyword nahi mila, to sirf text jawab milega
