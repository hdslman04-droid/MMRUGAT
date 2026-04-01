import pandas as pd
import streamlit as st

# ==========================
# CONFIGURATION
# ==========================
st.set_page_config(
    page_title="Sistem Pencarian Nombor Tentera - Majlis Makan Malam Regimental KPA (UGAT)",
    page_icon="🪖",
    layout="wide"
)

st.title("🪖 Majlis Makan Malam Regimental KPA (UGAT)")
st.caption("Cari maklumat tentera berdasarkan nama atau nombor tentera, termasuk tempat duduk dan kedudukan meja.")

# ==========================
# PRELOAD THE SEATING PLAN (hard-coded or static file)
# ==========================
# Assuming the file is located in the same directory or GitHub repository
# Change this path to where the file is located on your GitHub or static location

file_path = 'SEATING PLAN.xlsx'  # File path in your repository

# Load the seating data directly from the file
seating_df = pd.read_excel(file_path, engine='openpyxl')

# ==========================
# Display the seating data (for verification)
# ==========================
st.write("### Seating Plan Data", seating_df.head())

# ==========================
# SEARCH BY NAME OR MILITARY NO
# ==========================
search_option = st.sidebar.radio(
    "Search by", ["Nama", "No Tentera"]
)

search_term = st.text_input(f"Enter {search_option}")

if search_term:
    if search_option == "Nama":
        # Search by name (case insensitive)
        result_df = seating_df[seating_df["Nama"].str.contains(search_term, case=False, na=False)]
    elif search_option == "No Tentera":
        # Search by military number (case insensitive)
        result_df = seating_df[seating_df["No Tentera"].str.contains(search_term, case=False, na=False)]

    if result_df.empty:
        st.warning("No match found.")
    else:
        st.write(f"### Found {len(result_df)} results for {search_term}:")
        st.write(result_df[["Nama", "No Tentera", "Menu", "Kerusi", "Meja"]])

        # Option to download the result data
        st.download_button(
            label="Download Seating Information",
            data=result_df.to_csv(index=False).encode('utf-8'),
            file_name="seating_info.csv",
            mime="text/csv"
        )
else:
    st.info("Sila masukkan nama atau nombor tentera untuk mencari.")
