import streamlit as st
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

if ratings_file and caseload_file and namelist_file:
    try:
        ratings_df, caseload_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file
        )
        officer_names = sorted(namelist_df["name_self"].dropna().unique().tolist())

        selected_officer = st.selectbox("👤 Select officer to generate newsletter", ["-- Select --"] + officer_names)
        generate_all = st.checkbox("📢 Generate for all officers")

        if st.button("Generate Newsletter(s)"):
            with st.spinner("Generating newsletters..."):
                if generate_all:
                    officer_reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
                elif selected_officer != "-- Select --":
                    officer_row = namelist_df[namelist_df['name_self'] == selected_officer].iloc[0]
                    officer_reports = [compute_officer_stats(officer_row, caseload_df, ratings_df, period)]
                else:
                    st.warning("Please select an officer or choose to generate for all.")
                    st.stop()

                render_newsletters(officer_reports, period)
                st.success("✅ Newsletters generated successfully! Check the 'generated' folder.")
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
else:
    st.info("Please upload all three required files to begin.")
