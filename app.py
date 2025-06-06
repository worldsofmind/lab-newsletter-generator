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

    st.subheader("Select Officers to Generate Newsletters")
    officer_names = namelist_df['name'].dropna().str.strip().tolist()

    # Multiselect widget on the main page (scrollable list)
    selected_officers = st.multiselect(
        "Choose one or more officers (leave blank to select all):",
        options=officer_names,
        default=None
    )

    # Generate button appears after selection (or blank for all)
    if st.button("Generate Newsletters"):
        try:
            # Reload all data for computation
            ratings_df, caseload_df, namelist_df, period = load_all_data(
                ratings_file, caseload_file, namelist_file
            )

            # Determine which officers to process
            if selected_officers:
                filtered = namelist_df[namelist_df['name'].isin(selected_officers)]
            else:
                filtered = namelist_df.copy()

            all_reports = []
            for _, officer_row in filtered.iterrows():
                stats = compute_officer_stats(officer_row, caseload_df, ratings_df)
                all_reports.append(stats)

            # Render HTML files into output/<ABBR>.html
            output_dir = Path("output")
            # Clear previous outputs
            if output_dir.exists():
                for f in output_dir.iterdir():
                    if f.is_file() and f.suffix == ".html":
                        f.unlink()
            render_newsletters(all_reports, output_dir)

            st.success("Newsletters generated successfully!")
            st.markdown("### Download Individual Newsletters:")

            # Individual download buttons
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

            # “Download All” ZIP button
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                for report in all_reports:
                    abbr = report['abbreviation']
                    html_path = output_dir / f"{abbr}.html"
                    if html_path.exists():
                        zf.write(html_path, arcname=f"{abbr}.html")
            zip_buffer.seek(0)

            st.download_button(
                label="Download All as ZIP",
                data=zip_buffer.read(),
                file_name="all_newsletters.zip",
                mime="application/zip",
                key="download_all_zip"
            )

        except Exception as e:
            st.error(f"❌ An error occurred during processing: {e}")
