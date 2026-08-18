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


# Sidebar Controls for Data Management
st.sidebar.header("⚙️ Data Management & Testing")

# 1. Manual Entry Option
with st.sidebar.expander("➕ Add Manual Transaction"):
  with st.form("manual_entry_form"):
    m_client = st.text_input("Client ID / Name", "Client_Alpha")
    m_account = st.text_input("Account ID", "Acc_001")
    m_volume = st.number_input("Transaction Volume", min_value=1.0, value=100.0)
    m_submitted = st.form_submit_button("Record Transaction")

    if m_submitted:
      new_record = {
          "client_id": m_client,
          "account_id": m_account,
          "volume": m_volume,
          "source": "Manual",
      }
      save_log_record(new_record)
      st.success("Manual transaction logged successfully!")
      st.rerun()

# 2. Bulk Import Option (e.g., 1,000 records template)
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

  # Display selector to delete a specific record by index
  record_indices = [
      f"Row {i}: {r.get('client_id', 'Unknown')} - {r.get('account_id', 'Unknown')}"
      for i, r in enumerate(logs_data)
  ]
  selected_to_delete = st.sidebar.selectbox(
      "Select record to delete", ["-- None --"] + record_indices
  )

  if selected_to_delete != "-- None --":
    idx_to_remove = int(selected_to_delete.split(" ")[1].replace(":", ""))
    if st.sidebar.button("🗑️ Delete Selected Record"):
      logs_data.pop(idx_to_remove)
      # Rewrite the file with the remaining rows
      with open(LOG_FILE, "w") as f:
        for r in logs_data:
          f.write(json.dumps(r) + "\n")
      st.success(f"Deleted record at Row {idx_to_remove}!")
      st.rerun()

  if st.sidebar.button("⚠️ Wipe All Logs"):
    if os.path.exists(LOG_FILE):
      os.remove(LOG_FILE)
      st.success("All logs cleared!")
      st.rerun()
else:
  st.sidebar.info("No audit logs recorded yet.")

# Main Dashboard View
st.markdown("### 📊 Live Telemetry & Sampling Validation Dashboard")

if logs_data:
  df_logs = pd.DataFrame(logs_data)

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Records", len(df_logs))
  if "volume" in df_logs.columns:
    col2.metric("Total Aggregate Volume", f"{df_logs['volume'].sum():,.2f}")
  col3.metric("Unique Accounts", df_logs["account_id"].nunique() if "account_id" in df_logs.columns else 0)

  st.markdown("#### Stored Audit Records Preview")
  st.dataframe(df_logs, use_container_width=True)

  # Placeholder for your sampling and Excel export logic
  st.markdown("---")
  st.info(
      "💡 Ready to validate: The aggregate totals flow to billing, while your"
      " 1% global sample and 0.5% per-account cap apply automatically for"
      " reporting."
  )
else:
  st.warning(
      "No audit data found. Use the sidebar to add manual transactions or upload"
      " your bulk test template!"
  )
