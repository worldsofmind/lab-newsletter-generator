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

# ── MODE SELECTION ────────────────────────────────────────────────────────────────────────
mode = st.radio(
    "Choose an action:",
    options=["Generate Newsletters", "Batch Download"]
)

# ── BATCH DOWNLOAD MODE ──────────────────────────────────────────────────────────────────
if mode == "Batch Download":
    st.subheader("Batch Download Existing Newsletters")
    output_dir = Path("output")
    
    if not output_dir.exists() or not any(output_dir.glob("*.html")):
        st.info("No newsletters found in `./output/`. Please generate newsletters first.")
    else:
        # Create an in-memory ZIP of all .html files in output/
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for html_file in sorted(output_dir.glob("*.html")):
                zf.write(html_file, arcname=html_file.name)
        zip_buf.seek(0)

        st.download_button(
            label="Download All Newsletters as ZIP",
            data=zip_buf.read(),
            file_name="all_newsletters.zip",
            mime="application/zip"
        )

# ── GENERATE NEWSLETTERS MODE ────────────────────────────────────────────────────────────
else:
    st.subheader("Select Officers to Generate Newsletters")
    # ——— Sidebar: File Uploads —————————————————————————————————————————————————————————————
    with st.sidebar:
        st.header("📂 Upload Files")
        ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
        caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
        namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

        if not (ratings_file and caseload_file and namelist_file):
            st.warning("Please upload all three files to proceed.")

    # Only proceed if all three files are uploaded
    if ratings_file and caseload_file and namelist_file:
        # Try to load just the namelist to populate the multiselect
        try:
            _, _, namelist_df, _ = load_all_data(ratings_file, caseload_file, namelist_file)
        except Exception as e:
            st.error(f"❌ Failed to read files: {e}")
            st.stop()

        officer_names = namelist_df['name'].dropna().str.strip().tolist()
        selected_officers = st.multiselect(
            "Choose one or more officers (leave blank to select all):",
            options=officer_names
        )

        # Generate button
        if st.button("Generate Newsletters"):
            try:
                ratings_df, caseload_df, namelist_df, period = load_all_data(
                    ratings_file, caseload_file, namelist_file
                )

                # Determine which subset of officers to process
                if selected_officers:
                    filtered = namelist_df[namelist_df['name'].isin(selected_officers)]
                else:
                    filtered = namelist_df.copy()

                all_reports = []
                for _, officer_row in filtered.iterrows():
                    stats = compute_officer_stats(officer_row, caseload_df, ratings_df)
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
        st.info("Upload all three files (ratings.csv, case_load.csv, namelist.csv) to enable generation.")
