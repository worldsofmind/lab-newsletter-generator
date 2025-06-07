
import streamlit as st
from utils.data_loader import load_all_data
from utils.processor import compute_officer_stats
from utils.renderer import render_newsletters

st.title("LAB Officer Newsletter Generator")
st.write("Upload the Ratings, Caseload, and Namelist files to generate personalized newsletters for each officer.")

# File upload widgets
ratings_file = st.file_uploader("1. Upload Ratings CSV", type=["csv"])
caseload_file = st.file_uploader("2. Upload Caseload CSV/XLS(X)", type=["csv", "xls", "xlsx"])
namelist_file = st.file_uploader("3. Upload Namelist CSV", type=["csv"])

# Check that all files are uploaded
if ratings_file and caseload_file and namelist_file:
    try:
        # Load data and extract reporting period
        ratings_df, case_df, namelist_df, period = load_all_data(
            ratings_file, caseload_file, namelist_file
        )

        # Officer selection
        selected = st.multiselect(
            "Select Officers to Generate Newsletters",
            options=namelist_df['abbreviation'].tolist()
        )

        # Generate newsletters on button click
        if st.button("Generate Newsletters"):
            for abbr in selected:
                # Compute stats and render HTML
                row = namelist_df.loc[namelist_df['abbreviation'] == abbr].iloc[0]
                stats = compute_officer_stats(row, case_df, ratings_df, period)
                html = render_newsletters(stats)

                # Provide download button for each newsletter
                st.download_button(
                    label=f"Download {abbr}.html",
                    data=html,
                    file_name=f"{abbr}.html",
                    mime="text/html"
                )
    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")
else:
    st.info("Awaiting all three files: Ratings, Caseload, and Namelist.")
