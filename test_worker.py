# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 11:49:16 2026
@author: Ana Mikadze
"""

import pandas as pd
from pathlib import Path

SENT_STATUSES = ["Sent", "Received", "Confirmed", "Declined this Year"]
RECEIVED_STATUSES = ["Received"]

TOPIC_SRC = "Indicator Name"
GLOBAL_SRC = "Associated Global Firm (Associated Contributor) (Contributor)"
ECON_SRC = "Associated Economy (Associated Campaign Economy) (Campaign Economy)"
SECTOR_SRC = "Associated Account Sector (Associated Contributor) (Contributor)"


def main(excel_path: str) -> Path:
    df = pd.read_excel(excel_path)

    # ---- Standardize needed columns without creating duplicate names ----
    df = df.rename(columns={
        TOPIC_SRC: "Topic",
        GLOBAL_SRC: "Global",
        ECON_SRC: "Economy",
        SECTOR_SRC: "Sector",
    })

    # ---- Per-topic Sent/Received (one table) ----
    sent = (df[df["Survey Status"].isin(SENT_STATUSES)]
            .groupby("Topic").size().rename("Surveys Sent"))
    recv = (df[df["Survey Status"].isin(RECEIVED_STATUSES)]
            .groupby("Topic").size().rename("Surveys Received"))

    summary = pd.concat([sent, recv], axis=1).fillna(0).reset_index()
    summary["Response Rate (%)"] = (summary["Surveys Received"] / summary["Surveys Sent"] * 100).round(1)
    summary.loc[summary["Surveys Sent"].eq(0), "Response Rate (%)"] = 0

    # ---- Closed economy metrics (PER TOPIC) ----
    df_recv = df[df["Survey Status"].isin(RECEIVED_STATUSES)].copy()

    for col in ["Economy", "Sector", "Global"]:
        if col in df_recv.columns:
            df_recv[col] = df_recv[col].astype(str).str.strip()

    # Aggregate at Topic + Economy level
    topic_econ = (
        df_recv.groupby(["Topic", "Economy"])
        .agg(
            Received_Count=("Survey Status", "size"),
            All_Private=("Sector", lambda s: s.eq("Private").all()),
            All_Global_No=("Global", lambda s: s.eq("No").all()),
        )
        .reset_index()
    )

    # Coding closed per Topic: >= 2 received per (Topic, Economy)
    coding_closed_per_topic = (
        topic_econ[topic_econ["Received_Count"] >= 2]
        .groupby("Topic")
        .size()
        .rename("Economies Closed (Coding)")
    )

    # EP closed per Topic: >= 3 received AND all private AND all global == No (within that Topic+Economy)
    ep_closed_per_topic = (
        topic_econ[
            (topic_econ["Received_Count"] >= 3) &
            (topic_econ["All_Private"]) &
            (topic_econ["All_Global_No"])
        ]
        .groupby("Topic")
        .size()
        .rename("Economies Closed (EP)")
    )

    # Merge closure counts into summary
    summary = summary.merge(coding_closed_per_topic, on="Topic", how="left")
    summary = summary.merge(ep_closed_per_topic, on="Topic", how="left")

    summary[["Economies Closed (Coding)", "Economies Closed (EP)"]] = (
        summary[["Economies Closed (Coding)", "Economies Closed (EP)"]].fillna(0).astype(int)
    )

    # ---- Save ----
    output_path = Path(excel_path).parent / "dashboard_data.csv"
    summary.to_csv(output_path, index=False)
    print("Saved:", output_path)
    return output_path


if __name__ == "__main__":
    excel_path = r"C:\Users\wb611818\WBG\DEC - Women, Business and the Law - WB Group - Dashboard\CRM_Test_Data.xlsx"
    main(excel_path)
