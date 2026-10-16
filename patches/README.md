# REFlEx compatibility patch

`reflex-hand-boundary.patch` is a declared two-line modification of REFlEx, upstream https://github.com/c-hydro/reflex at `0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd`.

It retains a one-cell working halo for HAND and fixes merge extent/resolution to the authoritative grid. The original source remains unchanged; `configure_runtime.py` creates a separate compatibility copy. Original upstream failures and limitations are recorded in the research ledger. This is not an upstream-endorsed or calibrated model release.

Upstream copyright/licence notices remain applicable; the EUPL-1.2 text is in `licenses/EUPL-1.2.txt`. This patch notice does not change the licence of other HAZARDIA-authored files. The bootstrap downloads all upstream source separately, with pinned commit/archive SHA-256, preserving its own notices.
