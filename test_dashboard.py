# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 12:09:07 2026

@author: wb611818
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="WBL Survey Monitoring", layout="wide")
st.title("WBL Contributor Survey Monitoring")

data_path = Path(__file__).parent / "dashboard_data.csv"

try:
    df = pd.read_csv(data_path)
except:
    st.error("Run test_worker.py first to generate dashboard_data.csv")
    st.stop()

st.subheader("Survey Performance by Indicator")

st.dataframe(df, use_container_width=True)

st.subheader("Response Rate")

st.bar_chart(df.set_index("Indicator Name")["Response Rate (%)"])

st.subheader("Sent vs Received")

st.bar_chart(df.set_index("Indicator Name")[["Surveys Sent", "Surveys Received"]])