import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="AI Financial Analyst Bot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("💰 AI Financial Analyst & Portfolio Manager")

    st.markdown("""
    Welcome to your personal AI-powered Financial Analyst!
    
    This application helps you analyze your stock portfolio, get the latest news, and receive AI-driven insights.
    
    **Get started by following these simple steps:**
    1.  **Upload your Portfolio**: Use the uploader below to upload an Excel file (`.xlsx`) of your stock portfolio.
        The file should contain columns like 'Stock Symbol', 'Quantity', and 'Average Price'.
    2.  **Analyze Your Portfolio**: Navigate to the `Portfolio Analysis` page to see a detailed breakdown of your holdings,
        including current values, profit/loss, and the latest news for each stock.
    3.  **Chat with the AI Analyst**: Go to the `AI Financial Analyst` page to ask questions about your portfolio,
        market trends, or specific stocks.
        
    **Note**: Ensure your stock symbols are correct as per market listings (e.g., 'RELIANCE.NS' for Reliance Industries on NSE).
    """)

    st.sidebar.header("Portfolio Upload")

    uploaded_file = st.sidebar.file_uploader("Upload your portfolio Excel file", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # Read the uploaded Excel file
            portfolio_df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Store the portfolio dataframe in the session state
            st.session_state['portfolio_df'] = portfolio_df
            
            st.sidebar.success("Portfolio uploaded successfully!")
            
            st.subheader("Your Uploaded Portfolio")
            st.dataframe(portfolio_df)

        except Exception as e:
            st.sidebar.error(f"Error reading the file: {e}")
            st.error("There was an issue processing your Excel file. Please ensure it's in the correct format.")

    else:
        st.info("Please upload a portfolio file to begin analysis.")
        if 'portfolio_df' in st.session_state:
            del st.session_state['portfolio_df']


if __name__ == "__main__":
    main()
