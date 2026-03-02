# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 12:09:07 2026

@author: wb611818
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="WBL 2027 Tracking Dashboard", layout="wide")
st.title("WBL 2027 Tracking Dashboard")

data_path = Path(__file__).parent / "dashboard_data.csv"

try:
    df = pd.read_csv(data_path)
except:
    st.error("Run test_worker.py first to generate dashboard_data.csv")
    st.stop()

st.subheader("Data Collection Snapshot")

st.dataframe(df, use_container_width=True)

