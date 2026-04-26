import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import base64

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sistem Kehadiran MMR KPA (UGAT)",
    page_icon="TDM.png",
    layout="centered"
)

# =========================================================
# HIDE STREAMLIT DEFAULT UI
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

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.block-container {
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
</style>
""", unsafe_allow_html=True)

# =========================================================
# FILE PATH
# =========================================================
DATA_FILE = "SEATING_PLAN.csv"
CENTER_IMAGE = "FRONT PAAGE.png"

# =========================================================
# HELPER
# =========================================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def show_image_if_exists(image_path, width=None, use_container_width=False):
    if Path(image_path).exists():
        st.image(image_path, width=width, use_container_width=use_container_width)

def get_file_updated_time():
    if not Path(DATA_FILE).exists():
        return "Tiada rekod"

    latest_time = datetime.fromtimestamp(
        Path(DATA_FILE).stat().st_mtime,
        ZoneInfo("Asia/Kuala_Lumpur")
    )

    return latest_time.strftime("%d/%m/%Y %I:%M:%S %p")

# =========================================================
# LOAD DATA
# =========================================================
def load_data():
    try:
        return pd.read_csv(DATA_FILE, encoding="utf-8")
    except:
        return pd.read_csv(DATA_FILE, encoding="latin1")

# =========================================================
# HEADER (BANNER)
# =========================================================
img_base64 = get_base64_image("TDM.png")

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

# =========================================================
# LAST UPDATED
# =========================================================
st.markdown(
    f"<div class='time-box'>Last Updated: {get_file_updated_time()}</div>",
    unsafe_allow_html=True
)

# =========================================================
# LOAD DATA
# =========================================================
df = load_data()

# =========================================================
# SEARCH
# =========================================================
st.subheader("Carian Kehadiran")

search_no = st.text_input("Masukkan No Tentera")

# =========================================================
# RESULT
# =========================================================
if search_no:

    result_df = df[df["NO TEN"].astype(str).str.contains(search_no.strip(), case=False, na=False)]

    if result_df.empty:
        st.warning("Tiada rekod dijumpai.")
    else:
        st.success(f"{len(result_df)} rekod dijumpai")

        for idx, row in result_df.iterrows():

            st.markdown("---")

            left_col, right_col = st.columns([1, 1.3])

            with left_col:
                st.markdown(f"### {row['NAMA PENUH']}")
                st.write(f"**No Tentera:** {row['NO TEN']}")
                st.write(f"**Pangkat:** {row['PKT']}")
                st.write(f"**Pasukan:** {row['PASUKAN']}")
                st.write(f"**Jawatan:** {row['JAWATAN']}")
                st.write(f"**Menu:** {row['MENU']}")
                st.write(f"**Pasangan:** {row['PASANGAN']}")
                st.write(f"**Menu Pasangan:** {row['MENU PASANGAN']}")
                st.write(f"**Catatan:** {row['CATATAN']}")

            with right_col:
                show_image_if_exists(CENTER_IMAGE, use_container_width=True)
