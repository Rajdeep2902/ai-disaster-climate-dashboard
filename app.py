"""
app.py
------
Ye Streamlit app hai jo hamare pura project ko ek simple web interface mein
dikhata hai:
1. Cleaned dataset ka preview
2. Chat interface jahan user natural language mein sawaal pooch sakta hai
3. Groq LLM se text jawab + relevant chart (agar applicable ho)

Chalane ka tarika (terminal mein):
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import os
import sys

# src/ folder ko path mein add karo taaki hum apne modules import kar sakein
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from chatbot_groq import ask_chatbot, generate_chart  # noqa: E402

st.set_page_config(page_title="AI Disaster & Climate Risk Dashboard", layout="wide")

st.title("🌍 AI-Powered Global Disaster & Climate Risk Analytics Dashboard")
st.caption("Real-time disaster, weather & air quality data + AI chatbot (Groq LLM)")

# ---------------------------------------------------------------------------
# Step 1: Cleaned dataset load karo
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "processed", "master_dataset.csv")

if not os.path.exists(DATA_PATH):
    st.error(
        "⚠️ master_dataset.csv nahi mili! Pehle 'python src/data_collection.py' "
        "aur phir 'python src/data_cleaning.py' chala lo."
    )
    st.stop()

df = pd.read_csv(DATA_PATH)

# ---------------------------------------------------------------------------
# Step 2: Dataset ka quick preview aur basic stats sidebar mein dikhao
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📊 Dataset Overview")
    st.metric("Total Records", len(df))
    if "data_type" in df.columns:
        st.write(df["data_type"].value_counts())

st.subheader("📄 Dataset Preview")
st.dataframe(df.head(20), use_container_width=True)

# ---------------------------------------------------------------------------
# Step 3: Chat interface
# ---------------------------------------------------------------------------
st.subheader("💬 Ask the AI Assistant")

# Chat history ko session state mein rakho taaki page refresh pe na ude
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_question = st.chat_input("Apna sawaal yahan likho (e.g. 'Show disaster count by type')")

if user_question:
    # LLM se text jawab lo
    with st.spinner("Sochi raha hoon..."):
        answer = ask_chatbot(user_question, df)
        chart = generate_chart(user_question, df)

    st.session_state.chat_history.append({
        "question": user_question,
        "answer": answer,
        "chart": chart,
    })

# Purana chat history render karo (sabse naya sabse upar)
for entry in reversed(st.session_state.chat_history):
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        if entry["chart"] is not None:
            st.plotly_chart(entry["chart"], use_container_width=True)
