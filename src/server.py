from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from instrumentation import DAESGInstrumentation

app = FastAPI(title="DAESG Technical Companion POC - Telemetry Gateway")

class TurnRequest(BaseModel):
    session_id: str
    unit_type: str        # "tokens", "prompts", or "time"
    classification: str   # "user_initiated" or "model_initiated"
    count: int
    metadata: dict = None

@app.post("/v1/telemetry/record")
def record_extraction_turn(payload: TurnRequest):
    """
    Ingests runtime extraction metrics and records them permanently 
    to the append-only audit log sandbox.
    """
    try:
        tracker = DAESGInstrumentation(session_id=payload.session_id)
        result = tracker.record_turn(
            unit_type=payload.unit_type,
            classification=payload.classification,
            count=payload.count,
            metadata=payload.metadata
        )
        return {"status": "SUCCESS", "audit_trail": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
