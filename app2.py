import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import base64
from PIL import Image, ImageDraw

# Set page config for Streamlit
st.set_page_config(
    page_title="MMR KPA (GAJI)",
    page_icon="TDM.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "host_logged_in" not in st.session_state:
    st.session_state.host_logged_in = False

# Define constants
DATA_FILE = "SEATING PLAN MMR PENGHARGAAN 2026 2.csv"
ATTENDANCE_FILE = "attendance_records.csv"
LOGO_UGAT = "Logo-UGAT.png"
CENTER_IMAGE = "GAMBAR BARU 3.png"
DEFAULT_HOST_PASSWORD = "salman"
required_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]

# =========================================================
# BASIC FUNCTIONS
# =========================================================
def get_file_mtime(file_path):
    path = Path(file_path)
    if path.exists():
        return path.stat().st_mtime
    return 0

def get_file_updated_time():
    files_to_check = [DATA_FILE, ATTENDANCE_FILE]
    existing_files = [Path(f) for f in files_to_check if Path(f).exists()]
    if not existing_files:
        return "Tiada rekod"
    latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
    latest_time = datetime.fromtimestamp(latest_file.stat().st_mtime, ZoneInfo("Asia/Kuala_Lumpur"))
    return latest_time.strftime("%d/%m/%Y %I:%M:%S %p")

def clean_csv(df_raw):
    df_raw = df_raw.dropna(how="all").reset_index(drop=True)
    df_raw.columns = [str(col).strip().upper() for col in df_raw.columns]
    if all(col in df_raw.columns for col in required_cols):
        df = df_raw.copy()
    else:
        header_row_index = None
        for i in range(len(df_raw)):
            row_values = [str(value).strip().upper() for value in df_raw.iloc[i].tolist()]
            if "BIL" in row_values and "NOTEN" in row_values and "NAMA" in row_values and "MENU" in row_values and "MEJA" in row_values:
                header_row_index = i
                break
        if header_row_index is None:
            st.error("Header CSV tidak dijumpai. Pastikan fail CSV ada kolum BIL, NOTEN, NAMA, MENU dan MEJA.")
            st.stop()
        headers = [str(value).strip().upper() for value in df_raw.iloc[header_row_index].tolist()]
        df = df_raw.iloc[header_row_index + 1:].copy()
        df.columns = headers
    df = df.loc[:, df.columns.notna()]
    df = df.loc[:, [str(col).strip() != "" for col in df.columns]]
    df = df.loc[:, ~df.columns.astype(str).str.upper().str.startswith("UNNAMED")]
    df = df.dropna(how="all").reset_index(drop=True)
    df.columns = [str(col).strip().upper() for col in df.columns]
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()
    if "BIL" in df.columns:
        df["BIL"] = df["BIL"].str.replace(".0", "", regex=False)
    if "NOTEN" in df.columns:
        df["NOTEN"] = df["NOTEN"].str.replace(".0", "", regex=False)
    if "MEJA" in df.columns:
        df["MEJA"] = df["MEJA"].str.upper().str.replace(".0", "", regex=False)
    return df

@st.cache_data
def load_default_data(file_mtime):
    file_path = Path(DATA_FILE)
    if not file_path.exists():
        st.error(f"Fail '{DATA_FILE}' tidak dijumpai.")
        st.stop()
    df_raw = pd.read_csv(file_path, encoding="utf-8")
    return clean_csv(df_raw)

# =========================================================
# HIGHLIGHT MEJA DALAM LAYOUT
# =========================================================
def generate_highlighted_layout(df):
    # Open the seating chart image
    image_path = "GAMBAR BARU 3.png"
    try:
        img = Image.open(image_path)
    except Exception as e:
        st.error(f"Error opening the seating plan image: {e}")
        return None, None

    # Coordinates of seats (adjust these coordinates based on your actual layout)
    seat_coordinates = {
        'A1': (100, 200),  # Example: Seat A1 is at position (100, 200) in the image
        'A2': (150, 200),
        'B1': (100, 250),
        # Add more seats here based on your actual layout
    }

    # List of highlighted seats (example: from the 'MEJA' column)
    seats_to_highlight = df["MEJA"].tolist()

    # Create a drawing object to overlay the highlights
    draw = ImageDraw.Draw(img)

    # Highlight color
    highlight_color = (255, 0, 0)  # Red color

    # Size of the highlight box
    highlight_size = 40  # Adjust as needed

    # Loop through the seats to highlight them
    missing_seats = []

    for seat in seats_to_highlight:
        seat = seat.strip().upper()
        if seat in seat_coordinates:
            x, y = seat_coordinates[seat]
            draw.rectangle([x-10, y-10, x+highlight_size, y+highlight_size], outline=highlight_color, width=5)
        else:
            missing_seats.append(seat)

    # Save the modified image
    output_image_path = "highlighted_seating_plan.png"
    img.save(output_image_path)

    # Convert the image to base64 for display in Streamlit
    with open(output_image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    return img_base64, missing_seats

# =========================================================
# SIDEBAR HOST LOGIN + UPLOAD
# =========================================================
if st.session_state.host_logged_in:
    st.sidebar.title("Host Panel")
    st.sidebar.success("Anda login sebagai host.")

    uploaded_files = st.sidebar.file_uploader("Upload CSV Files", accept_multiple_files=True, type=["csv"])
    if uploaded_files:
        try:
            new_df = load_uploaded_files(uploaded_files)

            missing_uploaded_cols = [col for col in required_cols if col not in new_df.columns]
            if missing_uploaded_cols:
                st.sidebar.error(f"CSV baru tidak lengkap. Kolum tiada: {missing_uploaded_cols}")
            else:
                new_df.to_csv(DATA_FILE, index=False, encoding="utf-8")
                reset_attendance()
                st.cache_data.clear()
                st.sidebar.success("CSV baru berjaya dimuat naik.")
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"Fail tidak dapat dibaca: {e}")

    if st.sidebar.button("Logout Host"):
        st.session_state.host_logged_in = False
        st.rerun()

