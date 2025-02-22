import pandas as pd
import numpy as np
import yfinance as yf

# Define stock list (you can modify this list)
stock_symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]

# Define discount rate and perpetual growth rate for DCF model
discount_rate = 0.10  # 10% discount rate
perpetual_growth_rate = 0.03  # 3% growth rate

# Function to calculate intrinsic value using DCF model
def calculate_intrinsic_value(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info

    try:
        fcf = info.get("freeCashflow", np.nan)
        shares_outstanding = info.get("sharesOutstanding", np.nan)
        current_price = info.get("currentPrice", np.nan)

        if np.isnan(fcf) or np.isnan(shares_outstanding) or np.isnan(current_price):
            return {"Symbol": symbol, "Intrinsic Value": np.nan, "Current Price": current_price, "Undervalued": np.nan}

        # Project Free Cash Flow for 5 years using a 10% growth rate (assumption)
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

        # Determine if the stock is undervalued
        undervalued = intrinsic_value_per_share > current_price

        return {
            "Symbol": symbol,
            "Intrinsic Value": intrinsic_value_per_share,
            "Current Price": current_price,
            "Undervalued": undervalued
        }

    except Exception as e:
        return {"Symbol": symbol, "Intrinsic Value": np.nan, "Current Price": np.nan, "Undervalued": np.nan}

# Fetch intrinsic value calculations for selected stocks
intrinsic_values = [calculate_intrinsic_value(symbol) for symbol in stock_symbols]

# Convert to DataFrame
df_intrinsic = pd.DataFrame(intrinsic_values)

# Display results
print(df_intrinsic)