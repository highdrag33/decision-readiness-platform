# Architecture

## Boundaries

1. `NWSClient` owns HTTP communication and fails explicitly on non-success responses.
2. The ingestion pipeline timestamps and preserves the complete source response before transformation.
3. `normalize_alerts()` validates the expected GeoJSON structure and explodes each alert’s SAME codes into county-level records.
4. `Facility` validates the synthetic planning inputs independently of weather data.
5. DuckDB persists both domains and exposes `facility_risk` as a transparent SQL view.
6. The CSV export is a portable decision-product boundary for later dashboards or analysis.

## Join strategy

NWS alert properties can include six-digit SAME codes such as `037129`. For U.S. counties, the first zero is removed to produce the five-digit county FIPS code `37129`. Synthetic facilities use the same five-digit key.

Alerts without supported county SAME codes remain preserved in raw storage but do not produce county records. This prevents an unreliable text join against `areaDesc`.

## Idempotency

Raw filenames use the UTC retrieval timestamp. Curated builds drop and recreate snapshot tables in the selected DuckDB file, so rerunning the same input produces the same logical state rather than duplicating rows.

## Atomic raw writes

Raw JSON is first written to a `.tmp` path and then moved to the final `.json` path. A process interrupted during serialization is therefore less likely to leave a partial file that appears complete.

## Testing strategy

- Client unit tests replace only the network transport with `httpx.MockTransport`.
- Pure transformations use controlled JSON fixtures.
- Filesystem tests use pytest’s isolated `tmp_path` fixture.
- The end-to-end test builds an actual temporary DuckDB database and queries the resulting risk view.
