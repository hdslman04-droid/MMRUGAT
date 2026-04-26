import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Sistem Kehadiran MMR KPA (UGAT)",
    page_icon="TDM.png",
    layout="centered"
)

# =========================================================
# HIDE STREAMLIT DEFAULT UI (TAMBAHAN)
# =========================================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

[data-testid="stDecoration"] {
    display: none;
}

[data-testid="stStatusWidget"] {
    display: none;
}

.viewerBadge_container__1QSob {
    display: none;
}

.stDeployButton {
    display: none;
}
</style>
""", unsafe_allow_html=True)

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
    margin-bottom: 18px;
    color: black;
}
.center-title {
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
}
.center-caption {
    text-align: center;
    margin-bottom: 20px;
    color: #555;
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

DATA_FILE = "SEATING_PLAN.csv"
ATTENDANCE_FILE = "attendance_records.csv"

LOGO_UGAT = "Logo-UGAT.png"
CENTER_IMAGE = "FRONT PAAGE.png"

DEFAULT_HOST_PASSWORD = "host123"

required_cols = [
    "NO TEN", "PKT", "NAMA PENUH", "PASUKAN", "JAWATAN",
    "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN"
]

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

@st.cache_data
def load_default_data():
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

    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df

def load_uploaded_files(uploaded_files):
    all_data = []

    for uploaded_file in uploaded_files:
        df_raw = pd.read_csv(uploaded_file, encoding="cp1252", header=None)

        headers = df_raw.iloc[2].tolist()
        df = df_raw.iloc[3:].copy()
        df.columns = headers

        df = df.dropna(how="all").reset_index(drop=True)
        df.columns = [str(col).strip() for col in df.columns]

        for col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

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
        "NO TEN", "NAMA PENUH", "PKT", "PASUKAN", "JAWATAN",
        "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN",
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

if "host_logged_in" not in st.session_state:
    st.session_state.host_logged_in = False

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# =========================================================
# LOGO + BANNER (DITUKAR)
# =========================================================
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_image("Logo-UGAT.png")

st.markdown(f"""
<div style="display:flex; align-items:center; gap:12px;
background: linear-gradient(90deg, #020617, #111827);
padding:15px; border-radius:15px; margin-bottom:15px;">
    <img src="data:image/png;base64,{img_base64}" width="50">
    <h2 style="margin:0; color:white;">
        Sistem Kehadiran Majlis Makan Malam Regimental KPA (GAJI)
    </h2>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div class='center-caption'>Masukkan No Tentera untuk semak maklumat pegawai dan tandakan kehadiran.</div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<div class='time-box'>Last Updated: {get_file_updated_time()}</div>",
    unsafe_allow_html=True
)

st.markdown("---")
