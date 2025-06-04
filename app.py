
import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers
from utils.render import render_newsletters

st.set_page_config(page_title="📬 LAB Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# Sidebar for file uploads
st.sidebar.header("Upload Required Files")
ratings_file = st.sidebar.file_uploader("Upload ratings.csv", type="csv")
caseload_file = st.sidebar.file_uploader("Upload case_load.xlsx", type=["xls", "xlsx"])
namelist_file = st.sidebar.file_uploader("Upload namelist.csv", type="csv")

if not all([ratings_file, caseload_file, namelist_file]):
    st.warning("Please upload all three required files.")
    st.stop()

with st.spinner("Processing data and generating newsletters..."):
    try:
        ratings_df, caseload_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file
        )
        st.success("Data loaded successfully.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    st.write("✅ Columns in caseload file:", caseload_df.columns.tolist())
    st.write("✅ Columns in namelist file:", namelist_df.columns.tolist())

    try:
        officer_reports = process_all_officers(
            ratings_df, caseload_df, namelist_df, period
        )
        st.success("Officer reports processed successfully.")
    except Exception as e:
        st.error(f"Error in processing officer reports: {e}")
        st.stop()

    try:
        render_newsletters(officer_reports, period)
        st.success("Newsletters generated successfully. Check the 'generated_reports' folder.")
    except Exception as e:
        st.error(f"Newsletter rendering failed: {e}")
