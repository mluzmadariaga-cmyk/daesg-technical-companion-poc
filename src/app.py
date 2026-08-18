import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DAESG Technical Companion PoC", page_icon="🛡️", layout="wide"
)

st.title("🛡️ DAESG Technical Companion PoC")
st.markdown(
    "Data and Attention ESG Framework: Telemetry, Stratified Sampling, and Compliance Audit."
)

# Ensure data directory exists
LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "audit_logs.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)


# Helper function to load logs safely
def load_audit_logs():
  logs = []
  if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
      for line in f:
        line = line.strip()
        if line:
          try:
            logs.append(json.loads(line))
          except json.JSONDecodeError:
            continue
  return logs


# Helper function to save a single record
def save_log_record(record):
  with open(LOG_FILE, "a") as f:
    f.write(json.dumps(record) + "\n")


# Sidebar Controls for Data Management (Restored with Account and Client fields)
st.sidebar.header("⚙️ Data Management & Testing")

with st.sidebar.expander("➕ Add Manual Transaction"):
  with st.form("manual_entry_form"):
    m_client = st.text_input("Client ID / Name", "Client_Alpha")
    m_account = st.text_input("Account ID", "Acc_001")
    m_session = st.text_input("Session ID", "daesg_session_01")
    m_unit = st.selectbox("Unit Type", ["tokens", "requests", "seconds"])
    m_count = st.number_input("Count / Volume", min_value=1, value=1000)
    m_prompt_len = st.number_input("Prompt Length", min_value=1, value=100)
    m_duration = st.number_input(
        "Duration (Seconds)", min_value=0.1, value=1.5
    )
    m_submitted = st.form_submit_button("Record Transaction")

    if m_submitted:
      import datetime

      new_record = {
          "timestamp": datetime.datetime.now().isoformat(),
          "client_id": m_client,
          "account_id": m_account,
          "session_id": m_session,
          "unit_type": m_unit,
          "count": m_count,
          "prompt_length": m_prompt_len,
          "duration_seconds": m_duration,
      }
      save_log_record(new_record)
      st.success("Manual transaction logged successfully!")
      st.rerun()

# Sidebar Bulk Import
with st.sidebar.expander("📥 Bulk Import (Template)"):
  uploaded_file = st.file_uploader(
      "Upload Excel or CSV batch file", type=["xlsx", "csv"]
  )
  if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
      bulk_df = pd.read_excel(uploaded_file)
    else:
      bulk_df = pd.read_csv(uploaded_file)

    st.write(f"Rows detected: {len(bulk_df)}")
    if st.button("Confirm Bulk Append"):
      with open(LOG_FILE, "a") as f:
        for _, row in bulk_df.iterrows():
          f.write(json.dumps(row.to_dict()) + "\n")
      st.success(f"Successfully imported {len(bulk_df)} records!")
      st.rerun()

# Load current logs
logs_data = load_audit_logs()

# Main Dashboard View
st.markdown("### 📊 Live Telemetry & Sampling Validation Dashboard")

if logs_data:
  df_logs = pd.DataFrame(logs_data)

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Records", len(df_logs))
  col2.metric(
      "Unique Accounts",
      df_logs["account_id"].nunique() if "account_id" in df_logs.columns else 0,
  )
  col3.metric(
      "Unique Sessions",
      df_logs["session_id"].nunique() if "session_id" in df_logs.columns else 0,
  )

  # 🛠️ Batch Data Controls placed right between metrics/controls and the data table preview
  st.markdown("---")
  st.markdown("### 🛠️ Batch Data Controls")
  ctrl_col1, ctrl_col2 = st.columns(2)

  with ctrl_col1:
    if st.button("🗑️ Delete All Records (Clear Log)", use_container_width=True):
      if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        st.success("All logs cleared successfully!")
        st.rerun()

  with ctrl_col2:
    with st.popover("📤 Mass Upload Template File", use_container_width=True):
      st.markdown("### Upload Mass Dataset")
      mass_file = st.file_uploader(
          "Choose Excel or CSV file", type=["xlsx", "csv"], key="mass_popover"
      )
      if mass_file is not None:
        if mass_file.name.endswith(".xlsx"):
          mass_df = pd.read_excel(mass_file)
        else:
          mass_df = pd.read_csv(mass_file)
        st.write(f"Loaded {len(mass_df)} rows.")
        if st.button("Commit Mass Upload"):
          with open(LOG_FILE, "a") as f:
            for _, row in mass_df.iterrows():
              f.write(json.dumps(row.to_dict()) + "\n")
          st.success(
              f"Successfully mass-uploaded {len(mass_df)} records!"
          )
          st.rerun()

  st.markdown("---")
  st.markdown("#### Stored Audit Records Preview")
  st.dataframe(df_logs, use_container_width=True)

  st.info(
      "💡 Ready to validate: The aggregate totals flow to billing, while your"
      " 1% global sample and 0.5% per-account cap apply automatically for"
      " reporting."
  )
else:
  st.warning(
      "No audit data found. Use the sidebar to add manual transactions or use"
      " the mass upload control below!"
  )

  st.markdown("---")
  st.markdown("### 🛠️ Batch Data Controls")
  with st.popover("📤 Mass Upload Template File", use_container_width=True):
    st.markdown("### Upload Mass Dataset")
    mass_file = st.file_uploader(
        "Choose Excel or CSV file", type=["xlsx", "csv"], key="mass_popover_empty"
    )
    if mass_file is not None:
      if mass_file.name.endswith(".xlsx"):
        mass_df = pd.read_excel(mass_file)
      else:
        mass_df = pd.read_csv(mass_file)
      st.write(f"Loaded {len(mass_df)} rows.")
      if st.button("Commit Mass Upload"):
        with open(LOG_FILE, "a") as f:
          for _, row in mass_df.iterrows():
            f.write(json.dumps(row.to_dict()) + "\n")
        st.success(f"Successfully mass-uploaded {len(mass_df)} records!")
        st.rerun()
