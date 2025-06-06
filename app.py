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

# ── Sidebar: File Uploads ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

    if not (ratings_file and caseload_file and namelist_file):
        st.warning("Please upload all three files to proceed.")

# ── Main: Officer Selection & Generation ─────────────────────────────────────────────────
if ratings_file and caseload_file and namelist_file:
    # Attempt to load namelist to populate multiselect
    try:
        _, _, namelist_df, _ = load_all_data(ratings_file, caseload_file, namelist_file)
    except Exception as e:
        st.error(f"❌ Failed to read files: {e}")
        st.stop()

    st.subheader("Select Officers to Generate Newsletters")
    officer_names = namelist_df['name'].dropna().str.strip().tolist()

    selected_officers = st.multiselect(
        "Choose one or more officers (leave blank to select all):",
        options=officer_names
    )

    if st.button("Generate Newsletters"):
        try:
            # Reload everything for computation
            ratings_df, caseload_df, namelist_df, period = load_all_data(
                ratings_file, caseload_file, namelist_file
            )

            # Determine which subset to process
            if selected_officers:
                filtered = namelist_df[namelist_df['name'].isin(selected_officers)]
            else:
                filtered = namelist_df.copy()

            all_reports = []
            for _, officer_row in filtered.iterrows():
                stats = compute_officer_stats(officer_row, caseload_df, ratings_df)
                all_reports.append(stats)

            # Render HTML + PDF + PNG
            output_dir = Path("output")
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            else:
                for f in output_dir.glob("*"):
                    f.unlink()
            render_newsletters(all_reports, output_dir)

            st.success("Newsletters generated successfully!")
            st.markdown("### Download Individual Newsletters:")

            # For each officer, provide three download buttons
            for report in all_reports:
                abbr = report['abbreviation']

                # 1) HTML
                html_path = output_dir / f"{abbr}.html"
                if html_path.exists():
                    with open(html_path, "rb") as f_html:
                        html_data = f_html.read()
                    st.download_button(
                        label=f"Download {abbr}.html",
                        data=html_data,
                        file_name=f"{abbr}.html",
                        mime="text/html",
                        key=f"download_html_{abbr}"
                    )

                # 2) PDF
                pdf_path = output_dir / f"{abbr}.pdf"
                if pdf_path.exists():
                    with open(pdf_path, "rb") as f_pdf:
                        pdf_data = f_pdf.read()
                    st.download_button(
                        label=f"Download {abbr}.pdf",
                        data=pdf_data,
                        file_name=f"{abbr}.pdf",
                        mime="application/pdf",
                        key=f"download_pdf_{abbr}"
                    )

                # 3) PNG
                png_path = output_dir / f"{abbr}.png"
                if png_path.exists():
                    with open(png_path, "rb") as f_png:
                        png_data = f_png.read()
                    st.download_button(
                        label=f"Download {abbr}.png",
                        data=png_data,
                        file_name=f"{abbr}.png",
                        mime="image/png",
                        key=f"download_png_{abbr}"
                    )

        except Exception as e:
            st.error(f"❌ An error occurred during processing: {e}")
    else:
        st.info("After selecting officers, click 'Generate Newsletters' to create and download.")

else:
    st.info("Upload all three files (ratings.csv, case_load.csv, namelist.csv) to enable generation.")
