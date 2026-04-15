import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)",
    page_icon="TDM.png",  # Use custom icon (optional)
    layout="centered"
)

# ============================
# FILE PATHS
# ============================
DATA_FILE = "SEATING_PLAN.csv"
ATTENDANCE_FILE = "attendance_records.csv"

# ============================
# SEATING CONFIGURATION
# ============================
MAX_CAPACITY = 252
MIN_CAPACITY = 188
ROWS = 6
MIN_ROW = 15
MAX_ROW = 20

# ============================
# HELPER FUNCTIONS
# ============================
def get_kl_time():
    kl_now = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    return kl_now.strftime("%d/%m/%Y %I:%M:%S %p")

def load_data():
    file_path = Path(DATA_FILE)
    if not file_path.exists():
        st.error(f"Fail '{DATA_FILE}' tidak dijumpai.")
        st.stop()
    df_raw = pd.read_csv(file_path, encoding="cp1252", header=None)
    headers = df_raw.iloc[2].tolist()
    df = df_raw.iloc[3:].copy()
    df.columns = headers
    df = df.dropna(how="all").reset_index(drop=True)
    df.columns = [str(col).strip() for col in df.columns]
    return df

def load_attendance():
    file_path = Path(ATTENDANCE_FILE)
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["NO TEN", "NAMA PENUH", "PKT", "PASUKAN", "JAWATAN", "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN", "STATUS_KEHADIRAN", "TARIKH_MASA"])

def save_attendance(attendance_df):
    attendance_df.to_csv(ATTENDANCE_FILE, index=False)

def show_image_if_exists(image_path, width=None, use_container_width=False):
    path = Path(image_path)
    if path.exists():
        st.image(str(path), width=width, use_container_width=use_container_width)

# ============================
# UI COMPONENTS
# ============================
st.markdown("<h1 style='text-align: center;'>🪖 Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Masukkan No Tentera untuk semak maklumat pegawai dan tandakan kehadiran.</p>", unsafe_allow_html=True)
st.markdown(f"**Masa Terkini Kuala Lumpur, Malaysia:** {get_kl_time()}", unsafe_allow_html=True)

# ============================
# SEATING CAPACITY ADJUSTMENT
# ============================
st.subheader("Adjust Seating Capacity")

total_capacity = st.slider("Adjust Total Capacity", min_value=MIN_CAPACITY, max_value=MAX_CAPACITY, value=MAX_CAPACITY)
high_table_capacity = st.slider("Adjust High Table Capacity", min_value=8, max_value=12, value=8)

# Calculate remaining capacity
remaining_capacity = total_capacity - high_table_capacity
people_per_row = st.slider("People per Row", min_value=MIN_ROW, max_value=MAX_ROW, value=MIN_ROW)

# Calculate rows based on remaining capacity
rows_needed = max(remaining_capacity // people_per_row, 1)

# Show results of seating configuration
st.write(f"High Table Capacity: {high_table_capacity} people")
st.write(f"Remaining Capacity: {remaining_capacity} people")
st.write(f"People per Row: {people_per_row}")
st.write(f"Number of Rows Required: {rows_needed}")

# ============================
# SEARCH SECTION (For Attendance)
# ============================
search_no = st.text_input("Masukkan No Tentera")

df = load_data()
attendance_df = load_attendance()

if search_no:
    result_df = df[df["NO TEN"].str.contains(search_no.strip(), case=False, na=False)].copy()

    if result_df.empty:
        st.warning("Tiada rekod dijumpai untuk nombor tentera tersebut.")
    else:
        st.success(f"{len(result_df)} rekod dijumpai.")
        for idx, row in result_df.iterrows():
            no_ten = row["NO TEN"]
            st.write(f"**Nama:** {row['NAMA PENUH']}")
            st.write(f"**No Tentera:** {row['NO TEN']}")
            st.write(f"**Pangkat:** {row['PKT']}")
            st.write(f"**Menu:** {row['MENU']}")
            st.write(f"**Pasangan:** {row['PASANGAN']}")
            st.write(f"**Menu Pasangan:** {row['MENU PASANGAN']}")

            # Kehadiran Status
            if st.button(f"Tandakan Kehadiran {row['NAMA PENUH']}", key=f"submit_{idx}_{no_ten}"):
                new_record = pd.DataFrame([{
                    "NO TEN": row["NO TEN"],
                    "NAMA PENUH": row["NAMA PENUH"],
                    "PKT": row["PKT"],
                    "PASUKAN": row["PASUKAN"],
                    "JAWATAN": row["JAWATAN"],
                    "MENU": row["MENU"],
                    "PASANGAN": row["PASANGAN"],
                    "MENU PASANGAN": row["MENU PASANGAN"],
                    "CATATAN": row["CATATAN"],
                    "STATUS_KEHADIRAN": "HADIR",
                    "TARIKH_MASA": datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime("%Y-%m-%d %H:%M:%S")
                }])
                attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
                save_attendance(attendance_df)
                st.success(f"Kehadiran bagi {row['NAMA PENUH']} berjaya direkodkan.")
                st.rerun()
