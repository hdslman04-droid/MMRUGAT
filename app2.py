import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)",
    page_icon="🪖",
    layout="wide"
)

st.title("🪖 Sistem Kehadiran Majlis Makan Malam Regimental KPA (UGAT)")
st.caption("Masukkan No Tentera untuk semak maklumat pegawai dan tandakan kehadiran.")

# =========================================================
# FILE NAMES
# =========================================================
DATA_FILE = "SEATING_PLAN.csv"
ATTENDANCE_FILE = "attendance_records.csv"

# =========================================================
# LOAD MAIN DATA
# =========================================================
@st.cache_data
def load_data():
    file_path = Path(DATA_FILE)

    if not file_path.exists():
        st.error(f"Fail '{DATA_FILE}' tidak dijumpai. Pastikan fail ini berada dalam folder yang sama dengan app.py.")
        st.stop()

    # Baca CSV asal
    df_raw = pd.read_csv(file_path, encoding="cp1252", header=None)

    # Header sebenar berada pada baris ke-3 (index 2)
    headers = df_raw.iloc[2].tolist()
    df = df_raw.iloc[3:].copy()
    df.columns = headers

    # Buang baris kosong
    df = df.dropna(how="all").reset_index(drop=True)

    # Bersihkan nama kolum
    df.columns = [str(col).strip() for col in df.columns]

    # Bersihkan isi data
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df

# =========================================================
# LOAD / CREATE ATTENDANCE DATA
# =========================================================
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

# =========================================================
# MAIN DATA
# =========================================================
df = load_data()
attendance_df = load_attendance()

# Pastikan kolum wajib wujud
required_cols = [
    "NO TEN", "PKT", "NAMA PENUH", "PASUKAN", "JAWATAN",
    "MENU", "PASANGAN", "MENU PASANGAN", "CATATAN"
]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Kolum berikut tiada dalam fail CSV: {missing_cols}")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Carian Kehadiran")
search_no = st.sidebar.text_input("Masukkan No Tentera")

show_attendance = st.sidebar.checkbox("Papar senarai kehadiran", value=False)

# =========================================================
# SEARCH RESULT
# =========================================================
if search_no:
    result_df = df[df["NO TEN"].str.contains(search_no.strip(), case=False, na=False)].copy()

    if result_df.empty:
        st.warning("Tiada rekod dijumpai untuk nombor tentera tersebut.")
    else:
        st.success(f"{len(result_df)} rekod dijumpai.")

        for idx, row in result_df.iterrows():
            no_ten = row["NO TEN"]
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

            # Semak sama ada sudah hadir
            sudah_hadir = False
            if not attendance_df.empty:
                sudah_hadir = no_ten in attendance_df["NO TEN"].astype(str).values

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
                        "TARIKH_MASA": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
