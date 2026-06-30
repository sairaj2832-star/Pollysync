"""
process_gbif_data.py
Converts raw GBIF occurrence records into a monthly pollinator-activity index
per species + region. This replaces the hand-guessed thresholds in
pollinator_proxy.py with an actual data-derived signal.

Logic: count how many occurrence records fall in each calendar month for a
given species in a given state. Normalize to get a relative activity score
per month (0-1). The month(s) with peak activity become the predicted
pollinator-peak window for that region.

This is intentionally simple (a histogram, not a trained model) because GBIF
density in India is too sparse for anything more sophisticated to be
trustworthy — a stated limitation, not an oversight.

Usage:
    python process_gbif_data.py
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "gbif_bee_occurrences_maharashtra.csv"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_gbif_file(path: Path) -> pd.DataFrame:
    """
    Loads a GBIF occurrence file. Handles both:
      - the API-pulled CSV (comma-separated, from fetch_gbif_data.py)
      - the manually downloaded "Simple" export (actually tab-separated,
        named occurrence.txt by GBIF, despite being called CSV on the site)
    GBIF's manual TSV exports sometimes have malformed lines (stray tabs/
    newlines inside text fields like 'locality' or 'recordedBy'), so we use
    the python engine with QUOTE_NONE and skip unparseable lines rather than
    crashing on them — losing a handful of bad rows out of thousands is fine
    for this project.
    Also derives 'month' from 'eventDate' if the month column is missing or
    mostly empty, which happens often in manual downloads.
    """
    import csv as csv_module

    df = None
    for sep in ["\t", ","]:
        try:
            df = pd.read_csv(
                path, sep=sep, engine="python",
                quoting=csv_module.QUOTE_NONE,
                on_bad_lines="skip",
            )
            if df.shape[1] > 1:  # confirm we picked the right separator
                break
        except Exception:
            continue

    if df is None or df.shape[1] <= 1:
        raise ValueError(
            f"Could not parse {path} as tab- or comma-separated. "
            f"Open it in a text editor and check the actual delimiter."
        )

    if "species" not in df.columns and "scientificName" in df.columns:
        df["species"] = df["scientificName"]

    if "month" not in df.columns or df["month"].isna().mean() > 0.5:
        if "eventDate" in df.columns:
            parsed = pd.to_datetime(df["eventDate"], errors="coerce")
            df["month"] = parsed.dt.month

    return df


def build_monthly_activity_index(df: pd.DataFrame, min_records_threshold: int = 10) -> pd.DataFrame:
    """
    df must have columns: species, stateProvince, month (1-12; from eventDate).
    Returns a long-format table: species, region, month, record_count,
    activity_score (0-1, normalized within species+region), data_sufficient (bool).
    """
    df = df.dropna(subset=["month"]).copy()
    df["month"] = df["month"].astype(int)
    df["stateProvince"] = df["stateProvince"].fillna("Unknown")

    grouped = (
        df.groupby(["species", "stateProvince", "month"])
        .size()
        .reset_index(name="record_count")
    )

    results = []
    for (species, region), sub in grouped.groupby(["species", "stateProvince"]):
        total = sub["record_count"].sum()
        sufficient = total >= min_records_threshold
        sub = sub.copy()
        sub["activity_score"] = sub["record_count"] / total if total > 0 else 0
        sub["data_sufficient"] = sufficient
        sub["total_records"] = total
        results.append(sub)

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()


def get_peak_month(activity_df: pd.DataFrame, species: str, region: str) -> dict:
    """
    Returns the peak-activity month for a species+region, with a confidence
    flag based on whether enough records exist to trust the estimate.
    """
    sub = activity_df[
        (activity_df["species"] == species) & (activity_df["stateProvince"] == region)
    ]
    if sub.empty:
        return {"species": species, "region": region, "peak_month": None,
                "confidence": "no_data", "total_records": 0}

    peak_row = sub.loc[sub["activity_score"].idxmax()]
    confidence = "medium" if peak_row["data_sufficient"] else "low"
    return {
        "species": species,
        "region": region,
        "peak_month": int(peak_row["month"]),
        "activity_score": float(peak_row["activity_score"]),
        "total_records": int(peak_row["total_records"]),
        "confidence": confidence,
    }


if __name__ == "__main__":
    if not RAW_PATH.exists():
        print(
            f"No raw data found at {RAW_PATH}.\n"
            f"Either run fetch_gbif_data.py, or download manually from "
            f"gbif.org/occurrence/search and save the file to that exact path "
            f"(rename occurrence.txt to gbif_bee_occurrences_maharashtra.csv)."
        )
    else:
        raw_df = load_raw_gbif_file(RAW_PATH)
        print(f"Loaded {len(raw_df)} raw records, columns: {list(raw_df.columns)[:10]}...")

        missing_required = [c for c in ["species", "stateProvince", "month"] if c not in raw_df.columns]
        if missing_required:
            print(f"WARNING: missing expected columns {missing_required}. Check the file format.")

        activity_df = build_monthly_activity_index(raw_df)

        out_path = PROCESSED_DIR / "pollinator_monthly_activity.csv"
        activity_df.to_csv(out_path, index=False)
        print(f"Saved monthly activity index to {out_path}")

        # Example: print peak months for each species/region combo found
        combos = activity_df[["species", "stateProvince"]].drop_duplicates()
        for _, row in combos.iterrows():
            peak = get_peak_month(activity_df, row["species"], row["stateProvince"])
            print(peak)