else:
    st.sidebar.title("Host Login")
    host_password_input = st.sidebar.text_input("Masukkan kata laluan", type="password")
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
df = load_default_data(get_file_mtime(DATA_FILE))
attendance_df = load_attendance()

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Kolum berikut tiada dalam fail CSV: {missing_cols}")
    st.stop()

# =========================================================
# SEARCH SECTION
# =========================================================
search_no = st.text_input("Nombor Tentera:", max_chars=7, placeholder="Contoh: 3004463")
if search_no:
    search_value = search_no.strip()
    result_df = df[df["NOTEN"].astype(str).str.contains(search_value, case=False, na=False)].copy()
    if result_df.empty:
        st.warning("Tiada rekod dijumpai untuk nombor tentera tersebut.")
    else:
        bil_value = str(result_df.iloc[0]["BIL"]).strip()
        group_df = df[df["BIL"].astype(str).str.strip() == bil_value].copy()
        st.success(f"Rekod dijumpai")
        st.markdown("### Maklumat Kehadiran")
        display_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]
        st.table(group_df[display_cols])

        st.markdown("### Pelan Kedudukan Dewan")
        layout_base64, missing_meja = generate_highlighted_layout(df)
        if layout_base64:
            st.image(f"data:image/png;base64,{layout_base64}", use_column_width=True)
            if missing_meja:
                st.warning(f"The following seats are missing from the layout: {', '.join(missing_meja)}")
        else:
            st.error("Error generating the highlighted image.")
else:
    st.info("Sila masukkan No Tentera untuk membuat carian.")

# =========================================================
# HOST ONLY - LIVE ATTENDANCE MANAGEMENT
# =========================================================
if st.session_state.host_logged_in:
    st.markdown("### 📋 Live Attendance / Kehadiran Semasa")

    hadir_noten = []

    if not attendance_df.empty and "NOTEN" in attendance_df.columns:
        hadir_noten = attendance_df["NOTEN"].astype(str).str.strip().tolist()

    belum_hadir_df = df[
        ~df["NOTEN"].astype(str).str.strip().isin(hadir_noten)
    ].copy()

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
        hadir_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]
        st.dataframe(attendance_df[hadir_cols], use_container_width=True)

    st.markdown("### ❌ Belum Hadir")

    if belum_hadir_df.empty:
        st.success("Semua telah hadir.")
    else:
        belum_cols = ["BIL", "NOTEN", "NAMA", "MENU", "MEJA"]
        st.dataframe(belum_hadir_df[belum_cols], use_container_width=True)

    # Allow for CSV download of attendance records
    csv_data = attendance_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Muat Turun Rekod Kehadiran",
        data=csv_data,
        file_name="attendance_records.csv",
        mime="text/csv"
    )

# =========================================================
# FUNCTION TO MANAGE ATTENDANCE
# =========================================================
def reset_attendance():
    reset_attendance_df = pd.DataFrame(columns=[
        "BIL", "NOTEN", "NAMA", "MENU", "MEJA",
        "STATUS_KEHADIRAN", "TARIKH_MASA"
    ])
    reset_attendance_df.to_csv(ATTENDANCE_FILE, index=False, encoding="utf-8")

def save_attendance(attendance_df):
    attendance_df.to_csv(ATTENDANCE_FILE, index=False, encoding="utf-8")

def load_attendance():
    file_path = Path(ATTENDANCE_FILE)
    if file_path.exists():
        try:
            attendance_df = pd.read_csv(file_path)
            attendance_df.columns = [str(col).strip().upper() for col in attendance_df.columns]
            for col in attendance_df.columns:
                attendance_df[col] = attendance_df[col].fillna("").astype(str).str.strip()

            if "NOTEN" in attendance_df.columns:
                attendance_df["NOTEN"] = attendance_df["NOTEN"].str.replace(".0", "", regex=False)

            return attendance_df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "BIL", "NOTEN", "NAMA", "MENU", "MEJA",
        "STATUS_KEHADIRAN", "TARIKH_MASA"
    ])

def load_uploaded_files(uploaded_files):
    all_data = []
    for uploaded_file in uploaded_files:
        df_raw = pd.read_csv(uploaded_file, encoding="utf-8")
        df = clean_csv(df_raw)
        all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

# =========================================================
# HANDLE ATTENDANCE RECORD UPLOAD AND MARKING
# =========================================================
if st.session_state.host_logged_in:
    if not attendance_df.empty:
        st.markdown("### Kehadiran / Attendance")

        # Check if all members in the selected group have attended
        sudah_hadir_semua = True

        for idx, row in group_df.iterrows():
            noten = str(row["NOTEN"]).strip()

            sudah_hadir = False

            if not attendance_df.empty and "NOTEN" in attendance_df.columns:
                sudah_hadir = noten in attendance_df["NOTEN"].astype(str).str.strip().values

            if not sudah_hadir:
                sudah_hadir_semua = False

        # Display attendance status
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
