import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from alpha_vantage.fundamentaldata import FundamentalData

# Define the stock symbol
stock_symbol = "KO"  # Change to any stock

# Define discount rate and perpetual growth rate for DCF model
discount_rate = 0.10  # 10% discount rate
perpetual_growth_rate = 0.03  # 3% growth rate

# Initialize Alpha Vantage API
api_key = "ZFIL5I66WE2QMN1T"
fd = FundamentalData(api_key, output_format="pandas")

# Fetch Free Cash Flow data from Alpha Vantage
fcf_data, _ = fd.get_cash_flow_annual(symbol=stock_symbol)

# Convert to numeric values
fcf_data["operatingCashflow"] = pd.to_numeric(fcf_data["operatingCashflow"], errors="coerce")
fcf_data["capitalExpenditures"] = pd.to_numeric(fcf_data["capitalExpenditures"], errors="coerce")

# Compute Free Cash Flow (FCF)
fcf_data["Free Cash Flow"] = fcf_data["operatingCashflow"] - fcf_data["capitalExpenditures"]

# Convert fiscalDateEnding to a proper datetime format
fcf_data["fiscalDateEnding"] = pd.to_datetime(fcf_data["fiscalDateEnding"])
fcf_data = fcf_data[["fiscalDateEnding", "Free Cash Flow"]]

# Set fiscalDateEnding as the index
fcf_data.set_index("fiscalDateEnding", inplace=True)

# Reverse order (oldest to newest) for proper DCF calculations
fcf_data = fcf_data.sort_index()

# Get Shares Outstanding from Yahoo Finance
stock = yf.Ticker(stock_symbol)
try:
    shares_outstanding = stock.info.get("sharesOutstanding", np.nan)
    if np.isnan(shares_outstanding):
        raise ValueError("Shares Outstanding data unavailable")
except Exception as e:
    print(f"Error fetching Shares Outstanding: {e}")
    shares_outstanding = np.nan

# If data is missing, print a warning and exit
if fcf_data.empty or np.isnan(shares_outstanding):
    print("Error: Free Cash Flow or Shares Outstanding data unavailable for this stock. Try a different stock.")
    exit()

# Convert to DataFrame for processing
df = fcf_data.reset_index()
df["Year"] = df["fiscalDateEnding"].dt.year
df["Shares Outstanding"] = shares_outstanding

# Function to calculate intrinsic value for a given year
def calculate_intrinsic_value(fcf, shares_outstanding):
    if np.isnan(fcf) or np.isnan(shares_outstanding):
        return np.nan

    # Project Free Cash Flow for 5 years using a 10% growth rate
    years = 5
    fcf_projections = [fcf * (1.10 ** t) for t in range(1, years + 1)]

    # Discount projected FCFs to present value
    discounted_fcf = [fcf_t / ((1 + discount_rate) ** t) for t, fcf_t in enumerate(fcf_projections, 1)]

    # Calculate Terminal Value using perpetual growth model
    terminal_value = (fcf_projections[-1] * (1 + perpetual_growth_rate)) / (discount_rate - perpetual_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)

    # Sum of discounted FCFs + discounted terminal value
    total_intrinsic_value = sum(discounted_fcf) + discounted_terminal_value

    # Intrinsic value per share
    intrinsic_value_per_share = total_intrinsic_value / shares_outstanding

    return intrinsic_value_per_share

# Calculate intrinsic value for each year
df["Intrinsic Value"] = df.apply(lambda row: calculate_intrinsic_value(row["Free Cash Flow"], row["Shares Outstanding"]), axis=1)

# Fetch historical stock prices from Yahoo Finance
try:
    historical_prices = stock.history(period="20y", interval="1mo")["Close"]

    # Convert index to a DateTime object and extract the year
    historical_prices.index = pd.to_datetime(historical_prices.index)
    historical_prices = historical_prices.resample("Y").last()  # Get last available price per year
    historical_prices.index = historical_prices.index.year  # Convert index to just years

    # Filter stock prices to match financial report years
    df = df[df["Year"].isin(historical_prices.index)]

    # Match stock prices with available years
    df["Stock Price"] = df["Year"].map(historical_prices.to_dict())

except Exception as e:
    print(f"Error fetching stock prices: {e}")
    df["Stock Price"] = np.nan

# Plot intrinsic value vs. actual stock price
plt.figure(figsize=(12, 6))
plt.plot(df["Year"], df["Intrinsic Value"], label="Intrinsic Value", marker="o")
plt.plot(df["Year"], df["Stock Price"], label="Stock Price", marker="s", linestyle="dashed")
plt.xlabel("Year")
plt.ylabel("Price (USD)")
plt.title(f"Intrinsic Value vs. Stock Price for {stock_symbol} (20 Years)")
plt.legend()
plt.grid(True)
plt.show()

# Display results
print(df)