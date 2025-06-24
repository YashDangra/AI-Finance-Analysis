

import os
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import numpy as np


from data_fetch import (
    get_profit_loss_df,
    get_balance_sheet_df,
    get_shareholding_pattern,
    get_cashflow_df,
    build_summary_input
)

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# ✅ Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Initialize LangChain-compatible OpenAI model
client = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)



def run_fundamental_analysis(ticker: str, client):
    with st.status("⏳ Fetching financial data...", expanded=True) as status:
        st.write(f"📥 Profit & Loss for {ticker}")
        pl_df = get_profit_loss_df(ticker)

        st.write(f"📥 Cashflow for {ticker}")
        cf_df = get_cashflow_df(ticker)

        st.write(f"📥 Balance Sheet for {ticker}")
        bs_df = get_balance_sheet_df(ticker)

        st.write(f"📥 Shareholding for {ticker}")
        sh_df = get_shareholding_pattern(ticker)

        status.update(label="✅ All data fetched", state="complete")

    missing_data = []
    if pl_df.empty: missing_data.append("Profit & Loss")
    if cf_df.empty: missing_data.append("Cash Flow")
    if bs_df.empty: missing_data.append("Balance Sheet")
    if sh_df.empty: missing_data.append("Shareholding")

    if missing_data:
        st.warning(f"⚠️ Missing data: {', '.join(missing_data)}. Proceeding with available information.")

    
    summary = build_summary_input(pl_df, cf_df, bs_df, sh_df)

    analysis_prompt = f"""
You are a professional financial analyst AI. Your task is to evaluate the fundamental strength and risks of a company based on the provided structured financial data.

Please analyze the following:

1. 💸 **Cash Flow Analysis**  
   - Compare Net Profit and Cash from Operating Activities (CFO) trend.  
   - Flag any major divergence.  
   - Comment on the quality of earnings and cash generation capacity.

2. 📈 **Profit & Loss Trends**  
   - Analyze growth trends in Revenue, EBITDA, and Net Profit.  
   - Highlight any margin compression or operating efficiency trends.  
   - Flag inconsistent or declining growth.

3. 🧮 **Balance Sheet Health**  
   - Comment on debt levels, liquidity, and capital structure.  
   - Look for red flags like negative working capital, rising debt, or excessive goodwill.

4. 🧾 **Shareholding Pattern**  
   - Evaluate promoter holding trend.  
   - Flag any recent reduction in promoter stake or increase in public/FII/DII that could signal confidence or risk.

5. 🔍 **Fraud or Red Flag Indicators**  
   - Based on the above, identify any potential manipulation risk using indicators like:  
     - Declining CFO with rising profits  
     - Rising receivables  
     - Consistent promoter stake reduction  
     - High leverage or pledge risk

6. 📊 **Score & Summary**  
   - Conclude with an overall health score (0–100).  
   - Mention if the company is fundamentally strong, average, or weak.  
   - Summarize the company’s strengths, weaknesses, and investment-worthiness in plain English (3–5 bullet points).

Here is the financial data:
{summary}

If any critical data is missing, please let the user know, that data is missing. Please provide specifics of which data is missing.

"""

    response = client.invoke([
        SystemMessage(content="You are a financial analyst AI."),
        HumanMessage(content=analysis_prompt)
    ])
    print(response.content)
    return response.content

