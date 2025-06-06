import streamlit as st
import pandas as pd
import datetime
from utils.data_loader import load_all_data
from utils.processor import compute_officer_stats
from utils.renderer import render_newsletters
import os
from pathlib import Path # <--- THIS IS THE MISSING LINE!

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# --- SIDEBAR FILE UPLOADS ---
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

# --- MAIN LOGIC ---
if ratings_file and caseload_file and namelist_file:
    try:
        with st.spinner("Processing data..."):
            ratings_df, caseload_df, namelist_df, period = load_all_data(ratings_file, caseload_file, namelist_file)

            all_reports = []
            for _, officer_row in namelist_df.iterrows():
                officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df)
                all_reports.append(officer_report)

            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            render_newsletters(all_reports, output_dir)

        st.success("✅ Newsletters generated successfully.")
        for report in all_reports:
            name = report['name']
            abbreviation = report['abbreviation']
            file_path = output_dir / f"{abbreviation}_Newsletter.html"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.download_button(
                    label=f"📩 Download {abbreviation}_Newsletter.html",
                    data=html_content,
                    file_name=f"{abbreviation}_Newsletter.html",
                    mime="text/html"
                )

    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")
else:
    st.info("📥 Please upload all three files to begin.")
