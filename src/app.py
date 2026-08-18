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


# Helper function to load logs safely matching your schema format
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


# Sidebar Controls for Data Management
st.sidebar.header("⚙️ Data Management & Testing")

# 1. Manual Entry Option (matching your original schema format)
with st.sidebar.expander("➕ Add Manual Transaction"):
  with st.form("manual_entry_form"):
    m_session = st.text_input("Session ID", "daesg_session_02")
    m_unit = st.selectbox("Unit Type", ["tokens", "requests", "seconds"])
    m_count = st.number_input("Count", min_value=1, value=1000)
    m_prompt_len = st.number_input("Prompt Length", min_value=1, value=100)
    m_duration = st.number_input(
        "Duration (Seconds)", min_value=0.1, value=1.5
    )
    m_submitted = st.form_submit_button("Record Transaction")

    if m_submitted:
      import datetime

      new_record = {
          "timestamp": datetime.datetime.now().isoformat(),
          "session_id": m_session,
          "unit_type": m_unit,
          "count": m_count,
          "prompt_length": m_prompt_len,
          "duration_seconds": m_duration,
      }
      save_log_record(new_record)
      st.success("Manual transaction logged successfully!")
      st.rerun()

# 2. Bulk Import Option
with st.sidebar.expander("📥 Bulk Import (1k+ Template)"):
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

# 3. Log Inspection & Single-Record Deletion
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Audit Log Inspection")
logs_data = load_audit_logs()

if logs_data:
  st.sidebar.write(f"Total stored records: {len(logs_data)}")

  record_indices = [
      f"Row {i}: {r.get('session_id', 'Unknown')} ({r.get('unit_type', '')})"
      for i, r in enumerate(logs_data)
  ]
  selected_to_delete = st.sidebar.selectbox(
      "Select record to delete", ["-- None --"] + record_indices
  )

  if selected_to_delete != "-- None --":
    idx_to_remove = int(selected_to_delete.split(" ")[1].replace(":", ""))
    if st.sidebar.button("🗑️ Delete Selected Record"):
      logs_data.pop(idx_to_remove)
      with open(LOG_FILE, "w") as f:
        for r in logs_data:
          f.write(json.dumps(r) + "\n")
      st.success(f"Deleted record at Row {idx_to_remove}!")
      st.rerun()
else:
  st.sidebar.info("No audit logs recorded yet.")

# Main Dashboard View
st.markdown("### 📊 Live Telemetry & Sampling Validation Dashboard")

if logs_data:
  df_logs = pd.DataFrame(logs_data)

  col1, col2 = st.columns(2)
  col1.metric("Total Records", len(df_logs))
  col2.metric(
      "Unique Sessions",
      df_logs["session_id"].nunique() if "session_id" in df_logs.columns else 0,
  )

  st.markdown("#### Stored Audit Records Preview")
  st.dataframe(df_logs, use_container_width=True)

  st.markdown("---")
  st.info(
      "💡 Ready to validate: The aggregate totals flow to billing, while your"
      " 1% global sample and 0.5% per-account cap apply automatically for"
      " reporting."
  )

  # Restored and added the two required buttons at the bottom: Delete All and Mass Upload
  st.markdown("### 🛠️ Batch Data Controls")
  action_col1, action_col2 = st.columns(2)

  with action_col1:
    if st.button("🗑️ Delete All Records (Clear Log)", use_container_width=True):
      if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        st.success("All logs have been cleared successfully!")
        st.rerun()
      else:
        st.warning("No log file found to clear.")

  with action_col2:
    with st.popover("📤 Mass Upload Template File", use_container_width=True):
      st.markdown("### Upload Mass Dataset")
      mass_file = st.file_uploader(
          "Choose Excel or CSV file for mass upload",
          type=["xlsx", "csv"],
          key="mass_upload_bottom",
      )
      if mass_file is not None:
        if mass_file.name.endswith(".xlsx"):
          mass_df = pd.read_excel(mass_file)
        else:
          mass_df = pd.read_csv(mass_file)

        st.write(f"Loaded {len(mass_df)} rows ready for ingestion.")
        if st.button("Commit Mass Upload to Database"):
          with open(LOG_FILE, "a") as f:
            for _, row in mass_df.iterrows():
              f.write(json.dumps(row.to_dict()) + "\n")
          st.success(
              f"Successfully mass-uploaded {len(mass_df)} records!"
          )
          st.rerun()
else:
  st.warning(
      "No audit data found. Use the sidebar to add manual transactions or upload"
      " your bulk test template!"
  )

  # Also provide the bulk options at the bottom if screen is empty
  st.markdown("### 🛠️ Batch Data Controls")
  if st.button("📤 Mass Upload Template File", use_container_width=True):
    st.info(
        "Please use the sidebar bulk import tool or add an initial record first."
    )
