import streamlit as st
import pandas as pd
import json
import os
import io

# ... (rest of your existing code)

st.subheader("Data Export & Reporting")
log_file_path = "data/audit_logs.jsonl"

if os.path.exists(log_file_path):
    with open(log_file_path, "r") as f:
        logs = [json.loads(line) for line in f.readlines()]
    df = pd.DataFrame(logs)
    
    # Prepare Excel Buffer
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Sheet 1: Billing Data (Aggregated by Session & Unit)
        df.groupby(['session_id', 'unit_type'])['count'].sum().reset_index().to_excel(writer, sheet_name='BillingData', index=False)
        
        # Sheet 2: Usage Tokens & Time
        df[['timestamp', 'session_id', 'unit_type', 'count', 'duration_seconds']].to_excel(writer, sheet_name='UsageTokensTime', index=False)
        
        # Sheet 3: Sampling Data
        df[['session_id', 'prompt_length', 'duration_seconds']].to_excel(writer, sheet_name='SamplingData', index=False)
    
    buffer.seek(0)
    
    st.download_button(
        label="📥 Download Full Telemetry Report (Excel)",
        data=buffer,
        file_name="DAESG_Telemetry_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No data available to export yet.")
