import json
import os
from datetime import datetime

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/data/audit_logs.jsonl")

class DAESGInstrumentation:
    """
    First Line of Defence: Captures operational telemetry across 
    the three DAESG extraction measurement units (Tokens, Prompts, Time)
    without retaining raw identifiable payloads.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id

    def record_turn(self, unit_type: str, classification: str, count: int, metadata: dict = None):
        """
        Logs extraction units permanently into the append-only sandbox storage.
        
        :param unit_type: 'tokens' (data-commons), 'prompts' (attentional), or 'time' (wellbeing)
        :param classification: 'user_initiated' vs 'model_initiated'
        :param count: Numeric quantity of the unit
        :param metadata: Contextual non-PII indicators
        """
        if unit_type not in ["tokens", "prompts", "time"]:
            raise ValueError("Invalid DAESG measurement unit taxonomy.")

        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "unit_type": unit_type,
            "classification": classification,
            "count": count,
            "metadata": metadata or {}
        }

        # Append-only write ensures logs are kept permanently until manual purge
        with open(LOG_FILE_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
            
        return {"status": "LOGGED_PERMANENTLY", "unit": unit_type, "count": count}
