
import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔍 Debug: Caseload Columns", layout="centered")
st.title("🧪 Caseload Column Inspector")

uploaded_file = st.file_uploader("Upload your case_load.xlsx file", type=["xls", "xlsx"])

if uploaded_file:
    try:
        for skip in range(5, 15):
            st.subheader(f"skiprows={skip}")
            df = pd.read_excel(uploaded_file, skiprows=skip)
            st.write(df.columns.tolist())
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Please upload a case_load file to inspect its column headers.")
