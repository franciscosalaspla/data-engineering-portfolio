import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ADFStyleOrchestrator:
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.activities = []

    def activity(self, name, dependency, function, *args):
        started = time.perf_counter()
        try:
            output = function(*args)
            status, error = "SUCCEEDED", None
            return output
        except Exception as exc:
            status, error = "FAILED", str(exc)
            raise
        finally:
            self.activities.append({"activity": name, "depends_on": dependency, "status": status, "duration_seconds": round(time.perf_counter() - started, 4), "error": error})

    def write_summary(self, final_status):
        summary = {"pipeline": "pl_local_adf_databricks_medallion", "pipeline_run_id": self.run_id, "run_timestamp_utc": datetime.now(timezone.utc).isoformat(), "final_status": final_status, "activities": self.activities}
        out = ROOT / "output"
        out.mkdir(exist_ok=True)
        (out / "pipeline_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
