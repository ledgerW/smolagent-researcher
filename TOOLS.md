# 🛠️ Research Tools

This document lists the available tools and their usage.

## GDELT V2

### `query_gdelt_v2_doc`
```python
query_gdelt_v2_doc(query: str, mode: str = "TimelineTone", start: str | None = None, end: str | None = None) -> dict
```
Queries the GDELT V2 DOC API and returns a dictionary of results.

### `query_gdelt_v2_gkg`
```python
query_gdelt_v2_gkg(query: str, themes: list[str] | None = None) -> dict
```
Queries the GDELT V2 GKG API.

## GDELT V3

### `query_gdelt_v3_entities`
```python
query_gdelt_v3_entities(start: str, end: str, query: str) -> dict
```
Retrieves entity data from the experimental GDELT V3 API.

### `query_gdelt_v3_events`
```python
query_gdelt_v3_events(start: str, end: str, query: str) -> dict
```
Retrieves event data from the experimental GDELT V3 API.


