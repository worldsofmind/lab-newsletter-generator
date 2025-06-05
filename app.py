
import streamlit as st
from utils.data_loader import load_all_data
from utils.processor import process_all_officers, compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# --- SIDEBAR FILE UPLOADS ---
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

# --- PROCESS ---
if ratings_file and caseload_file and namelist_file:
    try:
        ratings_df, caseload_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file
        )

        # Select Officer
        officer_names = namelist_df["Name"].dropna().sort_values().unique().tolist()
        selected_officer = st.selectbox("Select Officer", ["All"] + officer_names)

        if st.button("Generate Newsletter"):
            if selected_officer == "All":
                reports = process_all_officers(ratings_df, caseload_df, namelist_df, period)
            else:
                officer_row = namelist_df[namelist_df["Name"] == selected_officer].iloc[0]
                try:
                    officer_report = compute_officer_stats(
                        officer_row, caseload_df, ratings_df, period, caseload_df
                    )
                    officer_report["period"] = period
                    reports = [officer_report]
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")
                    reports = []

            if reports:

import glob
import os

# Clean previously generated files
for old_file in glob.glob("generated/*.html") + glob.glob("generated/*.png"):
    os.remove(old_file)
                render_newsletters(reports)
                st.success("✅ Newsletters generated successfully.")

    st.markdown("### 📥 Download Newsletters")
    generated_files = glob.glob("generated/*.html") + glob.glob("generated/*.png")
    for file_path in generated_files:
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download {os.path.basename(file_path)}",
                data=f,
                file_name=os.path.basename(file_path),
                mime="application/octet-stream"
            )

    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")

import glob
import os

st.markdown("### 📥 Download Newsletters")
generated_files = glob.glob("generated/*.html") + glob.glob("generated/*.png")
for file_path in generated_files:
    with open(file_path, "rb") as f:
        st.download_button(
            label=f"Download {os.path.basename(file_path)}",
            data=f,
            file_name=os.path.basename(file_path),
            mime="application/octet-stream"
        )
