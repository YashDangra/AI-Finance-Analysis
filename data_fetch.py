import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np


def get_profit_loss_df(ticker: str) -> pd.DataFrame:
    print(f"📥 Fetching Profit & Loss data for {ticker}...")
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
        table = soup.find("section", id="profit-loss").find("table")
        if not table:
            raise ValueError("Profit & Loss table not found on page.")
        headers = [th.text.strip() for th in table.select("thead tr th")]
        rows = [[td.text.strip() for td in row.find_all("td")] for row in table.select("tbody tr")]
        df = pd.DataFrame(rows, columns=headers)
        if "Line Item" not in df.columns:
            df.columns = ["Line Item"] + list(df.columns[1:])
        print("✅ Profit & Loss data fetched successfully.")
        return df
    except Exception as e:
        print(f"❌ Error fetching P&L: {e}")
        return pd.DataFrame(columns=["Line Item"])

def get_cashflow_df(ticker: str) -> pd.DataFrame:
    print(f"📥 Fetching Cash Flow data for {ticker}...")
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
        table = soup.find("section", id="cash-flow").find("table")
        if not table:
            raise ValueError("Cash Flow table not found on page.")
        headers = [th.text.strip() for th in table.select("thead tr th")]
        rows = [[td.text.strip() for td in row.find_all("td")] for row in table.select("tbody tr")]
        df = pd.DataFrame(rows, columns=headers)
        if "Line Item" not in df.columns:
            df.columns = ["Line Item"] + list(df.columns[1:])
        print("✅ Cash Flow data fetched successfully.")
        return df
    except Exception as e:
        print(f"❌ Error fetching Cash Flow: {e}")
        return pd.DataFrame(columns=["Line Item"])

def get_balance_sheet_df(ticker: str) -> pd.DataFrame:
    print(f"📥 Fetching Balance Sheet data for {ticker}...")
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
        table = soup.find("section", id="balance-sheet").find("table")
        if not table:
            raise ValueError("Balance Sheet table not found on page.")
        headers = [th.text.strip() for th in table.select("thead tr th")]
        rows = [[td.text.strip() for td in row.find_all("td")] for row in table.select("tbody tr")]
        df = pd.DataFrame(rows, columns=headers)
        if "Line Item" not in df.columns:
            df.columns = ["Line Item"] + list(df.columns[1:])
        print("✅ Balance Sheet data fetched successfully.")
        return df
    except Exception as e:
        print(f"❌ Error fetching Balance Sheet: {e}")
        return pd.DataFrame(columns=["Line Item"])

def get_shareholding_pattern(ticker: str) -> pd.DataFrame:
    print(f"📥 Fetching Shareholding Pattern data for {ticker}...")
    url = f"https://www.screener.in/company/{ticker}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        soup = BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
        table = soup.find("section", id="shareholding").find("table")
        if not table:
            raise ValueError("Shareholding table not found on page.")
        headers = [th.text.strip() for th in table.select("thead tr th")]
        rows = [[td.text.strip() for td in row.find_all("td")] for row in table.select("tbody tr")]
        df = pd.DataFrame(rows, columns=headers)
        if "Category" not in df.columns:
            df.columns = ["Category"] + list(df.columns[1:])
        print("✅ Shareholding data fetched successfully.")
        return df
    except Exception as e:
        print(f"❌ Error fetching Shareholding Pattern: {e}")
        return pd.DataFrame(columns=["Category"])

# def build_summary_input(pl_df, cf_df, bs_df, sh_df) -> str:
#     def _get_row(df, regex):
#         if "Line Item" not in df.columns:
#             return pd.Series(["N/A"] * 10)
#         match = df[df["Line Item"].str.contains(regex, case=False, na=False)]
#         if not match.empty:
#             return match.iloc[0]
#         return pd.Series(["N/A"] * len(df.columns))

#     def _get_latest(df, regex):
#         row = _get_row(df, regex)
#         return row.iloc[-1] if isinstance(row, pd.Series) else "N/A"

