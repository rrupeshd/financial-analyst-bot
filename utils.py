import streamlit as st
import yfinance as yf
from duckduckgo_search import DDGS
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
# Configure the Gemini API key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.warning("Gemini API key not found. Please add it to your Streamlit secrets.", icon="⚠️")

# --- Yahoo Finance Functions ---
@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_stock_data(symbol):
    """Fetches current stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        if current_price:
            return {'current_price': current_price}
        else:
            # Fallback for symbols that might not have 'currentPrice'
            hist = stock.history(period="1d")
            if not hist.empty:
                return {'current_price': hist['Close'].iloc[-1]}
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# --- News Fetching Functions ---
@st.cache_data(ttl=1800) # Cache for 30 minutes
def get_stock_news(symbol):
    """Fetches news for a given stock symbol using DuckDuckGo Search."""
    try:
        query = f"latest financial news for {symbol} stock"
        with DDGS() as ddgs:
            results = list(ddgs.news(query, region='en-in', safesearch='moderate', max_results=5))
        
        formatted_results = []
        if not results:
            return []

        for res in results:
            # Defensive check to ensure the result is a dictionary
            if isinstance(res, dict):
                formatted_results.append({
                    'title': res.get('title', 'No title available'),
                    'url': res.get('url', '#'),
                    'source': {'name': res.get('source', 'Unknown source')},
                    'publishedAt': res.get('date', 'No date available') 
                })
        return formatted_results
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []

def get_all_news(symbols):
    """Fetches news for a list of stock symbols and compiles them."""
    news_list = []
    for symbol in symbols:
        news = get_stock_news(symbol)
        if news:
            news_list.append(f"\n--- News for {symbol} ---\n")
            for item in news:
                # Safely get the title
                title = item.get('title')
                if title:
                    news_list.append(f"- {title}")
    return "\n".join(news_list) if news_list else "No recent news found for the stocks in the portfolio."


# --- Gemini AI Functions ---
def get_gemini_response(prompt):
    """
    Gets a response from the Gemini model based on the provided prompt.
    """
    if not st.secrets.get("GEMINI_API_KEY"):
        return "Gemini API key is not configured. Please add it to your Streamlit secrets."
        
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return f"An error occurred while generating the AI response: {e}"

def parse_portfolio_file(uploaded_file):
    """
    Parses the uploaded portfolio file, supporting both simple and Zerodha formats.
    Returns a standardized DataFrame or None if parsing fails.
    """
    try:
        # Try reading multiple sheets if available, prioritizing 'Equity' for Zerodha reports
        xls = pd.ExcelFile(uploaded_file)
        df = None
        if 'Equity' in xls.sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name='Equity')
        else:
            df = pd.read_excel(uploaded_file)

        # --- Attempt 1: Simple format ---
        # Create a copy for manipulation
        df_simple_check = df.copy()
        # Standardize column names for checking
        df_simple_check.columns = [str(col).strip().lower().replace(' ', '_') for col in df_simple_check.columns]
        simple_cols = {'stock_symbol': 'stock_symbol', 'quantity': 'quantity', 'average_price': 'average_price'}
        
        if all(col in df_simple_check.columns for col in simple_cols.keys()):
            df_simple_check = df_simple_check.rename(columns=simple_cols)
            # Ensure required columns are numeric
            df_simple_check['quantity'] = pd.to_numeric(df_simple_check['quantity'], errors='coerce')
            df_simple_check['average_price'] = pd.to_numeric(df_simple_check['average_price'], errors='coerce')
            return df_simple_check[['stock_symbol', 'quantity', 'average_price']].dropna()

        # --- Attempt 2: Zerodha format ---
        # Find the header row which contains 'Symbol' and 'ISIN'
        header_row_index = -1
        for i, row in df.iterrows():
            row_str = ''.join(map(str, row.values))
            if 'Symbol' in row_str and 'ISIN' in row_str:
                header_row_index = i
                break
        
        if header_row_index != -1:
            # Re-read the file skipping the header rows
            if 'Equity' in xls.sheet_names:
                df = pd.read_excel(uploaded_file, sheet_name='Equity', skiprows=header_row_index + 1)
            else:
                df = pd.read_excel(uploaded_file, skiprows=header_row_index + 1)

            zerodha_cols = {
                'Symbol': 'stock_symbol',
                'Quantity Available': 'quantity',
                'Average Price': 'average_price'
            }
            
            # Check if all required zerodha columns are present
            if all(col in df.columns for col in zerodha_cols.keys()):
                df = df[list(zerodha_cols.keys())].rename(columns=zerodha_cols)
                # Append .NS for yfinance compatibility, assuming NSE stocks
                df['stock_symbol'] = df['stock_symbol'].astype(str).str.strip() + '.NS'
                # Ensure required columns are numeric
                df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
                df['average_price'] = pd.to_numeric(df['average_price'], errors='coerce')
                return df[['stock_symbol', 'quantity', 'average_price']].dropna()

        return None # Return None if no valid format is found

    except Exception as e:
        st.error(f"Failed to parse portfolio file: {e}")
        return None


