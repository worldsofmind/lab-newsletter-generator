import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Make sure these imports match your project structure:
from utils.data_loader import load_all_data
from utils.processor import compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# ——— Sidebar: File Uploads —————————————————————————————————————————————————————————————————

with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

    # Only enable “Generate” once all three files are provided
    if not (ratings_file and caseload_file and namelist_file):
        st.warning("Please upload all three files to proceed.")

# ——— Main: Generate Newsletters —————————————————————————————————————————————————————————————————

if ratings_file and caseload_file and namelist_file:
    # Button to trigger the generation process
    if st.button("Generate Newsletters"):
        try:
            # 1) Load all data (will extract period from caseload_file)
            ratings_df, caseload_df, namelist_df, period = load_all_data(
                ratings_file, caseload_file, namelist_file
            )

            # 2) Compute stats for each officer in namelist_df
            all_reports = []
            # Optionally, allow selecting a subset of officers via multiselect:
            officer_names = namelist_df['name'].dropna().str.strip().tolist()
            selected_officers = st.multiselect(
                "Select officers (leave blank for all):",
                options=officer_names
            )
            if selected_officers:
                filtered = namelist_df[namelist_df['name'].isin(selected_officers)]
            else:
                filtered = namelist_df.copy()

            for _, officer_row in filtered.iterrows():
                stats = compute_officer_stats(officer_row, caseload_df, ratings_df)
                all_reports.append(stats)

            # 3) Render each individual HTML into output/<ABBREVIATION>.html
            output_dir = Path("output")
            render_newsletters(all_reports, output_dir)

            st.success("Newsletters generated successfully!")
            st.markdown("### Download Individual Newsletters:")

            # 4) Show one download button per officer
            #    (Reads the generated HTML from disk and makes it downloadable)
            for report in all_reports:
                abbr = report['abbreviation']
                file_path = output_dir / f"{abbr}.html"
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        data = f.read()
                    st.download_button(
                        label=f"Download {abbr}.html",
                        data=data,
                        file_name=f"{abbr}.html",
                        mime="text/html"
                    )
                else:
                    st.error(f"Expected output file not found: {file_path}")

        except Exception as e:
            st.error(f"❌ An error occurred during processing: {e}")
