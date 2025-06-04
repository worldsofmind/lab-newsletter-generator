import streamlit as st
import pandas as pd
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# Sidebar: File uploads
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.xlsx`", type=["xls", "xlsx"])
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

# Main UI logic
if not ratings_file or not caseload_file or not namelist_file:
    st.warning("Please upload all required files to proceed.")
    st.stop()

ratings_df, caseload_df, namelist_df, period = load_all_data(
    ratings_file, caseload_file, namelist_file
)

generate_all = st.checkbox("Generate for all officers")
selected_officer = None

if not generate_all:
    selected_officer = st.selectbox(
        "Select officer to generate newsletter for:",
        ["-- Select --"] + namelist_df["name_self"].dropna().unique().tolist(),
    )

if st.button("Generate Newsletter"):
    try:
        if generate_all:
            officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
        elif selected_officer and selected_officer != "-- Select --":
            officer_row = namelist_df[namelist_df["name_self"] == selected_officer].iloc[0]
            officer_reports = [compute_officer_stats(officer_row, caseload_df, ratings_df, period)]
        else:
            st.warning("Please select an officer or choose to generate for all.")
            st.stop()

        render_newsletters(officer_reports)
        st.success("✅ Newsletters generated successfully. Check the 'generated' folder.")
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
