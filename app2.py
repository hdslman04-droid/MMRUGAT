import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import base64

st.set_page_config(
    page_title="MMR KPA (GAJI)",
    page_icon="TDM.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "host_logged_in" not in st.session_state:
    st.session_state.host_logged_in = False

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 900px;
}

.time-box {
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    padding: 10px;
    border-radius: 10px;
    background-color: #f3f4f6;
    margin-top: 14px;
    margin-bottom: 18px;
    color: black;
}

.center-caption {
    text-align: center;
    margin-bottom: 20px;
    color: #555;
}

div[data-testid="stTextInput"] {
    max-width: 420px;
}

@media (max-width: 640px) {
    .block-container {
        padding-top: 0.5rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "SEATING PLAN MMR PENGHARGAAN 2026 2.csv"
ATTENDANCE_FILE = "attendance_records.csv"

LOGO_UGAT = "Logo-UGAT.png"
CENTER_IMAGE = "LAYOUT SUSUNAN.png"

DEFAULT_HOST_PASSWORD = "host123"

required_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]


def get_file_updated_time():
    files_to_check = [DATA_FILE, ATTENDANCE_FILE]
    existing_files = [Path(f) for f in files_to_check if Path(f).exists()]

    if not existing_files:
        return "Tiada rekod"

    latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
    latest_time = datetime.fromtimestamp(
        latest_file.stat().st_mtime,
        ZoneInfo("Asia/Kuala_Lumpur")
    )

    return latest_time.strftime("%d/%m/%Y %I:%M:%S %p")


def clean_csv(df_raw):
    if "BIL" not in df_raw.columns:
        headers = df_raw.iloc[0].tolist()
        df = df_raw.iloc[1:].copy()
        df.columns = headers
    else:
        df = df_raw.copy()

    df = df.dropna(how="all").reset_index(drop=True)
    df.columns = [str(col).strip() for col in df.columns]

    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


@st.cache_data
def load_default_data():
    file_path = Path(DATA_FILE)

    if not file_path.exists():
        st.error(f"Fail '{DATA_FILE}' tidak dijumpai.")
        st.stop()

    df_raw = pd.read_csv(file_path, encoding="utf-8")
    return clean_csv(df_raw)


def load_uploaded_files(uploaded_files):
    all_data = []

    for uploaded_file in uploaded_files:
        df_raw = pd.read_csv(uploaded_file, encoding="utf-8")
        df = clean_csv(df_raw)
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)


def load_attendance():
    file_path = Path(ATTENDANCE_FILE)

    if file_path.exists():
        try:
            attendance_df = pd.read_csv(file_path)
            attendance_df.columns = [str(col).strip() for col in attendance_df.columns]

            for col in attendance_df.columns:
                attendance_df[col] = attendance_df[col].astype(str).str.strip()

            return attendance_df
        except Exception:
            pass

    return pd.DataFrame(columns=[
        "BIL", "NOTEN", "NAMA", "MENU", "MEJA",
        "STATUS_KEHADIRAN", "TARIKH_MASA"
    ])


def save_attendance(attendance_df):
    attendance_df.to_csv(ATTENDANCE_FILE, index=False)


def show_image_if_exists(image_path, width=None, use_container_width=False):
    path = Path(image_path)

    if path.exists():
        st.image(str(path), width=width, use_container_width=use_container_width)


def verify_host_password(password_input):
    try:
        real_password = st.secrets["HOST_PASSWORD"]
    except Exception:
        real_password = DEFAULT_HOST_PASSWORD

    return password_input == real_password


def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================================================
# SIDEBAR HOST LOGIN + UPLOAD
# =========================================================
if st.session_state.host_logged_in:
    st.sidebar.title("Host Panel")
    st.sidebar.success("Anda login sebagai host.")

    uploaded_files = st.sidebar.file_uploader(
        "Upload CSV Files",
        accept_multiple_files=True,
        type=["csv"]
    )

    if uploaded_files:
        try:
            st.session_state.uploaded_df = load_uploaded_files(uploaded_files)
            st.sidebar.success(f"{len(uploaded_files)} fail berjaya dimuat naik.")
        except Exception as e:
            st.sidebar.error(f"Fail tidak dapat dibaca: {e}")

    if st.sidebar.button("Logout Host"):
        st.session_state.host_logged_in = False
        st.session_state.uploaded_df = None
        st.rerun()

else:
    st.sidebar.title("Host Login")

    host_password_input = st.sidebar.text_input(
        "Masukkan kata laluan",
        type="password"
    )

    if st.sidebar.button("Login"):
        if verify_host_password(host_password_input):
            st.session_state.host_logged_in = True
            st.sidebar.success("Login berjaya.")
            st.rerun()
        else:
            st.sidebar.error("Kata laluan salah.")


# =========================================================
# LOAD DATA
# =========================================================
if st.session_state.uploaded_df is not None:
    df = st.session_state.uploaded_df
else:
    df = load_default_data()

attendance_df = load_attendance()

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Kolum berikut tiada dalam fail CSV: {missing_cols}")
    st.stop()


# =========================================================
# BANNER HEADER
# =========================================================
img_base64 = get_base64_image(LOGO_UGAT)

