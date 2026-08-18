import sqlite3
import json
import os

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/data/audit_logs.jsonl")
BILLING_DB_PATH = os.getenv("BILLING_DB_PATH", "/app/data/billing_ledger.db")

class DAESGReconciliationControl:
    """
    Second Line of Defence: Performs automated variance reconciliation 
    between operational AI telemetry and enterprise financial ledgers.
    """
    def __init__(self, token_unit_cost: float = 0.00002):
        self.token_unit_cost = token_unit_cost # Cost per token in USD

    def aggregate_runtime_telemetry(self) -> int:
        """Reads permanent audit logs and sums total tokens consumed."""
        total_tokens = 0
        if not os.path.exists(LOG_FILE_PATH):
            return 0
            
        with open(LOG_FILE_PATH, "r") as f:
            for line in f:
                record = json.loads(line.strip())
                if record.get("unit_type") == "tokens":
                    total_tokens += record.get("count", 0)
        return total_tokens

    def get_financial_ledger_cost(self) -> float:
        """Simulates fetching the recorded expense from the financial ERP/billing database."""
        if not os.path.exists(BILLING_DB_PATH):
            return 0.0 # Default if ledger hasn't synced yet
            
        conn = sqlite3.connect(BILLING_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(billed_amount) FROM vendor_invoices")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] is not None else 0.0

    def run_reconciliation_variance_check(self) -> dict:
        """
        Compares operational usage expenditure against financial billing records.
        Flags discrepancies exceeding acceptable audit variance thresholds.
        """
        tokens_consumed = self.aggregate_runtime_telemetry()
        calculated_liability = tokens_consumed * self.token_unit_cost
        recorded_billing_expense = self.get_financial_ledger_cost()

        variance = calculated_liability - recorded_billing_expense
        variance_percentage = (variance / recorded_billing_expense * 100) if recorded_billing_expense > 0 else 0.0

        status = "PASSED_RECONCILIATION"
        if abs(variance_percentage) > 2.0: # 2% materiality threshold
            status = "VARIANCE_THRESHOLD_EXCEEDED"

        return {
            "status": status,
            "operational_tokens": tokens_consumed,
            "calculated_liability_usd": round(calculated_liability, 4),
            "ledger_expense_usd": round(recorded_billing_expense, 4),
            "variance_usd": round(variance, 4),
            "variance_percentage": round(variance_percentage, 2)
        }
