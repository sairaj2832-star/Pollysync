# PolliSync ML workspace

This directory keeps experimentation separate from the deployed API.

## Layout

- data/ documents dataset provenance and later stores ignored local CSV files.
- notebooks/ stores exploration and model-evaluation notebooks.
- models/ documents trained artifacts; generated pickle and joblib files are ignored.
- src/ contains reusable feature and prediction code.

The current predictor is a transparent rule-based baseline so the API contract can be integrated before trained artifacts exist. Replace it with validated models during the ML milestones in the playbook. Never present synthetic-data results as field-validated accuracy.
