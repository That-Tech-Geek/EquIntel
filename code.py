import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re

# Configure tesseract executable path (adjust if necessary)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update to your Tesseract installation path

# Function to load uploaded share price data
def load_share_prices(file):
    return pd.read_csv(file, index_col=0, parse_dates=True)

# Function to convert PDF to images
def convert_pdf_to_images(pdf_file):
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        images = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        return images
    except Exception as e:
        st.error(f"Error converting PDF to images: {e}")
        return []

# Function to extract text from images using OCR
def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR not found. Please ensure it is installed and configured correctly.")
        return ""

# Function to extract text from PDF by converting to images and applying OCR
def extract_text_from_pdf(uploaded_statements_pdf):
    images = convert_pdf_to_images(uploaded_statements_pdf)
    text = ""
    for image in images:
        text += extract_text_from_image(image)
    return text

# Function to find specific financial data in the extracted text
def find_financial_data_in_text(text, key):
    pattern = re.compile(rf'{key}[\s:]*([\d,\.]+)', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return float(match.group(1).replace(',', '').replace('$', ''))
    st.write(f"Could not find {key} in the extracted text.")
    return None

# Function to get financial data from PDF text
def get_financial_data_from_pdf(pdf_text, keys):
    data = {}
    for key in keys:
        data[key] = find_financial_data_in_text(pdf_text, key)
    return pd.DataFrame([data])

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

def calculate_industry_average(exchange, financial_data):
    # Placeholder function to get industry average based on the exchange
    # Replace with actual calculation or data retrieval logic
    industry_averages = {
        'NSE': 0.05,  # Example fixed value; replace with actual industry average calculation
        'NYSE': 0.04,
        'NASDAQ': 0.06,
        # Add other exchanges and their industry averages here
    }
    return industry_averages.get(exchange, None)

def pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage):
    verdict = "Invest" if roic and roic > 0.1 and stock_returns > industry_average and cagr and cagr > 0.05 and market_cap and market_cap < intrinsic_value and operating_leverage and operating_leverage > 0.5 else "Do Not Invest"
    return verdict

# Streamlit UI
st.title("EquiIntel: Comprehensive Equity Analysis AI")

uploaded_share_prices = st.file_uploader("Upload Share Prices CSV", type="csv")
uploaded_statements_pdf = st.file_uploader("Upload Financial Statements PDF", type="pdf")
company_exchange = st.selectbox("Select the company's exchange", ['NSE', 'NYSE', 'NASDAQ'])  # Add other exchanges if needed

if uploaded_share_prices and uploaded_statements_pdf:
    share_prices = load_share_prices(uploaded_share_prices)
    pdf_text = extract_text_from_pdf(uploaded_statements_pdf)
    
    st.write("Extracted Text from PDF:")
    st.write(pdf_text[:2000])  # Display the first 2000 characters for debugging
    
    financial_keys = ['Net Income', 'Total Assets', 'Current Liabilities', 'Capital Expenditures', 'Total Revenue', 'Market Cap', 'Book Value', 'Shares Outstanding', 'Operating Expenses', 'Cost of Revenue']
    financial_data = get_financial_data_from_pdf(pdf_text, financial_keys)
    
    st.write("Extracted Financial Data:")
    st.write(financial_data)
    
    roic = calculate_moat_indicators(financial_data)
    investments_in_high, investments_in_low = analyze_investments(financial_data)
    stock_returns = share_prices['Close'].pct_change().mean()
    industry_average = calculate_industry_average(company_exchange, financial_data)
    cagr = assess_growth(financial_data)
    market_cap, intrinsic_value = define_valuation(financial_data)
    stress_scenarios = conduct_stress_test(financial_data)
    operating_leverage = find_operating_leverage(financial_data)
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
