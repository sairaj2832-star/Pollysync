"""
test_sensitivity.py
Demonstrates the core value prop: as environment parameters shift (e.g.
a warming trend), the predicted flowering date moves relative to the
pollinator peak, changing gap_days and the alert. Run this to show judges
the model actually responds to changing conditions, not just static input.

Usage: python test_sensitivity.py
"""

from datetime import date, timedelta
import pandas as pd
from mismatch import predict_mismatch


def make_temp_series(sowing, n_days, base_temp):
    return pd.DataFrame({
        "date": [sowing + timedelta(days=i) for i in range(n_days)],
        "T2M_MAX": [base_temp + 5] * n_days,
        "T2M_MIN": [base_temp - 5] * n_days,
    })


if __name__ == "__main__":
    sowing = date(2025, 6, 15)
    print("Sunflower, Maharashtra — varying base temperature:\n")

    for base_temp in [20, 23, 26, 29, 32]:
        temp_df = make_temp_series(sowing, 150, base_temp)
        result = predict_mismatch(
            crop="sunflower", region="Maharashtra",
            sowing_date=sowing, temp_df=temp_df,
        )
        print(
            f"base_temp={base_temp}C -> flowering={result['predicted_flowering_date']}, "
            f"pollinator_peak={result['predicted_pollinator_peak_date']}, "
            f"gap_days={result['gap_days']}, alert={result['alert'][:70]}..."
        )

    print("\nMustard, Rajasthan — varying base temperature:\n")
    sowing_m = date(2025, 10, 20)

    for base_temp in [10, 13, 16, 19, 22]:
        temp_df = make_temp_series(sowing_m, 150, base_temp)
        result = predict_mismatch(
            crop="mustard", region="Rajasthan",
            sowing_date=sowing_m, temp_df=temp_df,
        )
        print(
            f"base_temp={base_temp}C -> flowering={result['predicted_flowering_date']}, "
            f"pollinator_peak={result['predicted_pollinator_peak_date']}, "
            f"gap_days={result['gap_days']}, alert={result['alert'][:70]}..."
        )