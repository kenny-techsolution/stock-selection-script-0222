# Extract numbers associated with keywords like "Operating Activities" and "Capital Expenditures" using refined regex
operating_cash_flow_pattern = re.compile(
    r"Net cash provided by operating activities[\s\S]*?\$?\(?([0-9,]+)\)?", re.IGNORECASE
)
capital_expenditures_pattern = re.compile(
    r"Capital expenditures[\s\S]*?\$?\(?([0-9,]+)\)?|Purchases of property, plant and equipment[\s\S]*?\$?\(?([0-9,]+)\)?",
    re.IGNORECASE,
)

# Extract values from the text
operating_cash_flow_match = operating_cash_flow_pattern.search(cash_flow_section) if cash_flow_section else None
capital_expenditures_match = capital_expenditures_pattern.search(cash_flow_section) if cash_flow_section else None

# Extract numbers from matched patterns
def extract_value(match):
    if match:
        for group in match.groups():
            if group:
                return int(group.replace(",", ""))
    return None

operating_cash_flow = extract_value(operating_cash_flow_match)
capital_expenditures = extract_value(capital_expenditures_match)

# Compute Free Cash Flow (FCF)
if operating_cash_flow is not None and capital_expenditures is not None:
    free_cash_flow = operating_cash_flow - capital_expenditures
else:
    free_cash_flow = None

# Display extracted values
{
    "Operating Cash Flow": operating_cash_flow if operating_cash_flow else "Not Found",
    "Capital Expenditures": capital_expenditures if capital_expenditures else "Not Found",
    "Free Cash Flow (FCF)": free_cash_flow if free_cash_flow is not None else "Not Found",
}