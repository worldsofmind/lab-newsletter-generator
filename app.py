
import streamlit as st
from utils.data_loader import load_all_data
from utils.processor import process_all_officers
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

st.sidebar.header("📂 Upload Files")
ratings_file = st.sidebar.file_uploader("Upload `ratings.csv`", type="csv")
caseload_file = st.sidebar.file_uploader("Upload `case_load.xlsx`", type=["xls", "xlsx"])
namelist_file = st.sidebar.file_uploader("Upload `namelist.csv`", type="csv")

if not ratings_file or not caseload_file or not namelist_file:
    st.error("Please upload all required files.")
else:
    with st.spinner("Processing data and generating newsletters..."):
        ratings_df, caseload_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file)
        officer_reports = process_all_officers(
            ratings_df, caseload_df, namelist_df, period)
        render_newsletters(officer_reports, period)
    st.success("Newsletters generated successfully. Check the 'generated' folder.")
