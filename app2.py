import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="Sistem Kehadiran Majlis Makan Malam Regimental KPA (GAJI)",
    page_icon="TDM.png",  # Use custom icon (optional)
    layout="centered"
)

# ============================
# FILE PATHS
# ============================
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

def load_data_from_files(files):
    """Load data from multiple files into a single DataFrame."""
    all_data = []
    for file in files:
        df = pd.read_csv(file)
        all_data.append(df)
    
    # Concatenate all data into a single DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def load_attendance():
    """Load attendance records from a CSV file."""
    file_path = Path(ATTENDANCE_FILE)
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["NO TEN", "NAMA PENUH", "PKT", "PASUKAN", "JAWATAN", "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN", "STATUS_KEHADIRAN", "TARIKH_MASA"])

def save_attendance(attendance_df):
    """Save the updated attendance data to a CSV file."""
    attendance_df.to_csv(ATTENDANCE_FILE, index=False)

def show_image_if_exists(image_path, width=None, use_container_width=False):
    """Display image if it exists."""
    path = Path(image_path)
    if path.exists():
        st.image(str(path), width=width, use_container_width=use_container_width)

def verify_host_password(password_input):
    """Verify host password."""
    return password_input == DEFAULT_HOST_PASSWORD

# ============================
# SESSION STATE
# ============================
if "host_logged_in" not in st.session_state:
    st.session_state.host_logged_in = False

# ============================
# UI COMPONENTS
# ============================
st.markdown("<h1 style='text-align: center;'>🪖 Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Masukkan No Tentera untuk semak maklumat pegawai dan tandakan kehadiran.</p>", unsafe_allow_html=True)
st.markdown(f"**Masa Terkini Kuala Lumpur, Malaysia:** {get_kl_time()}", unsafe_allow_html=True)

# ============================
# MULTIPLE FILE UPLOAD
# ============================
uploaded_files = st.file_uploader("Upload CSV Files", accept_multiple_files=True, type=["csv"])

if uploaded_files:
    st.write(f"Total {len(uploaded_files)} file(s) uploaded.")
    combined_data = load_data_from_files(uploaded_files)
    st.dataframe(combined_data)
else:
    st.info("Please upload at least one CSV file.")

# ============================
# SEARCH SECTION (For Attendance)
# ============================
search_no = st.text_input("Masukkan No Tentera")

df = combined_data if uploaded_files else pd.DataFrame()
attendance_df = load_attendance()

if search_no and not df.empty:
    result_df = df[df["NO TEN"].str.contains(search_no.strip(), case=False, na=False)].copy()

    if result_df.empty:
        st.warning("Tiada rekod dijumpai untuk nombor tentera tersebut.")
        if st.button("Re-enter No Tentera"):
            st.experimental_rerun()
    else:
        st.success(f"{len(result_df)} rekod dijumpai.")
        for idx, row in result_df.iterrows():
            no_ten = str(row["NO TEN"]).strip()
            st.write(f"**Nama:** {row['NAMA PENUH']}")
            st.write(f"**No Tentera:** {row['NO TEN']}")
            st.write(f"**Pangkat:** {row['PKT']}")
            st.write(f"**Menu:** {row['MENU']}")
            st.write(f"**Pasangan:** {row['PASANGAN']}")
            st.write(f"**Menu Pasangan:** {row['MENU PASANGAN']}")

            # Kehadiran Status
            if st.button(f"Tandakan Kehadiran {row['NAMA PENUH']}", key=f"submit_{idx}_{no_ten}"):
                if no_ten in attendance_df["NO TEN"].astype(str).values:
                    st.warning("Attendance already submitted!")
                else:
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
                    st.experimental_rerun()
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
            st.experimental_rerun()
        else:
            st.error("Kata laluan host salah.")
else:
    st.success("Anda login sebagai host.")

    if st.button("Logout Host"):
        st.session_state.host_logged_in = False
        st.experimental_rerun()

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
