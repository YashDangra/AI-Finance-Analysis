

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

# def build_summary_input(pl_df, cf_df, bs_df, sh_df) -> str:
#     def _get_row(df, regex):
#         match = df[df["Line Item"].str.contains(regex, case=False, na=False)]
#         if not match.empty:
#             return match.iloc[0]
#         return pd.Series(["N/A"] * len(df.columns), index=df.columns)

#     def _get_latest(df, regex):
#         row = _get_row(df, regex)
#         return row.iloc[-1] if isinstance(row, pd.Series) else "N/A"

#     def _to_num(x):
#         try:
#             return float(str(x).split()[0].replace(",", ""))
#         except:
#             return np.nan

#     # Balance Sheet
#     total_assets = _get_latest(bs_df, r"Total Assets")
#     borrowings = _get_latest(bs_df, r"Borrowings")
#     cash_equiv = _get_latest(bs_df, r"Cash")
#     curr_assets = _get_latest(bs_df, r"Current Assets")
#     curr_liab = _get_latest(bs_df, r"Current Liabilities")
#     current_ratio = round(_to_num(curr_assets) / _to_num(curr_liab), 2) if all(map(np.isfinite, [_to_num(curr_assets), _to_num(curr_liab)])) else "N/A"

#     # Shareholding
#     try:
#         promoter_row = sh_df[sh_df.columns[0]].str.lower().str.contains("promoter")
#         promoter_holding = sh_df.loc[promoter_row].iloc[0, -1] if promoter_row.any() else "N/A"
#     except:
#         promoter_holding = "N/A"

#     try:
#         fii_row = sh_df[sh_df.columns[0]].str.lower().str.contains("fii")
#         fii_holding = sh_df.loc[fii_row].iloc[0, -1] if fii_row.any() else "N/A"
#     except:
#         fii_holding = "N/A"

#     # P&L and Cash Flow
#     sales_row = _get_row(pl_df, r"Sales")
#     net_profit_row = _get_row(pl_df, r"Net Profit")
#     cfo_row = _get_row(cf_df, r"Cash from Operating|Cash Flow from Ops")

#     def last_n_years(row, n=5):
#         try:
#             return row[-n:].tolist()
#         except:
#             return ["N/A"] * n

#     return f"""
# 📈 Profit & Loss (last 5 years):
# - Sales: {last_n_years(sales_row)}
# - Net Profit: {last_n_years(net_profit_row)}

# 💸 Cash Flow (last 5 years):
# - CFO: {last_n_years(cfo_row)}
# - Net Profit vs CFO Divergence: check if pattern diverges

# 🧮 Balance Sheet (latest year only):
# - Total Assets: {total_assets}
# - Borrowings: {borrowings}
# - Cash & Equivalents: {cash_equiv}
# - Current Ratio (CA / CL): {current_ratio}

# 🧾 Shareholding Pattern (latest):
# - Promoter Holding: {promoter_holding}
# - FII Holding: {fii_holding}
# """

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

