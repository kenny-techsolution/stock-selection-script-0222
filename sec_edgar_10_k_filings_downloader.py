from sec_edgar_downloader import Downloader

# Initialize the downloader with required arguments
dl = Downloader(company_name="MyInvestmentTool", email_address="kennychung.techsolution@gmail.com")

# Fetch 10-K filings for AAPL (this downloads the latest available filings)
dl.get("10-K", "AAPL")