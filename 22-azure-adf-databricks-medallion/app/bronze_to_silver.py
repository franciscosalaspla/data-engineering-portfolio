from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def bronze_to_silver():
    source, target = ROOT / "data/bronze", ROOT / "data/silver"
    target.mkdir(parents=True, exist_ok=True)
    counts = {}
    for path in sorted(source.glob("*.parquet")):
        frame = pd.read_parquet(path).drop_duplicates()
        text_cols = frame.select_dtypes(include="object").columns
        for col in text_cols:
            frame[col] = frame[col].astype(str).str.strip()
        frame.to_parquet(target / path.name, index=False)
        counts[path.stem] = len(frame)
    return counts
