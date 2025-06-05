
import streamlit as st
import pandas as pd
import zipfile
import os
import shutil
from utils.data_loader import load_all_data
from utils.processor import compute_officer_stats
from utils.renderer import render_newsletters

# Setup directories
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR)

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type=["csv"])
    caseload_file = st.file_uploader("Upload `case_load.csv`", type=["csv"])
    namelist_file = st.file_uploader("Upload `namelist.csv`", type=["csv"])

if ratings_file and caseload_file and namelist_file:
    try:
        ratings_df, caseload_df, namelist_df, period = load_all_data(ratings_file, caseload_file, namelist_file)
        reports = []

        for _, officer_row in namelist_df.iterrows():
            officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df, period, caseload_df)
            reports.append(officer_report)

        render_newsletters(reports)

        st.success("✅ Newsletters generated successfully.")
        # Show individual download links
        for report in reports:
            file_name = f"{report['abbreviation']}_Newsletter.html"
            file_path = os.path.join(GENERATED_DIR, file_name)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Download {file_name}",
                        data=f,
                        file_name=file_name,
                        mime="text/html"
                    )

        # Optionally zip all and offer bulk download
        zip_path = os.path.join(GENERATED_DIR, "all_newsletters.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for report in reports:
                file_name = f"{report['abbreviation']}_Newsletter.html"
                file_path = os.path.join(GENERATED_DIR, file_name)
                zipf.write(file_path, arcname=file_name)
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Download All Newsletters (.zip)",
                data=f,
                file_name="all_newsletters.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")
else:
    st.info("👈 Upload all 3 files to begin.")
