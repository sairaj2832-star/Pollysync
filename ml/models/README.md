# Model artifacts

The `.pkl` files in this directory are tracked in git and deployed to Render automatically with the backend service.

## Files

| File | Description |
|------|-------------|
| `flowering_model.pkl` / `flowering_scaler.pkl` | Flowering window prediction — general model |
| `flowering_model_mh.pkl` / `flowering_scaler_mh.pkl` | Flowering window prediction — Maharashtra-specific (trained on 1545 real MH rows) |
| `psi_model.pkl` / `psi_scaler.pkl` | Pollination Suitability Index — general model |
| `psi_model_mh.pkl` / `psi_scaler_mh.pkl` | Pollination Suitability Index — Maharashtra-specific |
| `risk_model.pkl` / `risk_scaler.pkl` | Risk level classification — general model |
| `risk_model_mh.pkl` / `risk_scaler_mh.pkl` | Risk level classification — Maharashtra-specific |

## Updating models

To promote a retrained model, replace the `.pkl` files and commit. Render will pick them up on next deploy.

When adding a new model variant, add a model card here describing:
- Training data source and size
- Evaluation metrics
- Expected input features
- Known limitations
