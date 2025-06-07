import streamlit as st
from utils.data_loader import load_all_data
from utils.processor   import compute_officer_stats
from utils.renderer    import render_newsletters

# ... file-upload UI omitted for brevity ...

if all_files_uploaded:
    ratings_df, case_df, namelist_df, period = load_all_data(
        ratings_file,
        caseload_file,
        namelist_file
    )

    # Allow user to pick which officers to generate
    selected = st.multiselect("Officers", namelist_df['abbreviation'].tolist())

    if st.button("Generate Newsletters"):
        try:
            # render each selected officer
            for abbr in selected:
                row  = namelist_df.loc[namelist_df['abbreviation'] == abbr].iloc[0]
                stats = compute_officer_stats(row, case_df, ratings_df, period)
                html = render_newsletters(stats)

                st.download_button(
                    label=f"Download {abbr}.html",
                    data=html,
                    file_name=f"{abbr}.html",
                    mime="text/html",
                )
        except Exception as e:
            st.error(f"❌ An error occurred during processing: {e}")
