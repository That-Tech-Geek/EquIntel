import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import easyocr

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

# Function to initialize EasyOCR reader
def initialize_easyocr_reader():
    return easyocr.Reader(['en'])

# Function to find all possible values for a financial parameter in the extracted text
def find_all_financial_data_in_text(text, key):
    pattern = re.compile(rf'{key}[\s:]*[\$]?([\d,\.]+)', re.IGNORECASE)
    matches = pattern.findall(text)
    if matches:
        st.write(f"Found possible matches for {key}:")
        results = []
        for match in matches:
            value = float(match.replace(',', '').replace('$', ''))
            results.append(value)
            st.write(f"- {value}")
        return results
    else:
        # Debug: Show the context around the missing key
        context_pattern = re.compile(rf'.{{0,30}}{key}.{{0,30}}', re.IGNORECASE)
        context_matches = context_pattern.findall(text)
        st.write(f"Could not find {key} in the extracted text. Here are some contexts where it might appear:")
        for context in context_matches:
            st.write(f"...{context}...")
    return []

# Function to get financial data from PDF text with associated dates
def get_financial_data_from_pdf(pdf_text, keys):
    data = {key: [] for key in keys}
    
    # Use regex to extract dates and their corresponding financial data
    date_pattern = re.compile(r'(\d{4}[-/]\d{2}[-/]\d{2})', re.IGNORECASE)
    dates = date_pattern.findall(pdf_text)
    st.write(f"Dates found: {dates}")
    
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(find_all_financial_data_in_text, pdf_text, key): key for key in keys}
        for future in as_completed(futures):
            key = futures[future]
            values = future.result()
            for value in values:
                date = dates[min(len(dates) - 1, len(values) - 1)] if dates else 'Unknown'
                data[key].append({'Date': date, 'Value': value})

    # Create a DataFrame for each key with proper indexing
    data_frames = {}
    for key in keys:
        if data[key]:
            df = pd.DataFrame(data[key])
            data_frames[key] = df
    
    return data_frames

# Functions for calculations
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
    
    # Initialize EasyOCR reader
    easyocr_reader = initialize_easyocr_reader()

    # Get financial data from PDF text
    financial_data = get_financial_data_from_pdf(pdf_text, financial_keys)
    
    st.write("Extracted Financial Data:")
    for key in financial_keys:
        if key in financial_data:
            df = financial_data[key]
            if not df.empty:
                st.write(f"{key}:")
                st.write(df)
            else:
                st.write(f"Could not find {key} in the extracted text. Here are some contexts where it might appear:")
                context_pattern = re.compile(rf'.{{0,30}}{key}.{{0,30}}', re.IGNORECASE)
                context_matches = context_pattern.findall(pdf_text)
                for context in context_matches:
                    st.write(f"...{context}...")
                # Display a text input box for additional user input if data is not available
                additional_info = st.text_input(f"Input {key} (if any):", key=key)
                if additional_info:
                    try:
                        financial_data[key] = pd.DataFrame({'Date': ['Unknown'], 'Value': [float(additional_info)]})
                    except ValueError:
                        st.write(f"Invalid input for {key}. Please enter a numeric value.")
    
    # Perform calculations based on the most recent data
    latest_financials = {key: df['Value'].iloc[-1] for key, df in financial_data.items() if not df.empty}
    
    with ThreadPoolExecutor() as executor:
        future_results = {
            'roic': executor.submit(calculate_moat_indicators, latest_financials),
            'investments': executor.submit(analyze_investments, latest_financials),
            'growth': executor.submit(assess_growth, latest_financials),
            'valuation': executor.submit(define_valuation, latest_financials),
            'leverage': executor.submit(find_operating_leverage, latest_financials)
        }

        roic = None
        investments_in_high = investments_in_low = None
        cagr = None
        market_cap = intrinsic_value = None
        operating_leverage = None

        for key, future in future_results.items():
            result = future.result()
            if key == 'roic':
                roic = result
            elif key == 'investments':
                investments_in_high, investments_in_low = result
            elif key == 'growth':
                cagr = result
            elif key == 'valuation':
                market_cap, intrinsic_value = result
            elif key == 'leverage':
                operating_leverage = result

    stock_returns = share_prices['Close'].pct_change().mean()
    industry_average = 0.05  # Example fixed value; replace with actual industry average
    stress_scenarios = conduct_stress_test(latest_financials)
    verdict = pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage)

    st.write(f"ROIC: {roic}")
    st.write(f"Investments in High Performing Companies: {investments_in_high}")
    st.write(f"Investments in Low Performing Companies: {investments_in_low}")
    st.write(f"Stock returns: {stock_returns}")
    st.write(f"Industry average returns: {industry_average}")
    st.write(f"CAGR: {cagr}")
    st.write(f"Market Cap: {market_cap}")
    st.write(f"Intrinsic Value: {intrinsic_value}")
    st.write(f"Stress Scenarios: {stress_scenarios}")
    st.write(f"Operating Leverage: {operating_leverage}")
    st.write(f"Verdict: {verdict}")