#     def _to_num(x):
#         try:
#             return float(str(x).split()[0].replace(",", ""))
#         except:
#             return float("nan")

#     total_assets = _get_latest(bs_df, r"Total Assets")
#     borrowings = _get_latest(bs_df, r"Borrowings")
#     cash_equiv = _get_latest(bs_df, r"Cash")
#     curr_assets = _get_latest(bs_df, r"Current Assets")
#     curr_liab = _get_latest(bs_df, r"Current Liabilities")
#     current_ratio = round(_to_num(curr_assets) / _to_num(curr_liab), 2) if all(map(pd.notnull, [_to_num(curr_assets), _to_num(curr_liab)])) else "N/A"

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

#     sales_row = _get_row(pl_df, r"Sales")
#     net_profit_row = _get_row(pl_df, r"Net Profit")
#     cfo_row = _get_row(cf_df, r"Cash from Operating|Cash Flow from Ops")

#     def last_n_years(row, n=5):
#         try:
#             return row[-n:].tolist()
#         except:
#             return ["N/A"] * n

#     return f'''
# Profit & Loss (last 5 years):
# - Sales: {last_n_years(sales_row)}
# - Net Profit: {last_n_years(net_profit_row)}

# Cash Flow (last 5 years):
# - CFO: {last_n_years(cfo_row)}
# - Net Profit vs CFO Divergence: check if pattern diverges

# Balance Sheet (latest year only):
# - Total Assets: {total_assets}
# - Borrowings: {borrowings}
# - Cash & Equivalents: {cash_equiv}
# - Current Ratio (CA / CL): {current_ratio}

# Shareholding Pattern (latest):
# - Promoter Holding: {promoter_holding}
# - FII Holding: {fii_holding}
# '''

def build_summary_input(pl_df, cf_df, bs_df, sh_df) -> str:
    def _get_row(df, regex):
        if "Line Item" not in df.columns:
            return pd.Series(["N/A (missing)"] * 10)
        match = df[df["Line Item"].str.contains(regex, case=False, na=False)]
        if not match.empty:
            return match.iloc[0]
        return pd.Series(["N/A (missing)"] * len(df.columns))

    def _get_latest(df, regex):
        row = _get_row(df, regex)
        return row.iloc[-1] if isinstance(row, pd.Series) and not row.empty else "N/A (missing)"

    def _to_num(x):
        try:
            return float(str(x).split()[0].replace(",", ""))
        except:
            return float("nan")

    # Balance Sheet values
    total_assets = _get_latest(bs_df, r"Total Assets")
    borrowings = _get_latest(bs_df, r"Borrowings")
    cash_equiv = _get_latest(bs_df, r"Cash")
    curr_assets = _get_latest(bs_df, r"Current Assets")
    curr_liab = _get_latest(bs_df, r"Current Liabilities")

    current_ratio = (
        round(_to_num(curr_assets) / _to_num(curr_liab), 2)
        if all(map(pd.notnull, [_to_num(curr_assets), _to_num(curr_liab)]))
        else "N/A (missing)"
    )

    # Shareholding
    try:
        promoter_row = sh_df[sh_df.columns[0]].str.lower().str.contains("promoter")
        promoter_holding = sh_df.loc[promoter_row].iloc[0, -1] if promoter_row.any() else "N/A (missing)"
    except:
        promoter_holding = "N/A (missing)"

    try:
        fii_row = sh_df[sh_df.columns[0]].str.lower().str.contains("fii")
        fii_holding = sh_df.loc[fii_row].iloc[0, -1] if fii_row.any() else "N/A (missing)"
    except:
        fii_holding = "N/A (missing)"

    # P&L and Cash Flow
    sales_row = _get_row(pl_df, r"Sales")
    net_profit_row = _get_row(pl_df, r"Net Profit")
    cfo_row = _get_row(cf_df, r"Cash from Operating|Cash Flow from Ops")

    def last_n_years(row, n=5):
        try:
            return [x if x else "N/A (missing)" for x in row[-n:].tolist()]
        except:
            return ["N/A (missing)"] * n

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

