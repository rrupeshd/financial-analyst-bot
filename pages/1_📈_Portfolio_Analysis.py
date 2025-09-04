import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from utils import get_stock_news, get_stock_data
import datetime

st.set_page_config(page_title="Portfolio Analysis", page_icon="📈", layout="wide")

st.title("📈 Portfolio Analysis")

if 'portfolio_df' not in st.session_state or st.session_state['portfolio_df'].empty:
    st.warning("Please upload your portfolio on the main page to see the analysis.")
    st.stop()

portfolio_df = st.session_state['portfolio_df']

# --- Data Processing and Analysis ---
try:
    # Standardize column names
    portfolio_df.columns = [col.lower().replace(' ', '_') for col in portfolio_df.columns]
    
    required_cols = ['stock_symbol', 'quantity', 'average_price']
    if not all(col in portfolio_df.columns for col in required_cols):
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_cols)}")
        st.stop()

    with st.spinner("Fetching live stock data and news... This may take a moment."):
        # Fetch current data for each stock
        portfolio_analysis = []
        for index, row in portfolio_df.iterrows():
            stock_symbol = row['stock_symbol']
            quantity = row['quantity']
            avg_price = row['average_price']
            
            stock_data = get_stock_data(stock_symbol)
            if stock_data:
                current_price = stock_data['current_price']
                investment_value = quantity * avg_price
                current_value = quantity * current_price
                pl = current_value - investment_value
                pl_percent = (pl / investment_value) * 100 if investment_value > 0 else 0
                
                portfolio_analysis.append({
                    "Stock Symbol": stock_symbol,
                    "Quantity": quantity,
                    "Average Price": avg_price,
                    "Current Price": current_price,
                    "Investment Value": investment_value,
                    "Current Value": current_value,
                    "Profit/Loss": pl,
                    "P/L %": pl_percent
                })
        
        analysis_df = pd.DataFrame(portfolio_analysis)

    st.session_state['analysis_df'] = analysis_df

    st.header("Portfolio Overview")
    st.dataframe(analysis_df.style.format({
        'Average Price': '₹{:.2f}', 'Current Price': '₹{:.2f}',
        'Investment Value': '₹{:.2f}', 'Current Value': '₹{:.2f}',
        'Profit/Loss': '₹{:.2f}', 'P/L %': '{:.2f}%'
    }).applymap(
        lambda x: 'color: green' if x > 0 else 'color: red',
        subset=['Profit/Loss', 'P/L %']
    ))
    
    # --- Portfolio Summary Metrics ---
    total_investment = analysis_df['Investment Value'].sum()
    total_current_value = analysis_df['Current Value'].sum()
    total_pl = total_current_value - total_investment
    total_pl_percent = (total_pl / total_investment) * 100 if total_investment > 0 else 0
    
    st.header("Portfolio Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Investment", f"₹{total_investment:,.2f}")
    col2.metric("Total Current Value", f"₹{total_current_value:,.2f}")
    col3.metric("Overall Profit/Loss", f"₹{total_pl:,.2f}", f"{total_pl_percent:.2f}%")

    # --- Visualizations ---
    st.header("Visualizations")
    
    fig_allocation = px.pie(analysis_df, names='Stock Symbol', values='Current Value', title='Portfolio Allocation by Current Value')
    st.plotly_chart(fig_allocation, use_container_width=True)

    fig_pl = px.bar(analysis_df, x='Stock Symbol', y='Profit/Loss', color='Profit/Loss',
                    title='Profit/Loss per Stock', labels={'Profit/Loss': 'Profit/Loss (₹)'},
                    color_continuous_scale=px.colors.diverging.RdYlGn,
                    color_continuous_midpoint=0)
    st.plotly_chart(fig_pl, use_container_width=True)
    
    # --- Individual Stock Analysis ---
    st.header("Individual Stock Analysis")
    
    selected_stock = st.selectbox("Select a stock for detailed analysis", analysis_df['Stock Symbol'].unique())
    
    if selected_stock:
        st.subheader(f"Analysis for {selected_stock}")
        
        # Display latest news
        with st.expander("Latest News", expanded=True):
            with st.spinner(f"Fetching news for {selected_stock}..."):
                news = get_stock_news(selected_stock)
                if news:
                    for item in news:
                        st.write(f"**[{item['title']}]({item['url']})**")
                        st.caption(f"Source: {item['source']['name']} | Published: {item['publishedAt']}")
                else:
                    st.write("No recent news found.")

        # Display historical price chart
        with st.expander("Historical Price Chart"):
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)
            
            stock_hist = yf.download(selected_stock, start=start_date, end=end_date)
            if not stock_hist.empty:
                fig_hist = px.line(stock_hist, x=stock_hist.index, y='Close', title=f"{selected_stock} Price Chart (1 Year)")
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("Could not fetch historical data.")

except Exception as e:
    st.error(f"An error occurred during analysis: {e}")
    st.info("Please ensure your Excel file is formatted correctly and stock symbols are valid.")
