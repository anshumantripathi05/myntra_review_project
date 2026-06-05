import os
import sys
import pandas as pd
import streamlit as st 

# Force inject the root path so 'src' module imports always resolve safely
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews

st.set_page_config(page_title="myntra-review-scrapper")
st.title("Myntra Review Scrapper")


if "data" not in st.session_state:
    st.session_state["data"] = False


if SESSION_PRODUCT_KEY not in st.session_state:
    st.session_state[SESSION_PRODUCT_KEY] = ""


def form_input():
    product = st.text_input("Search Products")
    st.session_state[SESSION_PRODUCT_KEY] = product
    
    no_of_products = st.number_input("No of products to search",
                                     step=1,
                                     min_value=1,
                                     value=5)

    if st.button("Scrape Reviews"):
        if not product.strip():
            st.error("Please enter a product name first!")
            return

        with st.spinner(f"Scraping live datasets from Myntra..."):
            scrapper = ScrapeReviews(
                product_name=product,
                no_of_products=int(no_of_products)
            )
            scrapped_data = scrapper.get_review_data()
            
        if scrapped_data is not None and not scrapped_data.empty:
            # 🔥 Switch flag to True inside memory workspace cache
            st.session_state["data"] = True
            
            with st.spinner("Syncing payloads with MongoDB Cloud Cluster..."):
                try:
                    mongoio = MongoIO()
                    mongoio.store_reviews(product_name=product, reviews=scrapped_data)
                    st.success("🎉 Stored Data into mongodb! Click on the Analysis page in the sidebar.")
                except Exception as e:
                    st.warning(f"Data scraped, but MongoDB storage failed: {e}")

            st.dataframe(scrapped_data, use_container_width=True)
        else:
            st.error("Scraper returned an empty dataset. Try another product.")

if __name__ == "__main__":
    form_input()
