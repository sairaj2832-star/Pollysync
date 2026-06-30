"""
fetch_gbif_data.py
Pulls pollinator (bee) occurrence records from GBIF for India, by species,
using the GBIF REST API via pygbif. Saves raw results to ml/data/raw/.

This is a synchronous "search" pull (good for a few thousand records, no
auth needed). For very large pulls, GBIF's async "download" API requires a
free account — see notes at the bottom of this file.

Usage:
    python fetch_gbif_data.py
"""

import time
import pandas as pd
from pathlib import Path
from pygbif import occurrences as occ

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Bee species relevant to sunflower and mustard pollination in India.
# Add/remove based on what your literature review turned up.
SPECIES_LIST = [
    "Apis cerana",
    "Apis dorsata",
    "Apis florea",
    "Apis mellifera",
]

COUNTRY = "IN"  # ISO code for India
TARGET_REGION = "Maharashtra"  # narrowed scope per project decision


def _search_with_retry(max_retries=5, base_delay=3, **kwargs):
    """Calls occ.search with exponential backoff on HTTP 429 (rate limit)."""
    for attempt in range(max_retries):
        try:
            return occ.search(**kwargs)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = base_delay * (2 ** attempt)
                print(f"  Rate limited (429). Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded for GBIF request")


def fetch_species_occurrences(species_name: str, country: str = COUNTRY,
                               state_province: str = None, limit: int = 300) -> pd.DataFrame:
    """
    Fetches occurrence records for one species, paginating through GBIF's
    search API (max 300 per page). Optionally filtered to a single Indian
    state via state_province (GBIF's stateProvince field is free-text and
    inconsistently filled, so results are filtered client-side after the
    pull rather than relying on a server-side exact match).
    """
    all_records = []
    offset = 0
    page_size = 300

    while True:
        resp = _search_with_retry(
            scientificName=species_name,
            country=country,
            stateProvince=state_province,
            hasCoordinate=True,
            limit=page_size,
            offset=offset,
        )
        results = resp.get("results", [])
        if not results:
            break
        all_records.extend(results)
        offset += page_size
        if offset >= limit or resp.get("endOfRecords", True):
            break
        time.sleep(1.5)  # be polite between pages of the same species

    if not all_records:
        return pd.DataFrame()

    df = pd.json_normalize(all_records)
    keep_cols = [c for c in [
        "species", "scientificName", "decimalLatitude", "decimalLongitude",
        "eventDate", "year", "month", "day", "stateProvince", "locality",
        "basisOfRecord", "recordedBy",
    ] if c in df.columns]
    df = df[keep_cols]

    if state_province and "stateProvince" in df.columns:
        df = df[df["stateProvince"].astype(str).str.contains(state_province, case=False, na=False)]

    return df


if __name__ == "__main__":
    combined = []
    print(f"Region: {TARGET_REGION} | Country: {COUNTRY}\n")

    for sp in SPECIES_LIST:
        print(f"Fetching {sp} (Maharashtra)...")
        df = fetch_species_occurrences(sp, state_province=TARGET_REGION, limit=1000)
        print(f"  -> {len(df)} records after state filter")
        if not df.empty:
            combined.append(df)
        time.sleep(2)  # be polite between species to avoid 429s

    if combined:
        full_df = pd.concat(combined, ignore_index=True)
        out_path = OUTPUT_DIR / "gbif_bee_occurrences_maharashtra.csv"
        full_df.to_csv(out_path, index=False)
        print(f"\nSaved {len(full_df)} total records to {out_path}")

        print("\nPer-species record counts (use this to pick which species has enough data):")
        print(full_df["species"].value_counts())
    else:
        print(
            "\nNo records found for Maharashtra via the API filter.\n"
            "Try the web UI instead: gbif.org/occurrence/search\n"
            "  -> filter: scientificName=Apis cerana, country=India, "
            "stateProvince=Maharashtra, hasCoordinate=true\n"
            "GBIF's stateProvince field is inconsistently filled by data "
            "providers, so the API filter can under-return. The web UI map "
            "view lets you draw a polygon around Maharashtra instead, which "
            "is more reliable."
        )

# ---------------------------------------------------------------------------
# NOTE on the alternative "download" API (for large pulls):
# If you need the full dataset (tens of thousands of records) rather than a
# capped search, use occ.download() with a free GBIF account:
#
#   from pygbif import occurrences as occ
#   occ.download.credentials(user="...", pwd="...", email="...")
#   key = occ.download([
#       "country = IN",
#       "taxonKey = 1341976",  # Apis genus taxonKey, look up via species.name_backbone
#       "hasCoordinate = TRUE",
#   ])
#   # then occ.download_get(key) once GBIF emails that it's ready
# ---------------------------------------------------------------------------