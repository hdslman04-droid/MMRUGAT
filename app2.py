import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ============================
# SETTINGS
# ============================
MAX_CAPACITY = 252
MIN_CAPACITY = 188
ROWS = 6
MIN_ROW = 15
MAX_ROW = 20

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

LOGO_KPA = "KPA.png"
LOGO_ATM = "Logo ATM.png"
LOGO_UGAT = "Logo-UGAT.png"
CENTER_IMAGE = "FRONT PAAGE.png"

# ============================
# HOST PASSWORD
# ============================
DEFAULT_HOST_PASSWORD = "host123"

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

def verify_host_password(password_input):
    return password_input == DEFAULT_HOST_PASSWORD

def generate_seating_layout(total_capacity, high_table_capacity, remaining_capacity, people_per_row, rows_needed):
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.add_patch(patches.Rectangle((0, 5), 3, 1, linewidth=2, edgecolor='yellow', facecolor='yellow', label="High Table"))
    ax.text(1.5, 5.5, f"High Table ({high_table_capacity})", horizontalalignment='center', fontsize=12, color='black', weight='bold')

    for i in range(rows_needed):
        ax.add_patch(patches.Rectangle((0, 4-i), 3, 1, linewidth=2, edgecolor='yellow', facecolor='yellow'))
        ax.text(1.5, 4-i+0.5, f"Row {i+1} ({people_per_row})", horizontalalignment='center', fontsize=10, color='black', weight='bold')

    for i in range(rows_needed):
        for j in range(people_per_row):
            ax.add_patch(patches.Rectangle((j * 0.5, 4-i), 0.5, 0.7, linewidth=1, edgecolor='black', facecolor='white'))
            ax.text(j * 0.5 + 0.25, 4-i+0.3, f"Seat {j+1}", horizontalalignment='center', fontsize=8, color='black')

    ax.set_xlim(-1, 3)
    ax.set_ylim(-1, 6)
    ax.axis('off')
    ax.set_title(f"Seating Layout for {total_capacity} people", fontsize=16, weight="bold", color="yellow")

    return fig

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

high_table_capacity = st.slider("Adjust High Table Capacity", min_value=8, max_value=12, value=8)

# Calculate remaining capacity
remaining_capacity = MAX_CAPACITY - high_table_capacity  # Total capacity (252) is fixed

people_per_row = st.slider("People per Row", min_value=MIN_ROW, max_value=MAX_ROW, value=MIN_ROW)

# Calculate rows based on remaining capacity
rows_needed = max(remaining_capacity // people_per_row, 1)

# Calculate total capacity automatically
total_capacity = high_table_capacity + (people_per_row * rows_needed)

# Show results of seating configuration
st.write(f"High Table Capacity: {high_table_capacity} people")
st.write(f"Remaining Capacity: {remaining_capacity} people")
st.write(f"People per Row: {people_per_row}")
st.write(f"Number of Rows Required: {rows_needed}")
st.write(f"Total Capacity: {total_capacity} people")

# ============================
# DISPLAY SEATING LAYOUT
# ============================
fig = generate_seating_layout(total_capacity, high_table_capacity, remaining_capacity, people_per_row, rows_needed)
st.pyplot(fig)

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
else:
    st.info("Sila masukkan No Tentera untuk membuat carian.")

st.markdown("---")

# ============================
# HOST ONLY SECTION
# ============================
st.subheader("Host Access")

if not st.session_state.host_logged_in:
    host_password_input = st.text_input("Masukkan kata laluan host untuk lihat live attendance", type="password")

    if st.button("Login Host"):
        if verify_host_password(host_password_input):
            st.session_state.host_logged_in = True
            st.success("Login host berjaya.")
            st.rerun()
        else:
            st.error("Kata laluan host salah.")
else:
    st.success("Anda login sebagai host.")

    if st.button("Logout Host"):
        st.session_state.host_logged_in = False
        st.rerun()

    st.markdown("### 📋 Live Attendance / Kehadiran Semasa")

    if attendance_df.empty:
        st.warning("Belum ada rekod kehadiran.")
    else:
        st.dataframe(attendance_df, use_container_width=True)

        total_hadir = len(attendance_df)
        st.info(f"Jumlah Kehadiran Semasa: {total_hadir}")

        csv_data = attendance_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Muat Turun Rekod Kehadiran",
            data=csv_data,
            file_name="attendance_records.csv",
            mime="text/csv"
        )
