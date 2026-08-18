import json
import os
import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DAESG Technical Companion & Telemetry Sandbox",
    page_icon="🛡️",
    layout="wide",
)

st.title("DAESG Technical Companion & Telemetry Sandbox")
st.markdown(
    "Use this interface to execute evaluations, record telemetry data, and feed your financial reconciliation pipeline."
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

# Helper function to save a record
def save_log_record(record):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

# 1. Main Telemetry Execution Form
with st.form("telemetry_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        client_name = st.text_input("Client Name", "Client_Alpha")
    with col_b:
        account_id = st.text_input("Account ID", "Acc_001")

    session_id = st.text_input("Session ID", "daesg_session_01")
    unit_type = st.selectbox("Unit Type", ["tokens", "requests", "seconds"])

    col1, col2, col3 = st.columns(3)
    with col1:
        count_val = st.number_input("Consumption Count", min_value=1, value=1500)
    with col2:
        prompt_len = st.number_input("Prompt Length (Chars)", min_value=1, value=120)
    with col3:
        duration_val = st.number_input("Duration (Seconds)", min_value=0.1, value=2.5)

    submitted = st.form_submit_button("Record Telemetry & Simulate Run")

    if submitted:
        import datetime
        new_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "client_name": client_name,
            "account_id": account_id,
            "session_id": session_id,
            "unit_type": unit_type,
            "count": count_val,
            "prompt_length": prompt_len,
            "duration_seconds": duration_val
        }
        save_log_record(new_record)
        st.success("Telemetry recorded successfully!")
        st.rerun()

st.markdown("---")
st.markdown("### Current Stored Audit Logs")

logs_data = load_audit_logs()

if logs_data:
    df_logs = pd.DataFrame(logs_data)
    st.dataframe(df_logs, use_container_width=True)

    # 🛠️ Batch Controls & Multi-Tab Excel Reporting (10% global sample, 0.5% per-account cap)
    st.markdown("### 🛠️ Batch Controls & Reporting")
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("🗑️ Delete All Logs", use_container_width=True):
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
                st.success("All logs cleared!")
                st.rerun()

    with action_col2:
        with st.popover("📤 Mass Upload Template", use_container_width=True):
            st.markdown("### Upload Batch Dataset")
            mass_file = st.file_uploader("Choose Excel or CSV", type=["xlsx", "csv"], key="mass_file_main")
            if mass_file is not None:
                if mass_file.name.endswith('.xlsx'):
                    mass_df = pd.read_excel(mass_file)
                else:
                    mass_df = pd.read_csv(mass_file)
                st.write(f"Loaded {len(mass_df)} rows.")
                if st.button("Confirm Mass Ingestion"):
                    with open(LOG_FILE, "a") as f:
                        for _, row in mass_df.iterrows():
                            f.write(json.dumps(row.to_dict()) + "\n")
                    st.success(f"Successfully imported {len(mass_df)} records!")
                    st.rerun()

    with action_col3:
        # Multi-tab Excel Report Generation with Privacy Isolation Rules
        # 1. Telemetry Details (Anonymized: Client & Account excluded/masked)
        # 2. Sampled Telemetry (10% global sample, capped at <1% per account, retaining Account & Client ID)
        # 3. Billing Tokens / Aggregate Summary (Retaining Account & Client ID for billing reconciliation)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # Tab 1: Raw Telemetry Details (Anonymized - No Client/Account)
            df_telemetry = df_logs.drop(columns=[c for c in ["client_name", "account_id"] if c in df_logs.columns], errors="ignore")
            df_telemetry.to_excel(writer, sheet_name="Telemetry_Details", index=False)
            
            # Tab 2: 10% Sampled Telemetry (<1% per account cap, retaining Client & Account)
            # Applying 10% global sample or group-level cap (0.5% - 1.0% per account constraint)
            sampled_df = df_logs.groupby("account_id", group_keys=False).apply(
                lambda x: x.sample(fraction=min(0.01, len(x)), replace=False) if len(x) > 0 else x
            ) if "account_id" in df_logs.columns else df_logs.sample(frac=0.10, random_state=42)
            
            # Fallback if sample is empty or too small
            if len(sampled_df) == 0 and len(df_logs) > 0:
                sampled_df = df_logs.sample(frac=min(1.0, max(0.10, 1/len(df_logs))), random_state=42)
                
            sampled_df.to_excel(writer, sheet_name="Sampled_Telemetry_10pct", index=False)
            
            # Tab 3: Billing Reconciliation (Full aggregations with Account & Client ID)
            if "account_id" in df_logs.columns and "client_name" in df_logs.columns:
                billing_df = df_logs.groupby(["client_name", "account_id", "unit_type"], as_index=False)["count"].sum()
            else:
                billing_df = df_logs
            billing_df.to_excel(writer, sheet_name="Billing_Tokens", index=False)

        processed_data = output.getvalue()

        st.download_button(
            label="📥 Export Multi-Tab Compliance Report",
            data=processed_data,
            file_name="daesg_compliance_audit_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

else:
    st.info("No audit logs found. Run an interaction above to generate telemetry data.")
    
    st.markdown("---")
    with st.expander("📤 Mass Upload Template (Empty State)"):
        mass_file_empty = st.file_uploader("Choose Excel or CSV batch file", type=["xlsx", "csv"], key="mass_empty")
        if mass_file_empty is not None:
            if mass_file_empty.name.endswith('.xlsx'):
                mass_df = pd.read_excel(mass_file_empty)
            else:
                mass_df = pd.read_csv(mass_file_empty)
            st.write(f"Loaded {len(mass_df)} rows.")
            if st.button("Confirm Mass Ingestion"):
                with open(LOG_FILE, "a") as f:
                    for _, row in mass_df.iterrows():
                        f.write(json.dumps(row.to_dict()) + "\n")
                st.success(f"Successfully imported {len(mass_df)} records!")
                st.rerun()
