import os
import sys

# 1. Capture the root project workspace path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. FORCE look into your environment site-packages folder
# This guarantees Python can see 'database_connect' no matter how folders are nested!
VENV_PACKAGES = os.path.join(PROJECT_ROOT, "env", "Lib", "site-packages")
if VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)


import pandas as pd
from database_connect import mongo_operation as mongo 
import os, sys
from src.constants import *
from src.exception import CustomException
import streamlit as st


class MongoIO:
    mongo_ins = None

    def __init__(self):
        if MongoIO.mongo_ins is None:
            mongo_db_url = st.secrets["mongodb+srv://anshuman05:KvgK3qHVsHIGoXvo@cluster0.pkcbxgj.mongodb.net/?appName=Cluster0"]
            if mongo_db_url is None:
                raise Exception(f"Environment key: {MONGODB_URL_KEY} is not set.")
            MongoIO.mongo_ins = mongo(client_url=mongo_db_url,
                                      database_name=MONGO_DATABASE_NAME)
        self.mongo_ins = MongoIO.mongo_ins

    def store_reviews(self,
                      product_name: str, reviews: pd.DataFrame):
        try:
            collection_name = product_name.replace(" ", "_")
            self.mongo_ins.bulk_insert(reviews,
                                       collection_name)

        except Exception as e:
            raise CustomException(e, sys)

    def get_reviews(self,
                    product_name: str):
        try:
            data = self.mongo_ins.find(
                collection_name=product_name.replace(" ", "_")
            )

            return data

        except Exception as e:
            raise CustomException(e, sys)

