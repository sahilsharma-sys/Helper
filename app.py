import streamlit as st
import pandas as pd
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Easy – Data Utility",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL + SIDEBAR CSS
# --------------------------------------------------
st.markdown("""
<style>
body {background:#f6f8fb;}

section[data-testid="stSidebar"] {
    background:#ffffff;
    border-right:1px solid #e5e7eb;
}

/* Sidebar buttons */
div.stButton > button {
    width:100%;
    text-align:left;
    padding:12px 14px;
    border-radius:10px;
    border:none;
    background:transparent;
    font-weight:600;
    color:#0f172a;
}
div.stButton > button:hover {
    background:#e0ecff;
}
div.stButton > button:focus {
    background:#2563eb;
    color:white;
}

/* Upload box */
.upload-box {
    border:2px dashed #cbd5e1;
    border-radius:18px;
    padding:40px;
    text-align:center;
    background:#f8fafc;
    margin-bottom:20px;
    font-weight:600;
}

/* Metric cards */
.metric-card {
    padding:22px;
    border-radius:16px;
    color:white;
    font-weight:700;
    box-shadow:0 8px 20px rgba(0,0,0,0.12);
}
.metric-title {
    font-size:14px;
    opacity:0.9;
}
.metric-value {
    font-size:34px;
    margin-top:6px;
}

.blue {background:linear-gradient(135deg,#2563eb,#1e40af);}
.green {background:linear-gradient(135deg,#16a34a,#166534);}
.orange {background:linear-gradient(135deg,#f97316,#c2410c);}
.purple {background:linear-gradient(135deg,#7c3aed,#4c1d95);}

.stDownloadButton button {
    background:linear-gradient(135deg,#0ea5e9,#0369a1);
    color:white;
    font-weight:700;
    border-radius:12px;
    padding:10px 18px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR MENU
# --------------------------------------------------
st.sidebar.markdown("## 📊 Easy")
st.sidebar.markdown("### Navigation")

menu_items = {
    "🏠 Home": "Home",
    "📂 Compile & Clean": "Compile & Clean",
    "🧠 Column Mapper": "Column Mapper",
    "✂️ Smart Split": "Smart Split",
    "🧹 Duplicate & Validation": "Duplicate & Validation",
    "🔄 Converter": "Converter",
    "📊 Compare Files": "Compare Files",
    "📤 Export": "Export"
}

if "menu" not in st.session_state:
    st.session_state.menu = "Home"

for label, value in menu_items.items():
    if st.sidebar.button(label, key=value):
        st.session_state.menu = value

menu = st.session_state.menu

# --------------------------------------------------
# COMMON
# --------------------------------------------------
def read_file(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# --------------------------------------------------
# HOME
# --------------------------------------------------
if menu == "Home":
    st.markdown("## 📊 Data Overview")

    st.markdown('<div class="upload-box">📤 Upload CSV / Excel File</div>', unsafe_allow_html=True)
    file = st.file_uploader("", type=["csv","xlsx"])

    if file:
        df = read_file(file)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="metric-card blue">
                <div class="metric-title">Rows</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="metric-card green">
                <div class="metric-title">Columns</div>
                <div class="metric-value">{len(df.columns)}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="metric-card orange">
                <div class="metric-title">Unique Values</div>
                <div class="metric-value">{df.nunique().max()}</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="metric-card purple">
                <div class="metric-title">Preview Rows</div>
                <div class="metric-value">50</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🔍 Data Preview")
        st.dataframe(df.head(50), use_container_width=True)

# --------------------------------------------------
# COMPILE
# --------------------------------------------------
elif menu == "Compile & Clean":
    st.markdown("## 📂 Compile Multiple Files")
    files = st.file_uploader("Upload files", type=["csv","xlsx"], accept_multiple_files=True)

    if files:
        dfs = []
        for f in files:
            d = read_file(f)
            d["Source_File"] = f.name
            dfs.append(d)

        final = pd.concat(dfs, ignore_index=True)
        st.success(f"Combined Rows: {len(final)}")
        st.dataframe(final.head(100), use_container_width=True)

        buf = BytesIO()
        final.to_excel(buf, index=False)
        st.download_button("⬇️ Download Compiled File", buf.getvalue(), "compiled.xlsx")

# --------------------------------------------------
# COLUMN MAPPER
# --------------------------------------------------
elif menu == "Column Mapper":
    st.markdown("## 🧠 Column Mapper")
    file = st.file_uploader("Upload file", type=["csv","xlsx"])
    if file:
        df = read_file(file)
        mapping = {}
        for k in ["AWB","Merchant","Courier","Date","Payment","Pincode","Weight"]:
            mapping[k] = st.selectbox(k, [""] + list(df.columns))
        st.json(mapping)

# --------------------------------------------------
# SMART SPLIT
# --------------------------------------------------
elif menu == "Smart Split":
    st.markdown("## ✂️ Smart Split")
    file = st.file_uploader("Upload file", type=["csv","xlsx"])
    if file:
        df = read_file(file)
        col = st.selectbox("Split column", df.columns)
        values = st.multiselect("Values", df[col].unique())

        for v in values:
            sub = df[df[col] == v]
            buf = BytesIO()
            sub.to_excel(buf, index=False)
            st.download_button(f"Download {v}", buf.getvalue(), f"{v}.xlsx")

# --------------------------------------------------
# DUPLICATE
# --------------------------------------------------
elif menu == "Duplicate & Validation":
    st.markdown("## 🧹 Duplicate & Validation")
    file = st.file_uploader("Upload file", type=["csv","xlsx"])
    if file:
        df = read_file(file)
        cols = st.multiselect("Duplicate check columns", df.columns)
        if cols:
            dup = df[df.duplicated(cols, keep=False)]
            st.warning(f"Duplicate rows: {len(dup)}")
            st.dataframe(dup, use_container_width=True)

# --------------------------------------------------
# CONVERTER
# --------------------------------------------------
elif menu == "Converter":
    st.markdown("## 🔄 Converter")
    file = st.file_uploader("Upload file", type=["csv","xlsx"])
    if file:
        df = read_file(file)
        to = st.radio("Convert to", ["Excel","CSV"])
        buf = BytesIO()
        if to == "Excel":
            df.to_excel(buf, index=False)
            name = "converted.xlsx"
        else:
            df.to_csv(buf, index=False)
            name = "converted.csv"
        st.download_button("⬇️ Download File", buf.getvalue(), name)

# --------------------------------------------------
# COMPARE
# --------------------------------------------------
elif menu == "Compare Files":
    st.markdown("## 📊 Compare Files")
    old = st.file_uploader("Old File", type=["csv","xlsx"])
    new = st.file_uploader("New File", type=["csv","xlsx"])
    if old and new:
        d1 = read_file(old)
        d2 = read_file(new)
        diff = d2.merge(d1, how="outer", indicator=True)
        st.dataframe(diff.head(100), use_container_width=True)

# --------------------------------------------------
# EXPORT
# --------------------------------------------------
elif menu == "Export":
    st.info("📤 Auto export & summary coming next.")
