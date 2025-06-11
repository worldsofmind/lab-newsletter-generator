
import streamlit as st
import pandas as pd
import os
import io
import zipfile
from pathlib import Path

from utils.data_loader import load_all_data
from utils.processor import compute_officer_stats
from utils.renderer import render_newsletters

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="wide")
st.title("📬 LAB Officer Newsletter Generator")

# ——— Sidebar: File Uploads —————————————————————————————————————————————————————————————————

with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

    if not (ratings_file and caseload_file and namelist_file):
        st.warning("Please upload all three files to proceed.")

# ——— Main Area: Officer Selection & Generation ——————————————————————————————————————————————————

if ratings_file and caseload_file and namelist_file:
    # Attempt to load namelist to populate multiselect
    try:
        _, _, namelist_df, _ = load_all_data(ratings_file, caseload_file, namelist_file)
    except Exception as e:
        st.error(f"❌ Failed to read files: {e}")
        st.stop()

    st.subheader("Filter and Select Officers to Generate Newsletters")

    # Dropdown to filter by function
    function_filter = st.selectbox(
        "Filter by Function:",
        options=["All", "LO", "LE"],
        index=0
    )

    # Filter namelist_df by selected function
    if function_filter != "All":
        filtered_namelist = namelist_df[namelist_df['function'].str.upper() == function_filter]
    else:
        filtered_namelist = namelist_df

    officer_names = filtered_namelist['name'].dropna().str.strip().tolist()

    # Multiselect widget on the main page (scrollable list)
    selected_officers = st.multiselect(
        "Choose one or more officers (leave blank to select all):",
        options=officer_names
    )

    # Generate button
    if st.button("Generate Newsletters"):
        try:
            # Reload all data for computation
            ratings_df, caseload_df, namelist_df, period = load_all_data(
                ratings_file, caseload_file, namelist_file
            )

            # Apply same function filtering after reload
            if function_filter != "All":
                namelist_df = namelist_df[namelist_df['function'].str.upper() == function_filter]

            # Determine which subset of officers to process
            if selected_officers:
                filtered = namelist_df[namelist_df['name'].isin(selected_officers)]
            else:
                filtered = namelist_df.copy()

            all_reports = []
            for _, officer_row in filtered.iterrows():
                stats = compute_officer_stats(officer_row, caseload_df, ratings_df, period)
                all_reports.append(stats)

            # Render each officer's HTML into output/<ABBR>.html
            output_dir = Path("output")
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            else:
                # Clear out any existing .html files to avoid stale downloads
                for f in output_dir.glob("*.html"):
                    f.unlink()

            render_newsletters(all_reports, output_dir)

            st.success("Newsletters generated successfully!")
            st.markdown("### Download Individual Newsletters:")

            # Show a download button per officer
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
                        mime="text/html",
                        key=f"download_{abbr}"
                    )
                else:
                    st.error(f"Missing expected file: {file_path}")

        except Exception as e:
            st.error(f"❌ An error occurred during processing: {e}")
    else:
        st.info("After selecting officers, click 'Generate Newsletters' to create and download.")

else:
    st.info("Upload all three files (ratings.csv, case_load.csv, namelist.csv) to enable generation.")
