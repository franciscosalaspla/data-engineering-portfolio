from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def landing_to_bronze(run_id):
    source, target = ROOT / "data/landing", ROOT / "data/bronze"
    target.mkdir(parents=True, exist_ok=True)
    counts = {}
    for path in sorted(source.glob("*.csv")):
        frame = pd.read_csv(path)
        frame["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()
        frame["source_file"] = path.name
        frame["pipeline_run_id"] = run_id
        frame.to_parquet(target / f"{path.stem}.parquet", index=False)
        counts[path.stem] = len(frame)
    return counts
