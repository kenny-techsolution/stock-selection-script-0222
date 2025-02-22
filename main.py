import pandas as pd
import numpy as np
import yfinance as yf

# Define stock list (Update this later with dynamically selected stocks)
stock_symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]

# Define function to fetch stock data
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    
    return {
        "Symbol": symbol,
        "Market Cap": info.get("marketCap", np.nan),
        "PE Ratio": info.get("trailingPE", np.nan),
        "PB Ratio": info.get("priceToBook", np.nan),
        "ROE": info.get("returnOnEquity", np.nan),
        "Net Profit Margin": info.get("profitMargins", np.nan),
        "Revenue Growth": info.get("revenueGrowth", np.nan),
        "EPS Growth": info.get("earningsGrowth", np.nan),
        "Debt-to-Equity": info.get("debtToEquity", np.nan),
        "Free Cash Flow": info.get("freeCashflow", np.nan),
        "50-Day MA": info.get("fiftyDayAverage", np.nan),
        "200-Day MA": info.get("twoHundredDayAverage", np.nan),
    }

# Fetch data for selected stocks
stock_data = [get_stock_data(symbol) for symbol in stock_symbols]

# Convert to DataFrame
df = pd.DataFrame(stock_data)

# Normalize Scores
df["Valuation Score"] = (1 / df["PE Ratio"]) + (1 / df["PB Ratio"])
df["Profitability Score"] = df["ROE"] + df["Net Profit Margin"]
df["Growth Score"] = df["Revenue Growth"] + df["EPS Growth"]
df["Momentum Score"] = np.where(df["50-Day MA"] > df["200-Day MA"], 1, 0)

# Final Investment Score
df["Final Score"] = (
    0.3 * df["Valuation Score"] +
    0.25 * df["Profitability Score"] +
    0.25 * df["Growth Score"] +
    0.2 * df["Momentum Score"]
)

# Sort stocks by highest Final Score
df = df.sort_values(by="Final Score", ascending=False)

# Display Results
print(df)