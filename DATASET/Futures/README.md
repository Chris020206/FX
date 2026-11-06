# DATASET/Futures

STATUS: DATA NOT IN REPO · TIER SPLIT NOT YET DEFINED

Futures market data for research alongside the GBP/JPY spot data in `DATASET/GBPJPY SPOT/`.

## Why the data files are not on GitHub

The raw files stay on the trader's machine and are excluded by `.gitignore` (`DATASET/**/*.zip`):

- **Size.** GitHub rejects any file over 100 MB. One export is ~727 MB.
- **Licence.** This repository is public. Vendor market data is normally licensed for
  personal use only, and committing it here would redistribute it.

This README is committed in place of the data so the folder exists in the repo and the data can
be re-obtained on another machine.

## Local layout

```
DATASET/Futures/
    README.md                         <- this file (committed)
    6B1!/                             <- local only, not committed
        GLBX-20261106-3AG9TEL8RW.zip  (~74 MB)
        GLBX-20261106-WMK7TMU7AY.zip  (~727 MB)
```

## What the files are

Identified from the filenames only. The contents have not been inspected, so confirm before
relying on any of this:

| Field | Value | Basis |
|---|---|---|
| Instrument | `6B1!`, British pound futures (front month, continuous) | folder name |
| Venue | CME Globex (`GLBX`) | filename prefix |
| Vendor | Databento (filename pattern `GLBX-<date>-<job id>.zip`) | filename pattern, UNVERIFIED |
| Export date | 2026-11-06 | filename |
| Schema, date range, bar size | **unknown** | add when known |

`6B` is GBP/**USD**, not GBP/JPY. It is a different instrument from the spot series, so no
spot calibration carries over to it automatically.

## Tier discipline: decide before the first look

The spot data is split into Tier 1 (calibration), Tier 2 (held out) and Tier 3 (not in repo).
**The futures data has no split yet.** Until the trader defines one:

- Do not calibrate, tune or fit anything on it.
- Define the tier date ranges first and record them in `Standards/Decision_Log.md` and
  `CLAUDE.md` §4. Data cannot be un-seen, so the split is only free before anyone has looked.
- Note that `Implementation/run_pine_port.py` refuses paths containing "Tier 2" / "Tier 3".
  Futures paths have no tier in their name, so that guard does not protect them.
