import requests
from bs4 import BeautifulSoup
import numpy as np


from data_fetch_backup import (
    get_profit_loss_df,
    get_cashflow_df,
    get_balance_sheet_df,
    get_shareholding_pattern,
    build_summary_input,
    get_peer_companies
)

def get_all_financial_data(ticker: str):
    return {
        "ticker": ticker,
        "pnl": get_profit_loss_df(ticker),
        "cashflow": get_cashflow_df(ticker),
        "balance_sheet": get_balance_sheet_df(ticker),
        "shareholding": get_shareholding_pattern(ticker),
    }



def summarize(data):
    return build_summary_input(
        data["pnl"], data["cashflow"], data["balance_sheet"], data["shareholding"]
    )

def run_peer_comparison(ticker: str, client):
    target_data = get_all_financial_data(ticker)
    peer_tickers = get_peer_companies(ticker)

    peer_data_list = []
    for peer in peer_tickers:
        try:
            peer_data = get_all_financial_data(peer)
            peer_data_list.append(peer_data)
        except Exception as e:
            print(f"Skipping {peer} due to error: {e}")
    
    peer_summaries = "\n\n".join([f"{p['ticker']}:\n{summarize(p)}" for p in peer_data_list])

    comparison_prompt = f"""
You are a financial analyst AI.

Compare the financial health and metrics of the target company with its peers.

Target: {ticker}
Peers: {', '.join([p['ticker'] for p in peer_data_list])}

🔹 Target Company Financials:
{summarize(target_data)}

🔸 Peer Company Financials:
{peer_summaries}

Give:
- Relative strengths and weaknesses
- Performance highlights
- Final peer comparison verdict
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial comparison analyst AI."},
            {"role": "user", "content": comparison_prompt}
        ]
    )

    return response.choices[0].message.content









from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
import pandas as pd
from typing import List

from data_fetch_backup import (
    get_profit_loss_df,
    get_cashflow_df,
    get_balance_sheet_df,
    get_shareholding_pattern
)

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key)


def get_peer_companies_via_gpt_lc(ticker: str) -> List[str]:
    system_prompt = "You are a stock market assistant. Only return peer company names."

    user_prompt = f"""You are a financial analyst AI.

Your task is to find 3 to 5 **publicly listed Indian companies** that are **direct business competitors** or operate in the **same sector or product category** as the company given below.

Strict rules:
- Only include companies listed on NSE or BSE.
- Do NOT include conglomerates or unrelated businesses.
- Focus on **product overlap**, **customer segment**, or **business model similarity**.
- Do NOT include indices (like NIFTY), generic codes (like 500112), or unrelated firms.
- Do NOT repeat the target company itself.

Return only peer names or ticker symbols as a comma-separated list, no extra text.

Example  
Input Company: TITAN  
Output: TBZ, Kalyan Jewellers, PC Jeweller, Senco Gold

Input Company: {ticker}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm(messages)
    peers_text = response.content.strip()
    return [peer.strip() for peer in peers_text.split(",") if peer.strip()]


def build_summary_input(pl_df, cf_df, bs_df, sh_df) -> str:
    def _get_row(df, regex):
        match = df[df["Line Item"].str.contains(regex, case=False, na=False)]
        return match.iloc[0] if not match.empty else pd.Series(["N/A"] * len(df.columns), index=df.columns)

    def _get_latest(df, regex):
        row = _get_row(df, regex)
        return row.iloc[-1] if isinstance(row, pd.Series) else "N/A"

    def _to_num(x):
        try:
            return float(str(x).split()[0].replace(",", ""))
        except:
            return float("nan")

    total_assets = _get_latest(bs_df, r"Total Assets")
    borrowings = _get_latest(bs_df, r"Borrowings")
    cash_equiv = _get_latest(bs_df, r"Cash")
    curr_assets = _get_latest(bs_df, r"Current Assets")
    curr_liab = _get_latest(bs_df, r"Current Liabilities")
    current_ratio = round(_to_num(curr_assets) / _to_num(curr_liab), 2) if pd.notna(_to_num(curr_assets)) and pd.notna(_to_num(curr_liab)) else "N/A"

    try:
        promoter_row = sh_df[sh_df.columns[0]].str.lower().str.contains("promoter")
        promoter_holding = sh_df.loc[promoter_row].iloc[0, -1] if promoter_row.any() else "N/A"
    except:
        promoter_holding = "N/A"

    try:
        fii_row = sh_df[sh_df.columns[0]].str.lower().str.contains("fii")
        fii_holding = sh_df.loc[fii_row].iloc[0, -1] if fii_row.any() else "N/A"
    except:
        fii_holding = "N/A"

    sales_row = _get_row(pl_df, r"Sales")
    net_profit_row = _get_row(pl_df, r"Net Profit")
    cfo_row = _get_row(cf_df, r"Cash from Operating|Cash Flow from Ops")

    def last_n_years(row, n=5):
        try:
            return row[-n:].tolist()
        except:
            return ["N/A"] * n

    return f"""
📈 Profit & Loss (last 5 years):
- Sales: {last_n_years(sales_row)}
- Net Profit: {last_n_years(net_profit_row)}

💸 Cash Flow (last 5 years):
- CFO: {last_n_years(cfo_row)}
- Net Profit vs CFO Divergence: check if pattern diverges

🧮 Balance Sheet (latest year only):
- Total Assets: {total_assets}
- Borrowings: {borrowings}
- Cash & Equivalents: {cash_equiv}
- Current Ratio (CA / CL): {current_ratio}

🧾 Shareholding Pattern (latest):
- Promoter Holding: {promoter_holding}
- FII Holding: {fii_holding}
"""


def get_all_financial_data(ticker: str):
    return {
        "ticker": ticker,
        "pnl": get_profit_loss_df(ticker),
        "cashflow": get_cashflow_df(ticker),
        "balance_sheet": get_balance_sheet_df(ticker),
        "shareholding": get_shareholding_pattern(ticker),
    }


def summarize(data):
    return build_summary_input(
        data["pnl"], data["cashflow"], data["balance_sheet"], data["shareholding"]
    )


def run_peer_comparison(ticker: str):
    target_data = get_all_financial_data(ticker)
    peer_tickers = get_peer_companies_via_gpt_lc(ticker)

    peer_data_list = []
    for peer in peer_tickers:
        try:
            print(f"🔄 Fetching data for peer: {peer}")
            peer_data = get_all_financial_data(peer)
            peer_data_list.append(peer_data)
        except Exception as e:
            print(f"❌ Skipping {peer} due to error: {e}")

    peer_summaries = "\n\n".join([f"{p['ticker']}:\n{summarize(p)}" for p in peer_data_list])

    comparison_prompt = f"""
You are a financial comparison analyst AI.

Compare the financial health of the target company with its industry peers. Analyze each across profitability, cash flow quality, balance sheet strength, and promoter confidence.

Target: {ticker}
Peers: {', '.join([p['ticker'] for p in peer_data_list])}

🔹 Target Company Financials:
{summarize(target_data)}

🔸 Peer Company Financials:
{peer_summaries}

Return the following:
1. 📊 Strength and weakness comparison
2. 📈 Highlight which company has best profitability, CFO trend, leverage, and promoter confidence
3. ✅ Score each company out of 100
4. 🏆 Final verdict: Best positioned peer
"""

    response = llm([
        SystemMessage(content="You are a financial comparison analyst AI."),
        HumanMessage(content=comparison_prompt)
    ])

    return response.content


# Example usage:
# print(run_peer_comparison("ITC"))

