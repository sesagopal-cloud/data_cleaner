import streamlit as st
import pandas as pd
import config
from ai_interface import BankingAI
from chart_engine import ChartEngine
import os

# Page Config
st.set_page_config(page_title="AI Banking Architect", page_icon="🏦", layout="wide")

# Custom CSS for "Premium" look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatInput { border-radius: 20px; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #4CAF50; }
</style>
""", unsafe_allow_html=True)

# Helper to load data
@st.cache_data
def load_data():
    path = config.OUTPUT_DIR / "master_clean_data.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)

def main():
    st.title("🏦 AI Banking Data Architect")
    st.caption("Automated Cleaning • Validation • AI Analytics")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Control Panel")
        if st.button("🔄 Reload Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.header("📂 System Files")
        if (config.OUTPUT_DIR / "master_clean_data.csv").exists():
            st.success("✅ Cleaned Data Ready")
        else:
            st.error("❌ No Data Found. Run Pipeline.")
            
    # --- Main Content ---
    df = load_data()
    
    if df is not None:
        # Initialize AI
        ai = BankingAI(str(config.OUTPUT_DIR / "master_clean_data.csv"))
        chart = ChartEngine()
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["💬 AI Assistant", "📊 Dashboard", "💾 Data View"])
        
        with tab1:
            st.subheader("Ask questions about your banking data")
            
            # Chat History
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # User Input
            if prompt := st.chat_input("Ex: 'Show total amount for New York branch'"):
                # 1. User Message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # 2. AI Processing
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        intent = ai.parse_intent(prompt)
                        result = ai.process_query(prompt)
                        
                        response_text = result['text']
                        st.markdown(response_text)
                        
                        # Add Chart if requested or implied
                        if intent == 'chart' or 'trend' in prompt.lower():
                            if result['data'] is not None and not result['data'].empty:
                                fig = chart.plot_trend(result['data'])
                                st.plotly_chart(fig, use_container_width=True)
                        
                st.session_state.messages.append({"role": "assistant", "content": response_text})

        with tab2:
            st.subheader("Executive Overview")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Transactions", len(df))
            col1.metric("Total Volume", f"${df['Amount'].sum():,.2f}")
            col2.metric("Avg Transaction", f"${df['Amount'].mean():,.2f}")
            
            st.markdown("### Transaction Volume Over Time")
            fig_trend = chart.plot_trend(df)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.markdown("### Branch Distribution")
            fig_dist = chart.plot_distribution(df, category_col="Branch")
            st.plotly_chart(fig_dist, use_container_width=True)

        with tab3:
            st.dataframe(df)

    else:
        st.warning("Please run the Backend Pipeline (`main.py`) to generate data first.")

if __name__ == "__main__":
    main()
