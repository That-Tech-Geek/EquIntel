import streamlit as st
import pandas as pd
import pdfplumber
import re

# Function to load uploaded share price data
def load_share_prices(file):
    return pd.read_csv(file, index_col=0, parse_dates=True)

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(uploaded_statements_pdf):
    text = ""
    try:
        with pdfplumber.open(uploaded_statements_pdf) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text

# Function to find specific financial data in the extracted text with debug information
def find_financial_data_in_text(text, key):
    pattern = re.compile(rf'{key}[\s:]*[\$]?([\d,\.]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        st.write(f"Found {key}: {match.group(1)}")
        return float(match.group(1).replace(',', '').replace('$', ''))
    else:
        # Debug: Show the context around the missing key
        context_pattern = re.compile(rf'.{{0,30}}{key}.{{0,30}}', re.IGNORECASE)
        context_matches = context_pattern.findall(text)
        st.write(f"Could not find {key} in the extracted text. Here are some contexts where it might appear:")
        for context in context_matches:
            st.write(f"...{context}...")
    return None

# Function to get financial data from PDF text
def get_financial_data_from_pdf(pdf_text, keys):
    data = {}
    for key in keys:
        data[key] = find_financial_data_in_text(pdf_text, key)
    return pd.Series(data)

# Functions for calculations (reused from the previous code)
def calculate_moat_indicators(financials):
    net_income = financials.get('Net Income')
    total_assets = financials.get('Total Assets')
    current_liabilities = financials.get('Current Liabilities')
    
    st.write(f"Net Income: {net_income}, Total Assets: {total_assets}, Current Liabilities: {current_liabilities}")
    
    if net_income is not None and total_assets is not None and current_liabilities is not None:
        roic = net_income / (total_assets - current_liabilities)
        return roic
    return None

def analyze_investments(financials):
    net_income = financials.get('Net Income')
    capital_expenditures = financials.get('Capital Expenditures')
    
    st.write(f"Net Income: {net_income}, Capital Expenditures: {capital_expenditures}")
    
    if isinstance(net_income, pd.Series) and isinstance(capital_expenditures, pd.Series):
        performance = net_income.pct_change()
        high_performance = performance > performance.median()
        investments_in_high = capital_expenditures[high_performance].mean()
        investments_in_low = capital_expenditures[~high_performance].mean()
        return investments_in_high, investments_in_low
    return None, None

def assess_growth(financials):
    total_revenue = financials.get('Total Revenue')
    
    st.write(f"Total Revenue: {total_revenue}")
    
    if isinstance(total_revenue, pd.Series) and len(total_revenue) > 1:
        cagr = (total_revenue.iloc[-1] / total_revenue.iloc[0])**(1/len(total_revenue)) - 1
        return cagr
    return None

def define_valuation(financials):
    market_cap = financials.get('Market Cap')
    book_value = financials.get('Book Value')
    shares_outstanding = financials.get('Shares Outstanding')
    
    st.write(f"Market Cap: {market_cap}, Book Value: {book_value}, Shares Outstanding: {shares_outstanding}")
    
    if market_cap is not None and book_value is not None and shares_outstanding is not None:
        intrinsic_value = book_value * shares_outstanding
        return market_cap, intrinsic_value
    return None, None

def find_operating_leverage(financials):
    operating_expenses = financials.get('Operating Expenses')
    cost_of_revenue = financials.get('Cost of Revenue')
    
    st.write(f"Operating Expenses: {operating_expenses}, Cost of Revenue: {cost_of_revenue}")
    
    if isinstance(operating_expenses, pd.Series) and isinstance(cost_of_revenue, pd.Series):
        fixed_costs = operating_expenses.mean()
        variable_costs = cost_of_revenue.mean()
        operating_leverage = fixed_costs / (fixed_costs + variable_costs)
        return operating_leverage
    return None

def conduct_stress_test(financials):
    # Example stress scenarios: need specific financial data to implement
    return "Stress test results based on financial data."

def pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage):
    verdict = "Invest" if roic and roic > 0.1 and stock_returns > industry_average and cagr and cagr > 0.05 and market_cap and market_cap < intrinsic_value and operating_leverage and operating_leverage > 0.5 else "Do Not Invest"
    return verdict

# Streamlit UI
st.title("EquiIntel: Comprehensive Equity Analysis AI")

uploaded_share_prices = st.file_uploader("Upload Share Prices CSV", type="csv")
uploaded_statements_pdf = st.file_uploader("Upload Financial Statements PDF", type="pdf")

if uploaded_share_prices and uploaded_statements_pdf:
    share_prices = load_share_prices(uploaded_share_prices)
    pdf_text = extract_text_from_pdf(uploaded_statements_pdf)
    
    st.write("Extracted Text from PDF:")
    st.write(pdf_text[:2000])  # Display the first 2000 characters for debugging
    
    financial_keys = ['Net Income', 'Total Assets', 'Current Liabilities', 'Capital Expenditures', 'Total Revenue', 'Market Cap', 'Book Value', 'Shares Outstanding', 'Operating Expenses', 'Cost of Revenue']
    financials = get_financial_data_from_pdf(pdf_text, financial_keys)
    
    st.write("Extracted Financial Data:")
    st.write(financials)
    
    roic = calculate_moat_indicators(financials)
    investments_in_high, investments_in_low = analyze_investments(financials)
    stock_returns = share_prices['Close'].pct_change().mean()
    industry_average = 0.05  # Example fixed value; replace with actual industry average
    cagr = assess_growth(financials)
    market_cap, intrinsic_value = define_valuation(financials)
    stress_scenarios = conduct_stress_test(financials)
    operating_leverage = find_operating_leverage(financials)
    verdict = pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage)

    st.write(f"ROIC: {roic}")
    st.write(f"Investments in times of high performance: {investments_in_high}")
    st.write(f"Investments in times of low performance: {investments_in_low}")
    st.write(f"Stock returns: {stock_returns}")
    st.write(f"Industry average returns: {industry_average}")
    st.write(f"CAGR: {cagr}")
    st.write(f"Market Cap: {market_cap}")
    st.write(f"Intrinsic Value: {intrinsic_value}")
    st.write(f"Stress Scenarios: {stress_scenarios}")
    st.write(f"Operating Leverage: {operating_leverage}")
    st.write(f"Verdict: {verdict}")
