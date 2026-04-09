import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)",
    page_icon="🪖",
    layout="wide"
)

# =========================================================
# FILE PATHS
# =========================================================
DATA_FILE = "SEATING_PLAN.csv"
ATTENDANCE_FILE = "attendance_records.csv"

LOGO_KPA = "KPA.png"
LOGO_ATM = "Logo ATM.png"
LOGO_UGAT = "Logo-UGAT.png"
CENTER_IMAGE = "FRONT PAAGE.png"

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def get_kl_time():
    kl_now = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    return kl_now.strftime("%d/%m/%Y %I:%M:%S %p")

@st.cache_data
def load_data():
    file_path = Path(DATA_FILE)

    if not file_path.exists():
        st.error(f"Fail '{DATA_FILE}' tidak dijumpai. Pastikan fail ini berada dalam folder yang sama dengan app.py.")
        st.stop()

    df_raw = pd.read_csv(file_path, encoding="cp1252", header=None)

    # Header sebenar pada baris ke-3
    headers = df_raw.iloc[2].tolist()
    df = df_raw.iloc[3:].copy()
    df.columns = headers

    df = df.dropna(how="all").reset_index(drop=True)
    df.columns = [str(col).strip() for col in df.columns]

    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df

def load_attendance():
    file_path = Path(ATTENDANCE_FILE)

    if file_path.exists():
        try:
            attendance_df = pd.read_csv(file_path)
            attendance_df.columns = [str(col).strip() for col in attendance_df.columns]
            return attendance_df
        except Exception:
            return pd.DataFrame(columns=[
                "NO TEN", "NAMA PENUH", "PKT", "PASUKAN", "JAWATAN",
                "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN",
                "STATUS_KEHADIRAN", "TARIKH_MASA"
            ])
    else:
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

# =========================================================
# LOAD DATA
# =========================================================
df = load_data()
attendance_df = load_attendance()

required_cols = [
    "NO TEN", "PKT", "NAMA PENUH", "PASUKAN", "JAWATAN",
    "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN"
]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Kolum berikut tiada dalam fail CSV: {missing_cols}")
    st.stop()

# =========================================================
# TOP DASHBOARD LOGOS
# =========================================================
top_left, top_center, top_right = st.columns([1, 1, 1])

with top_left:
    show_image_if_exists(LOGO_KPA, width=220)

with top_center:
    show_image_if_exists(LOGO_ATM, width=220)

with top_right:
    show_image_if_exists(LOGO_UGAT, width=220)

# =========================================================
# TITLE + TIME
# =========================================================
st.markdown("<h1 style='text-align: center;'>🪖 Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Masukkan No Tentera untuk semak maklumat pegawai dan tandakan kehadiran.</p>", unsafe_allow_html=True)

current_time = get_kl_time()
st.markdown(
    f"""
    <div style='text-align:center; font-size:18px; font-weight:600; margin-bottom:20px;'>
        Masa Terkini Kuala Lumpur, Malaysia: {current_time}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CENTER IMAGE
# =========================================================
left_space, center_space, right_space = st.columns([1, 3, 1])
with center_space:
    show_image_if_exists(CENTER_IMAGE, use_container_width=True)

st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Carian Kehadiran")
search_no = st.sidebar.text_input("Masukkan No Tentera")
show_attendance = st.sidebar.checkbox("Papar senarai kehadiran", value=False)

# =========================================================
# SEARCH SECTION
# =========================================================
if search_no:
    result_df = df[df["NO TEN"].str.contains(search_no.strip(), case=False, na=False)].copy()

    if result_df.empty:
        st.warning("Tiada rekod dijumpai untuk nombor tentera tersebut.")
    else:
        st.success(f"{len(result_df)} rekod dijumpai.")

        for idx, row in result_df.iterrows():
            no_ten = str(row["NO TEN"]).strip()
            nama = row["NAMA PENUH"]

            st.markdown("---")
            st.subheader(f"Maklumat Pegawai: {nama}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**No Tentera:** {row['NO TEN']}")
                st.write(f"**Pangkat:** {row['PKT']}")
                st.write(f"**Nama Penuh:** {row['NAMA PENUH']}")
                st.write(f"**Pasukan:** {row['PASUKAN']}")
                st.write(f"**Jawatan:** {row['JAWATAN']}")

            with col2:
                st.write(f"**Menu:** {row['MENU']}")
                st.write(f"**Pasangan:** {row['PASANGAN']}")
                st.write(f"**Menu Pasangan:** {row['MENU PASANGAN']}")
                st.write(f"**Catatan:** {row['CATATAN']}")

            sudah_hadir = False
            if not attendance_df.empty and "NO TEN" in attendance_df.columns:
                attendance_df["NO TEN"] = attendance_df["NO TEN"].astype(str).str.strip()
                sudah_hadir = no_ten in attendance_df["NO TEN"].values

            if sudah_hadir:
                st.success("✅ Kehadiran telah ditandakan.")
            else:
                button_key = f"submit_{idx}_{no_ten}"

                if st.button("Submit / Tandakan Kehadiran", key=button_key):
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

                    st.success(f"Kehadiran bagi {nama} berjaya direkodkan.")
                    st.rerun()

        st.markdown("### Paparan Jadual Rekod Dijumpai")
        st.dataframe(
            result_df[[
                "NO TEN", "PKT", "NAMA PENUH", "PASUKAN",
                "JAWATAN", "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN"
            ]],
            use_container_width=True
        )
else:
    st.info("Sila masukkan No Tentera di bahagian kiri untuk membuat carian.")

# =========================================================
# ATTENDANCE LIST
# =========================================================
if show_attendance:
    st.markdown("---")
    st.header("📋 Senarai Kehadiran")

    if attendance_df.empty:
        st.warning("Belum ada rekod kehadiran.")
    else:
        st.dataframe(attendance_df, use_container_width=True)

        csv_data = attendance_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Muat Turun Rekod Kehadiran",
            data=csv_data,
            file_name="attendance_records.csv",
            mime="text/csv"
        )
