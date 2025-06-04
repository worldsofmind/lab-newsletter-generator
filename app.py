
import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# Sidebar for file uploads only
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.xlsx`", type=["xls", "xlsx"])
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

if not ratings_file or not caseload_file or not namelist_file:
    st.warning("Please upload all required files.")
    st.stop()

ratings_df, caseload_df, namelist_df, period = load_all_data(ratings_file, caseload_file, namelist_file)

st.markdown("### Select Officer to Generate Newsletter")

officer_names = namelist_df["name_self"].dropna().unique().tolist()
officer_names.insert(0, "-- Select --")
selected_officer = st.selectbox("Select an officer:", officer_names)

generate_all = st.checkbox("Generate for all officers")

if st.button("Generate Newsletter(s)"):
    with st.spinner("Generating newsletters..."):
        if generate_all:
            officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
        else:
            if selected_officer == "-- Select --":
                st.error("Please select an officer or check 'Generate for all officers'.")
                st.stop()
            officer_row = namelist_df[namelist_df["name_self"] == selected_officer].iloc[0]
            officer_reports = [compute_officer_stats(officer_row, caseload_df, ratings_df, period)]
        render_newsletters(officer_reports, period)
    st.success("Newsletters generated successfully. Check the 'generated' folder.")
