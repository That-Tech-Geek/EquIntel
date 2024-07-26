import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from joblib import dump, load

@st.cache_data
def load_share_prices(file):
    return pd.read_csv(file, index_col=0, parse_dates=True)

@st.cache_data
def extract_text_from_pdf(uploaded_statements_pdf):
    text = ""
    try:
        with pdfplumber.open(uploaded_statements_pdf) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text

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
        context_pattern = re.compile(rf'.{{0,30}}{key}.{{0,30}}', re.IGNORECASE)
        context_matches = context_pattern.findall(text)
        st.write(f"Could not find {key} in the extracted text. Here are some contexts where it might appear:")
        for context in context_matches:
            st.write(f"...{context}...")
    return []

def get_financial_data_from_pdf(pdf_text, keys):
    data = {key: [] for key in keys}
    date_pattern = re.compile(r'(\d{4}[-/]\d{2}[-/]\d{2})', re.IGNORECASE)
    dates = date_pattern.findall(pdf_text)
    st.write(f"Dates found: {dates}")
    
    for key in keys:
        values = find_all_financial_data_in_text(pdf_text, key)
        for value in values:
            date = dates[min(len(dates) - 1, len(values) - 1)] if dates else 'Unknown'
            data[key].append({'Date': date, 'Value': value})
    
    data_frames = {}
    for key in keys:
        if data[key]:
            df = pd.DataFrame(data[key])
            data_frames[key] = df
    
    return data_frames

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
    return "Stress test results based on financial data."

def pronounce_verdict(roic, stock_returns, industry_average, cagr, market_cap, intrinsic_value, operating_leverage):
    verdict = "Invest" if roic and roic > 0.1 and stock_returns > industry_average and cagr and cagr > 0.05 and market_cap and market_cap < intrinsic_value and operating_leverage and operating_leverage > 0.5 else "Do Not Invest"
    return verdict

@st.cache_resource
def train_price_prediction_model(share_prices):
    share_prices['Date'] = share_prices.index
    share_prices['Date'] = share_prices['Date'].map(datetime.toordinal)
    X = share_prices[['Date']]
    y = share_prices['Close']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    return model

def predict_future_prices(model, share_prices, days_into_future=30):
    last_date = share_prices.index[-1]
    future_dates = [last_date + pd.Timedelta(days=x) for x in range(1, days_into_future + 1)]
    future_dates_ordinal = [date.toordinal() for date in future_dates]
    
    future_prices = model.predict(pd.DataFrame(future_dates_ordinal, columns=['Date']))
    return pd.DataFrame({'Date': future_dates, 'Predicted Prices': future_prices})

@st.cache_resource
def train_clustering_model(financial_data):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(financial_data)
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(scaled_data)
    
    return kmeans, scaler

def cluster_companies(kmeans, scaler, financial_data):
    scaled_data = scaler.transform(financial_data)
    clusters = kmeans.predict(scaled_data)
    return clusters

@st.cache_resource
def train_classification_model(financial_data, labels):
    X_train, X_test, y_train, y_test = train_test_split(financial_data, labels, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    st.write(f"Classification Model Accuracy: {accuracy}")
    
    return model

def classify_investments(model, financial_data):
    return model.predict(financial_data)

st.title("EquiIntel: Comprehensive Equity Analysis AI")

uploaded_share_prices = st.file_uploader("Upload Share Prices CSV", type="csv")
uploaded_statements_pdf = st.file_uploader("Upload Financial Statements PDF", type="pdf")

if uploaded_share_prices and uploaded_statements_pdf:
    share_prices = load_share_prices(uploaded_share_prices)
    pdf_text = extract_text_from_pdf(uploaded_statements_pdf)
    
    st.write("Extracted Text from PDF:")
    st.write(pdf_text[:2000])
    
    financial_keys = ['Net Income', 'Total Assets', 'Current Liabilities', 'Capital Expenditures', 'Total Revenue', 'Market Cap', 'Book Value', 'Shares Outstanding', 'Operating Expenses', 'Cost of Revenue']
    financial_data = get_financial_data_from_pdf(pdf_text, financial_keys)
    
    st.write("Extracted Financial Data:")
    for key in financial_keys:
        if key in financial_data:
            df = financial_data[key]
            if not df.empty:
                st.write(f"{key}:")
                st.write(df)

    roic = calculate_moat_indicators(financial_data)
    investments_in_high, investments_in_low = analyze_investments(financial_data)
