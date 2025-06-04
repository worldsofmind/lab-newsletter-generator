import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.render import render_newsletters

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# Sidebar for uploads
st.sidebar.header("📂 Upload Files")
ratings_file = st.sidebar.file_uploader("Upload ratings.csv", type="csv")
caseload_file = st.sidebar.file_uploader("Upload case_load.xlsx", type=["xls", "xlsx"])
namelist_file = st.sidebar.file_uploader("Upload namelist.csv", type="csv")

# Checkbox for batch or individual
generate_all = st.sidebar.checkbox("🔁 Generate for All Officers", value=True)
selected_officer = None

if not generate_all:
    selected_officer = st.sidebar.selectbox("👤 Select Officer", ["-- Select --"])

if ratings_file and caseload_file and namelist_file:
    with st.spinner("Processing data..."):
        ratings_df, caseload_df, namelist_df, period = load_all_data(ratings_file, caseload_file, namelist_file)

    if generate_all:
        officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
    elif selected_officer != "-- Select --":
        officer_row = namelist_df[namelist_df["name_self"] == selected_officer].iloc[0]
        officer_reports = [compute_officer_stats(officer_row, caseload_df, ratings_df, period)]
    else:
        st.warning("Please select an officer or choose to generate all.")
        st.stop()

    render_newsletters(officer_reports, period)
    st.success("Newsletters generated successfully. Check the 'generated' folder.")
else:
    st.info("Please upload all required files.")
