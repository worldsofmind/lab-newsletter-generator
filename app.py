import streamlit as st
import pandas as pd
import datetime
from utils.data_loader import load_all_data
from utils.processor import compute_officer_stats
from utils.renderer import render_newsletters
import os
from pathlib import Path
import zipfile
import io

st.set_page_config(page_title="LAB Officer Newsletter Generator", layout="centered")
st.title("📬 LAB Officer Newsletter Generator")

# --- SIDEBAR FILE UPLOADS ---
with st.sidebar:
    st.header("📂 Upload Files")
    ratings_file = st.file_uploader("Upload `ratings.csv`", type="csv")
    caseload_file = st.file_uploader("Upload `case_load.csv`", type="csv")
    namelist_file = st.file_uploader("Upload `namelist.csv`", type="csv")

# --- MAIN LOGIC ---
if ratings_file and caseload_file and namelist_file:
    try:
        with st.spinner("Loading data and preparing officer list..."):
            ratings_df, caseload_df, namelist_df, period = load_all_data(ratings_file, caseload_file, namelist_file)

        # Get unique officer names for selection
        officer_names = namelist_df['name'].tolist()
        
        # Add a multiselect box to allow users to choose officers
        selected_officers = st.multiselect(
            "Select Officer(s) to Generate Newsletters For:",
            options=officer_names,
            default=officer_names # By default, all officers are selected
        )

        # Only proceed if officers are selected
        if selected_officers:
            # The "Generate Newsletters" button is back!
            if st.button("Generate Newsletters"):
                with st.spinner(f"Generating newsletters for {len(selected_officers)} officer(s)..."):
                    # Filter namelist_df based on selected officers
                    filtered_namelist_df = namelist_df[namelist_df['name'].isin(selected_officers)]

                    all_reports = []
                    for _, officer_row in filtered_namelist_df.iterrows(): # Loop through filtered officers
                        officer_report = compute_officer_stats(officer_row, caseload_df, ratings_df)
                        all_reports.append(officer_report)

                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    render_newsletters(all_reports, output_dir)

                st.success("✅ Newsletters generated successfully. Ready for download.")

                # --- Individual Downloads ---
                st.subheader("Download Individual Newsletters:")
                for report in all_reports:
                    name = report['name']
                    abbreviation = report['abbreviation']
                    file_path = output_dir / f"{abbreviation}_Newsletter.html"
                    if file_path.exists():
                        with open(file_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        st.download_button(
                            label=f"📩 Download {abbreviation}_Newsletter.html",
                            data=html_content,
                            file_name=f"{abbreviation}_Newsletter.html",
                            mime="text/html",
                            key=f"download_single_{abbreviation}" # Unique key for each button
                        )
                
                # --- Batch Download ---
                st.subheader("Download All Generated Newsletters:")
                if all_reports: # Only show batch download if reports were generated
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
                        for report in all_reports:
                            abbreviation = report['abbreviation']
                            file_name = f"{abbreviation}_Newsletter.html"
                            file_path = output_dir / file_name
                            if file_path.exists():
                                zf.write(file_path, arcname=file_name) # Add file to zip with its original name
                    zip_buffer.seek(0)

                    st.download_button(
                        label="📦 Download All Generated Newsletters as ZIP",
                        data=zip_buffer.getvalue(),
                        file_name="selected_newsletters.zip", # Renamed to reflect selection
                        mime="application/zip"
                    )
        else:
            st.info("Please select at least one officer to generate newsletters.")
            
    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")
else:
    st.info("📥 Please upload all three files to begin.")
