


from langchain.agents import Tool
from Fundamental_analysis import run_fundamental_analysis
from forensic_audit import run_forensic_analysis
from dotenv import load_dotenv
import os
import numpy as np


from langchain.chat_models import ChatOpenAI  # ✅ Use LangChain's model

# ✅ Load env and fetch API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Instantiate LangChain-compatible OpenAI model
client = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)


def get_tools(client):
    return [
        Tool(
            name="Fundamental Analysis",
            func=lambda ticker: run_fundamental_analysis(ticker, client),
            description="Analyzes the company's financials: profit & loss, balance sheet, cash flow, and shareholding pattern. Use this for financial analysis of the company"
        ),
        Tool(
            name="Forensic Audit",
            func=lambda ticker: run_forensic_analysis(ticker, client),
            description="Performs forensic accounting analysis to detect red flags, fraud, or financial manipulation. Use it only to find the red flags and forensic analysis of the company."
        )
    ]
