import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="DAESG Technical Companion", page_icon="📊", layout="wide")

st.title("DAESG Technical Companion & Telemetry Sandbox")
st.markdown("Use this interface to execute evaluations, record telemetry data, and feed your financial reconciliation pipeline.")

# Input parameters
session_id = st.text_input("Session ID", value="daesg_session_01")
unit_type = st.selectbox("Unit Type", ["tokens", "queries", "api_calls"])
count = st.number_input("Consumption Count", min_value=1, value=1500)
prompt_length = st.number_input("Prompt Length (Chars)", min_value=1, value=120)
duration_seconds = st.number_input("Duration (Seconds)", min_value=0.1, value=2.5)

if st.button("Record Telemetry & Simulate Run"):
    log_dir = "data"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "audit_logs.jsonl")
    
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "unit_type": unit_type,
        "count": count,
        "prompt_length": prompt_length,
        "duration_seconds": duration_seconds
    }
    
    # Append to permanent JSONL log storage
    with open(log_path, "a") as f:
        f.write(json.dumps(payload) + "\n")
        
    st.success(f"Telemetry successfully recorded to {log_path}!")
    st.json(payload)

st.markdown("---")
st.subheader("Current Stored Audit Logs")
log_file_path = "data/audit_logs.jsonl"
if os.path.exists(log_file_path):
    with open(log_file_path, "r") as f:
        logs = [json.loads(line) for line in f.readlines()]
    st.dataframe(logs)
else:
    info_text = "No audit logs found yet. Run an interaction above to generate telemetry data."
    st.info(info_text)