st.markdown(f"""
<div style="
    display:flex;
    align-items:center;
    gap:12px;
    background: linear-gradient(90deg, #020617, #111827);
    padding:15px;
    border-radius:15px;
    margin-bottom:15px;
">
    <img src="data:image/png;base64,{img_base64}" width="50">
    <h2 style="margin:0; color:white;">
        Sistem Kehadiran Majlis Makan Malam Regimental KPA (GAJI)
    </h2>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SEARCH SECTION
# =========================================================
st.markdown(
    "<h3 style='color:#38bdf8;'>Carian Nombor Tentera</h3>",
    unsafe_allow_html=True
)

search_no = st.text_input(
    "Masukkan No Tentera",
    max_chars=10,
    placeholder="Contoh: 3004463"
)

if search_no:
    result_df = df[df["NOTEN"].str.contains(search_no.strip(), case=False, na=False)].copy()

    if result_df.empty:
        st.warning("Tiada rekod dijumpai untuk nombor tentera tersebut.")
    else:
        bil_value = result_df.iloc[0]["BIL"]
        group_df = df[df["BIL"] == bil_value].copy()

        st.success(f"Rekod dijumpai. BIL: {bil_value}")

        st.markdown("### Maklumat Kehadiran")

        display_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]

        if "CATATAN" in group_df.columns:
            display_cols.append("CATATAN")

        st.table(group_df[display_cols])

        st.markdown("### Pelan Kedudukan Dewan")
        show_image_if_exists(CENTER_IMAGE, use_container_width=True)

        st.markdown(
            f"<div class='time-box'>Last Updated: {get_file_updated_time()}</div>",
            unsafe_allow_html=True
        )

        sudah_hadir_semua = True

        for idx, row in group_df.iterrows():
            noten = str(row["NOTEN"]).strip()

            sudah_hadir = False

            if not attendance_df.empty and "NOTEN" in attendance_df.columns:
                sudah_hadir = noten in attendance_df["NOTEN"].astype(str).str.strip().values

            if not sudah_hadir:
                sudah_hadir_semua = False

        if sudah_hadir_semua:
            st.success("✅ TELAH HADIR")
        else:
            st.warning("❌ BELUM HADIR")

        if st.session_state.host_logged_in:
            if not sudah_hadir_semua:
                if st.button("Submit / Tandakan Kehadiran Kumpulan Ini"):

                    new_records = []

                    for idx, row in group_df.iterrows():
                        noten = str(row["NOTEN"]).strip()

                        already_exists = False
                        if not attendance_df.empty and "NOTEN" in attendance_df.columns:
                            already_exists = noten in attendance_df["NOTEN"].astype(str).str.strip().values

                        if not already_exists:
                            new_records.append({
                                "BIL": row["BIL"],
                                "NOTEN": row["NOTEN"],
                                "NAMA": row["NAMA"],
                                "MENU": row["MENU"],
                                "MEJA": row["MEJA"],
                                "STATUS_KEHADIRAN": "HADIR",
                                "TARIKH_MASA": datetime.now(
                                    ZoneInfo("Asia/Kuala_Lumpur")
                                ).strftime("%Y-%m-%d %H:%M:%S")
                            })

                    if new_records:
                        attendance_df = pd.concat(
                            [attendance_df, pd.DataFrame(new_records)],
                            ignore_index=True
                        )
                        save_attendance(attendance_df)
                        st.success("Kehadiran berjaya direkodkan.")
                        st.rerun()
                    else:
                        st.info("Semua dalam BIL ini telah ditandakan hadir.")
        else:
            st.info("Hanya host boleh tandakan kehadiran.")

else:
    st.info("Sila masukkan No Tentera untuk membuat carian.")

st.markdown("---")


# =========================================================
# LIVE ATTENDANCE - HOST ONLY
# =========================================================
if st.session_state.host_logged_in:
    st.markdown("### 📋 Live Attendance / Kehadiran Semasa")

    hadir_noten = []

    if not attendance_df.empty and "NOTEN" in attendance_df.columns:
        hadir_noten = attendance_df["NOTEN"].astype(str).str.strip().tolist()

    belum_hadir_df = df[~df["NOTEN"].astype(str).str.strip().isin(hadir_noten)].copy()

    total_semua = len(df)
    total_hadir = len(attendance_df)
    total_belum_hadir = len(belum_hadir_df)

    st.info(f"Jumlah Keseluruhan: {total_semua}")
    st.success(f"Jumlah Telah Hadir: {total_hadir}")
    st.warning(f"Jumlah Belum Hadir: {total_belum_hadir}")

    st.markdown("### ✅ Telah Hadir")

    if attendance_df.empty:
        st.warning("Belum ada rekod kehadiran.")
    else:
        st.dataframe(attendance_df, use_container_width=True)

    st.markdown("### ❌ Belum Hadir")

    if belum_hadir_df.empty:
        st.success("Semua telah hadir.")
    else:
        belum_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]

        if "CATATAN" in belum_hadir_df.columns:
            belum_cols.append("CATATAN")

        st.dataframe(belum_hadir_df[belum_cols], use_container_width=True)

    csv_data = attendance_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Muat Turun Rekod Kehadiran",
        data=csv_data,
        file_name="attendance_records.csv",
        mime="text/csv"
    )
