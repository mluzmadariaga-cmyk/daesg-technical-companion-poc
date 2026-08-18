import sqlite3
import json
import os

DB_PATH = os.getenv("DB_PATH", "/app/data/billing_ledger.db")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/data/audit_logs.jsonl")

def execute_second_line_reconciliation(materiality_threshold_pct=0.1):
    """
    Performs Second Line of Defence reconciliation: 
    Compares operational telemetry aggregate tokens against commercial billing records.
    """
    # 1. Aggregate from permanent telemetry log (Pipeline 1 source simulation)
    telemetry_tokens = 0
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as f:
            for line in f:
                record = json.loads(line)
                if record.get("unit_type") == "tokens":
                    telemetry_tokens += record.get("metadata", {}).get("token_count", 0)

    # 2. Extract from immutable billing database (Commercial ledger)
    if not os.path.exists(DB_PATH):
        return {"status": "ERROR", "message": "Billing ledger database missing."}
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(commercial_billed_tokens) FROM verified_billing;")
    billing_result = cursor.fetchone()
    billing_tokens = billing_result[0] if billing_result and billing_result[0] is not None else 0
    conn.close()

    # 3. Variance Analysis (Materiality check)
    absolute_variance = abs(telemetry_tokens - billing_tokens)
    variance_pct = (absolute_variance / billing_tokens * 100) if billing_tokens > 0 else 0.0
    
    reconciled = variance_pct <= materiality_threshold_pct

    audit_assertion = {
        "ledger_telemetry_tokens": telemetry_tokens,
        "ledger_commercial_billing": billing_tokens,
        "absolute_variance": absolute_variance,
        "variance_percentage": round(variance_pct, 4),
        "materiality_threshold_pct": materiality_threshold_pct,
        "reconciliation_status": "PASSED" if reconciled else "MATERIAL_DISCREPANCY_DETECTED"
    }
    
    return audit_assertion
