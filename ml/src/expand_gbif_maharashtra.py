"""
expand_gbif_maharashtra.py
Expands GBIF bee data for Maharashtra: all Apidae species, not just 4 hardcoded.
Computes richness + Shannon diversity index per district.
Falls back to literature-based estimates when GBIF data is sparse.

Output: ml/data/raw/gbif_maharashtra_all_species.csv
        ml/data/processed/maharashtra_bee_diversity.csv

Usage:
    python expand_gbif_maharashtra.py
"""

from pathlib import Path
import time
import numpy as np
import pandas as pd
from pygbif import occurrences as occ
from pygbif import species as species_api

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MAHARASHTRA_DISTRICTS = [
    {"name": "nashik",     "lat": 19.99, "lon": 73.79, "area_km2": 15530},
    {"name": "pune",       "lat": 18.52, "lon": 73.86, "area_km2": 15642},
    {"name": "solapur",    "lat": 17.67, "lon": 75.91, "area_km2": 14895},
    {"name": "aurangabad", "lat": 19.88, "lon": 75.32, "area_km2": 10107},
    {"name": "nagpur",     "lat": 21.15, "lon": 79.09, "area_km2": 9892},
    {"name": "amravati",   "lat": 20.93, "lon": 77.75, "area_km2": 12235},
    {"name": "kolhapur",   "lat": 16.70, "lon": 74.24, "area_km2": 7685},
    {"name": "satara",     "lat": 17.69, "lon": 73.99, "area_km2": 10484},
    {"name": "jalgaon",    "lat": 21.01, "lon": 75.56, "area_km2": 11765},
    {"name": "latur",      "lat": 18.40, "lon": 76.56, "area_km2": 7157},
]

# Fallback diversity estimates based on published studies:
# - Abrol (2012) "Pollination Biology" for India bee diversity patterns
# - Maharashtra Krishi reports on native pollinator diversity
# - ICRISAT crop-pollinator studies in semi-arid tropics
DISTRICT_DIVERSITY_FALLBACK = {
    "nashik":     {"expected_richness": 8,  "shannon": 1.6, "note": "Western Ghats foothills, high diversity"},
    "pune":       {"expected_richness": 7,  "shannon": 1.5, "note": "Urban-agriculture mosaic"},
    "solapur":    {"expected_richness": 4,  "shannon": 1.0, "note": "Semi-arid Deccan, lower diversity"},
    "aurangabad": {"expected_richness": 5,  "shannon": 1.2, "note": "Marathwada plateau, moderate"},
    "nagpur":     {"expected_richness": 6,  "shannon": 1.4, "note": "Vidarbha, forest-agriculture mix"},
    "amravati":   {"expected_richness": 6,  "shannon": 1.3, "note": "Vidarbha cotton belt"},
    "kolhapur":   {"expected_richness": 9,  "shannon": 1.7, "note": "Western Ghats, high rainfall, high diversity"},
    "satara":     {"expected_richness": 8,  "shannon": 1.6, "note": "Western Ghats escarpment"},
    "jalgaon":    {"expected_richness": 5,  "shannon": 1.1, "note": "Khandesh plains, hot semi-arid"},
    "latur":      {"expected_richness": 4,  "shannon": 1.0, "note": "Marathwada, rain-shadow zone"},
}

# Known bee species in Maharashtra from literature + GBIF pilot
KNOWN_APIDAE_MAHARASHTRA = [
    "Apis cerana", "Apis dorsata", "Apis florea", "Apis mellifera",
    "Amegilla zonata", "Amegilla confusa", "Amegilla cingulata",
    "Xylocopa violacea", "Xylocopa latipes", "Xylocopa fenestrata",
    "Xylocopa rufa", "Xylocopa pubescens",
    "Ceratina hieroglyphica", "Ceratina smaragdula", "Ceratina binghami",
    "Nomia curvipes", "Nomia thoracica",
    "Megachile lanata", "Megachile disjuncta", "Megachile anthracina",
    "Tetralonia sp.", "Thyreus ramosellus",
    "Trigona iridipennis",
]


def _search_with_retry(max_retries=3, base_delay=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return occ.search(**kwargs)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = base_delay * (2 ** attempt)
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


def fetch_apidae_for_maharashtra() -> pd.DataFrame:
    print("Fetching all Apidae occurrences for Maharashtra...")
    all_records = []
    offset = 0
    page_size = 300
    limit = 3000

    while offset < limit:
        try:
            resp = _search_with_retry(
                family="Apidae",
                country="IN",
                stateProvince="Maharashtra",
                hasCoordinate=True,
                limit=page_size,
                offset=offset,
            )
            results = resp.get("results", [])
            if not results:
                break
            all_records.extend(results)
            offset += page_size
            if resp.get("endOfRecords", True):
                break
            time.sleep(1.5)
        except Exception as e:
            print(f"  GBIF search error: {e}")
            break

    if not all_records:
        return pd.DataFrame()

    df = pd.json_normalize(all_records)
    keep_cols = [c for c in [
        "species", "scientificName", "decimalLatitude", "decimalLongitude",
        "eventDate", "year", "month", "day", "stateProvince", "locality",
        "basisOfRecord", "recordedBy",
    ] if c in df.columns]
    return df[keep_cols] if keep_cols else df


def fetch_per_species_known_list() -> pd.DataFrame:
    print("Fetching known Maharashtra bee species individually...")
    all_dfs = []
    for sp in KNOWN_APIDAE_MAHARASHTRA:
        try:
            time.sleep(1.0)
            resp = _search_with_retry(
                scientificName=sp,
                country="IN",
                stateProvince="Maharashtra",
                hasCoordinate=True,
                limit=200,
            )
            results = resp.get("results", [])
            if results:
                df = pd.json_normalize(results)
                keep_cols = [c for c in [
                    "species", "scientificName", "decimalLatitude", "decimalLongitude",
                    "eventDate", "year", "month", "day", "stateProvince", "locality",
                ] if c in df.columns]
                df = df[keep_cols] if keep_cols else df
                all_dfs.append(df)
                print(f"  {sp}: {len(df)} records")
        except Exception as e:
            print(f"  {sp}: error - {e}")

    if not all_dfs:
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)


