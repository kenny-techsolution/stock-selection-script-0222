from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd

# Replace with your Alpha Vantage API key
api_key = "ZFIL5I66WE2QMN1T"

# Initialize API
fd = FundamentalData(api_key, output_format="pandas")

# Get Free Cash Flow data
fcf_data, _ = fd.get_cash_flow_annual(symbol="AAPL")

# Convert relevant columns to numeric values
fcf_data["operatingCashflow"] = pd.to_numeric(fcf_data["operatingCashflow"], errors="coerce")
fcf_data["capitalExpenditures"] = pd.to_numeric(fcf_data["capitalExpenditures"], errors="coerce")

# Check if required columns exist before computing Free Cash Flow
if "operatingCashflow" in fcf_data.columns and "capitalExpenditures" in fcf_data.columns:
    fcf_data["Free Cash Flow"] = fcf_data["operatingCashflow"] - fcf_data["capitalExpenditures"]

    # Convert fiscalDateEnding to a proper datetime format
    fcf_data["fiscalDateEnding"] = pd.to_datetime(fcf_data["fiscalDateEnding"])

    # Select only relevant columns
    fcf_data = fcf_data[["fiscalDateEnding", "Free Cash Flow"]]

    # Set fiscalDateEnding as the new index (instead of the default incorrect date)
    fcf_data.set_index("fiscalDateEnding", inplace=True)

    # Display the results
    print(fcf_data)
else:
    print("Error: Required columns not found in API response")