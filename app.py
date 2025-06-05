import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="📬 LAB Officer Newsletter Generator", layout="wide")

# Sidebar file uploads
with st.sidebar:
    st.title("📂 Upload Files")
    ratings_file = st.file_uploader("Upload ratings.csv", type="csv")
    caseload_file = st.file_uploader("Upload case_load.csv (CSV format only)", type="csv")
    namelist_file = st.file_uploader("Upload namelist.csv", type="csv")

if ratings_file and caseload_file and namelist_file:
    try:
    officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df, period, caseload_df)
    reports = [officer_report]
    st.success(f"✅ Generated newsletter for: {officer_name}")
        ratings_df, caseload_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file
        )
        namelist_df.columns = namelist_df.columns.str.strip()
    except Exception as e:
        st.error(f"❌ Error loading files: {e}")
        st.stop()

    st.title("📬 LAB Officer Newsletter Generator")

    generate_all = st.checkbox("Generate for all officers")

    if generate_all:
        try:
    officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df, period, caseload_df)
    reports = [officer_report]
    st.success(f"✅ Generated newsletter for: {officer_name}")
            officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
            render_newsletters(officer_reports)
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        officer_names = namelist_df['Name'].dropna().sort_values().unique().tolist()
        selected_officer = st.selectbox("Select an officer", ["-- Select --"] + officer_names)

        if selected_officer != "-- Select --":
            officer_row = namelist_df[namelist_df['Name'] == selected_officer].iloc[0]
            try:
    officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df, period, caseload_df)
    reports = [officer_report]
    st.success(f"✅ Generated newsletter for: {officer_name}")
                officer_report["period"] = period
                render_newsletters([officer_report])
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
else:
    st.info("📄 Please upload all three required files to continue.")
