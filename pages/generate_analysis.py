import os
import sys
import pandas as pd
import streamlit as st 


PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.utils import fetch_product_names_from_cloud
from src.data_report.generate_data_report import DashboardGenerator

# Configure page properties cleanly first
st.set_page_config(page_title="Product Analysis Dashboard", layout="wide")
st.title("📊 Product Analytics Report")

mongo_con = MongoIO()

# Initialize global tracking metrics so the page doesn't crash on initial boot
if "data" not in st.session_state:
    st.session_state["data"] = False

def create_analysis_page(review_data: pd.DataFrame):
    if review_data is not None and not review_data.empty:
        st.subheader(f"🗂️ Raw Dataset Preview ({len(review_data)} rows loaded)")
        st.dataframe(review_data, use_container_width=True)
        
        st.markdown("---")
        
        
        # This keeps the dashboard visible permanently until the user unchecks it.
        generate_report = st.toggle("🚀 Generate Full Analytics Report Visualization", value=True)
        
        if generate_report:
            with st.spinner("Processing text arrays and rendering Plotly visualizations..."):
                try:
                    dashboard = DashboardGenerator(review_data)

                    # Create layout tabs for cleaner report presentation
                    tab1, tab2 = st.tabs(["📈 Global Metrics Overview", "📦 Product Specific Insights"])
                    
                    with tab1:
                        dashboard.display_general_info()

                    with tab2:
                        dashboard.display_product_sections()
                        
                except Exception as e:
                    st.error(f"Failed to generate dashboard graphics: {e}")
    else:
        st.error("⚠️ Retrieved database collection payload is completely empty.")


# ==========================================
# 🛑 MAIN RUNTIME EXECUTION BLOCK 🛑
# ==========================================
try:
    if st.session_state.get("data") == True and SESSION_PRODUCT_KEY in st.session_state:
        search_target = st.session_state[SESSION_PRODUCT_KEY]
        
        with st.spinner(f"Pulling fresh records for '{search_target}' from MongoDB Atlas..."):
            data = mongo_con.get_reviews(product_name=search_target)
            
        create_analysis_page(data)
    else:
        # Fallback if page is visited out of sequence
        with st.sidebar:
            st.warning("No data loaded in memory workspace cache.")
            st.markdown("Please return to the **Main Search Page**, look up an item, and click **Scrape Reviews** first!")
            
        st.info("👋 Welcome! Please run the scraper on the home page first to unlock this analysis pipeline dashboard.")

except Exception as e:
    st.error(f"An unexpected pipeline tracking failure occurred: {e}")
