import streamlit as st
from Fundamental_analysis import run_fundamental_analysis #as fundamental_analysis
from forensic_audit import run_forensic_analysis
from react_agent import run_react_agent 
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
import numpy as np


# Load API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Instantiate LangChain-compatible OpenAI model
client = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)

# Streamlit UI
st.set_page_config(page_title="Company Financial Analysis", layout="centered")
st.title("📊 Fundamental Financial Analysis with AI")


st.title("🧠 ReAct Financial Agent")

ticker = st.text_input("Enter Company Ticker (e.g., TCS, GPIL)", value="GPIL")
query = st.text_area("Enter your query", value="Check for red flags and financial health.")

# Trigger agent
if st.button("Run ReAct Agent"):
    with st.spinner("Thinking..."):
        try:
            result = run_react_agent(ticker, query, openai_api_key)

            st.subheader("📋 Final Answer")
            st.markdown(result["output"])

            st.subheader("🔍 ReAct Agent Trace")
            for action, observation in result.get("intermediate_steps", []):
                st.markdown(f"🛠️ **Tool Used**: `{action.tool}`")
                st.markdown(f"🧾 **Tool Input**: `{action.tool_input}`")
                st.markdown(f"📤 **Tool Output**:\n```\n{observation}\n```")
                st.markdown("---")

        except Exception as e:
            st.error(f"❌ Agent failed: {e}")

