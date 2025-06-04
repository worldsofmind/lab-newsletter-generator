
import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Newsletter Generator", layout="wide")

st.title("📬 LAB Officer Newsletter Generator")

# Sidebar file uploads
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload ratings.csv", type="csv")
    caseload_file = st.file_uploader("Upload case_load.xlsx", type=["xls", "xlsx"])
    namelist_file = st.file_uploader("Upload namelist.csv", type="csv")

if ratings_file and caseload_file and namelist_file:
    with st.spinner("Processing files..."):
        ratings_df, caseload_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file
        )

    officer_names = namelist_df['name_self'].dropna().unique().tolist()
    selected_officer = st.selectbox("Select an officer", ["-- Select --"] + officer_names)
    generate_all = st.checkbox("Generate for all officers")

    if generate_all:
        with st.spinner("Generating newsletters for all officers..."):
            officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
            render_newsletters(officer_reports)
            st.success("✅ All newsletters generated.")
    elif selected_officer != "-- Select --":
        officer_row = namelist_df[namelist_df['name_self'] == selected_officer].iloc[0]
        with st.spinner(f"Generating newsletter for {selected_officer}..."):
            officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df, period)
            render_newsletters([officer_report])
            st.success(f"✅ Newsletter for {selected_officer} generated.")
    else:
        st.warning("Please select an officer or choose to generate all.")
else:
    st.warning("📥 Please upload all required files to begin.")
