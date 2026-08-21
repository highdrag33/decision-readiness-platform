# Data Card

## National Weather Service alerts

- **Source:** `https://api.weather.gov/alerts/active`
- **Owner:** National Oceanic and Atmospheric Administration / National Weather Service
- **Format:** GeoJSON feature collection
- **Retrieval filter:** NWS area code, default `NC`
- **Refresh behavior:** On demand in the current MVP
- **Preservation:** Complete source response stored as timestamped raw JSON

Selected fields include alert ID, event, severity, certainty, urgency, area description, effective time, expiration time, and SAME county codes.

### Known limitations

- Active-alert counts can legitimately be zero.
- Not all alerts provide county SAME codes or geometry.
- One alert can affect multiple counties and therefore produces multiple normalized records.
- Categories can include `Unknown` or future values; unrecognized severity values receive rank zero while their original text is preserved.
- API availability and source-schema changes remain external dependencies.

## Synthetic facilities

- **Source:** Authored specifically for this demonstration
- **File:** `data/sample/facilities.csv`
- **Geography:** Fictional facilities located in real North Carolina counties
- **Measures:** On-hand units, daily demand, and safety-stock days

Facility names, inventory, demand, and targets are fictional. They are designed to exercise the data model and risk calculation, not represent actual infrastructure or readiness.

## Derived facility risk

`facility_risk` joins facility county FIPS codes to active alert–county records and calculates days of supply, supply status, weather exposure, risk score, and risk band.

The score is a transparent portfolio heuristic, not a statistically calibrated or operationally approved model. Appropriate next steps would include stakeholder elicitation, sensitivity analysis, backtesting, and uncertainty modeling.
