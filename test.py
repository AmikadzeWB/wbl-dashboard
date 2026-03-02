# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 09:17:47 2026

@author: wb611818
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Test Dashboard", layout="wide")
st.title("Very Simple Test Dashboard")

# --- Make fake data (so you don't need files yet) ---
rng = np.random.default_rng(42)
weeks = pd.date_range("2026-01-05", periods=10, freq="W-MON").strftime("%Y-%m-%d")
economies = ["Albania", "Georgia", "Kosovo", "Armenia"]
topics = ["Work", "Pay", "Childcare"]

df = pd.DataFrame({
    "week": rng.choice(weeks, size=300),
    "economy": rng.choice(economies, size=300),
    "topic": rng.choice(topics, size=300),
    "value": np.round(rng.normal(loc=60, scale=15, size=300).clip(0, 100), 1)
})

# --- Sidebar filters ---
st.sidebar.header("Filters")
econ = st.sidebar.multiselect("Economy", sorted(df["economy"].unique()), default=sorted(df["economy"].unique()))
topic = st.sidebar.multiselect("Topic", sorted(df["topic"].unique()), default=sorted(df["topic"].unique()))
week_min, week_max = st.sidebar.select_slider(
    "Week range",
    options=sorted(df["week"].unique()),
    value=(sorted(df["week"].unique())[0], sorted(df["week"].unique())[-1])
)

# Apply filters
f = df[
    (df["economy"].isin(econ)) &
    (df["topic"].isin(topic)) &
    (df["week"] >= week_min) &
    (df["week"] <= week_max)
].copy()

# --- KPIs ---
c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(f))
c2.metric("Avg value", f["value"].mean().round(2) if len(f) else "—")
c3.metric("Max value", f["value"].max() if len(f) else "—")

st.divider()

# --- Charts ---
left, right = st.columns(2)

with left:
    st.subheader("Average value by week")
    by_week = f.groupby("week", as_index=False)["value"].mean().sort_values("week")
    st.line_chart(by_week, x="week", y="value", height=320)

with right:
    st.subheader("Average value by economy")
    by_econ = f.groupby("economy", as_index=False)["value"].mean().sort_values("value", ascending=False)
    st.bar_chart(by_econ, x="economy", y="value", height=320)

st.divider()
st.subheader("Data preview")
st.dataframe(f.sort_values(["week", "economy", "topic"]).head(50), use_container_width=True)