def compute_shannon_index(records_df: pd.DataFrame) -> float:
    if records_df.empty or "species" not in records_df.columns:
        return 0.0
    species_counts = records_df["species"].value_counts()
    total = species_counts.sum()
    proportions = species_counts / total
    shannon = -np.sum(proportions * np.log(proportions + 1e-10))
    return round(float(shannon), 4)


def estimate_district_richness(district: dict, df: pd.DataFrame) -> dict:
    lat, lon = district["lat"], district["lon"]
    deg = 0.5

    if not df.empty and "decimalLatitude" in df.columns:
        nearby = df[
            (df["decimalLatitude"].astype(float).between(lat - deg, lat + deg)) &
            (df["decimalLongitude"].astype(float).between(lon - deg, lon + deg))
        ]
        observed_richness = nearby["species"].nunique() if "species" in nearby.columns else 0
        observed_count = len(nearby)
        shannon = compute_shannon_index(nearby)
    else:
        observed_richness = 0
        observed_count = 0
        shannon = 0.0

    fallback = DISTRICT_DIVERSITY_FALLBACK[district["name"]]

    if observed_richness >= 3 and observed_count >= 10:
        richness = observed_richness
        diversity = shannon if shannon > 0 else fallback["shannon"]
        source = "gbif_observed"
        confidence = "high"
    elif observed_richness > 0:
        richness = max(observed_richness, fallback["expected_richness"])
        diversity = shannon if shannon > 0.5 else fallback["shannon"]
        source = "gbif_partial"
        confidence = "medium"
    else:
        richness = fallback["expected_richness"]
        diversity = fallback["shannon"]
        source = "literature_fallback"
        confidence = "low"

    return {
        "district": district["name"],
        "lat": lat,
        "lon": lon,
        "observed_species_richness": observed_richness,
        "observed_record_count": observed_count,
        "estimated_richness": richness,
        "shannon_diversity": diversity,
        "data_source": source,
        "confidence": confidence,
        "note": fallback["note"],
    }


def main():
    print("=" * 60)
    print("MAHARASHTRA BEE DIVERSITY DATA EXPANSION")
    print("=" * 60)

    # Try batch API search for all Apidae
    df_batch = fetch_apidae_for_maharashtra()
    print(f"Batch Apidae search: {len(df_batch)} records")

    # Try per-species search for known Maharashtra species
    df_known = fetch_per_species_known_list()
    print(f"Per-species search: {len(df_known)} records")

    all_records = None
    if not df_batch.empty and not df_known.empty:
        all_records = pd.concat([df_batch, df_known], ignore_index=True)
        all_records = all_records.drop_duplicates(subset=["decimalLatitude", "decimalLongitude", "eventDate", "species"])
    elif not df_batch.empty:
        all_records = df_batch
    elif not df_known.empty:
        all_records = df_known

    if all_records is not None and not all_records.empty:
        raw_path = RAW_DIR / "gbif_bee_occurrences_all_species.csv"
        all_records.to_csv(raw_path, index=False)
        print(f"Saved {len(all_records)} raw records to {raw_path}")

        if "species" in all_records.columns:
            print("\nSpecies breakdown:")
            print(all_records["species"].value_counts().head(20).to_string())
    else:
        print("No GBIF records retrieved via API. Using literature fallback.")

    # Per-district diversity estimates
    district_results = []
    for d in MAHARASHTRA_DISTRICTS:
        result = estimate_district_richness(d, all_records if all_records is not None else pd.DataFrame())
        district_results.append(result)
        print(f"  {result['district']:12s} richness={result['estimated_richness']} "
              f"shannon={result['shannon_diversity']} src={result['data_source']} "
              f"obs={result['observed_record_count']}rec")

    df_district = pd.DataFrame(district_results)
    diversity_path = PROCESSED_DIR / "maharashtra_bee_diversity.csv"
    df_district.to_csv(diversity_path, index=False)
    print(f"\nSaved district diversity estimates to {diversity_path}")

    print("\nSummary:")
    for _, r in df_district.iterrows():
        print(f"  {r['district']:12s} -> {r['estimated_richness']} species, "
              f"Shannon={r['shannon_diversity']:.2f} [{r['data_source']}]")

    print("=" * 60)


if __name__ == "__main__":
    main()
