
import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="📬 LAB Officer Newsletter Generator", layout="wide")

# Sidebar file uploads
with st.sidebar:
    st.title("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.xlsx`", type=["xls", "xlsx"])
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

if ratings_file and caseload_file and namelist_file:
    try:
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
            officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
            render_newsletters(officer_reports)
            st.success("✅ Newsletters generated successfully.")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        officer_names = namelist_df['name_self'].dropna().sort_values().unique().tolist()
        selected_officer = st.selectbox("Select an officer", ["-- Select --"] + officer_names)

        if selected_officer != "-- Select --":
            officer_row = namelist_df[namelist_df['name_self'] == selected_officer].iloc[0]
            try:
                officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df, period)
                officer_report["period"] = period
                render_newsletters([officer_report])
                st.success(f"✅ Newsletter generated for {selected_officer}.")
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
else:
    st.info("📄 Please upload all three required files to continue.")
