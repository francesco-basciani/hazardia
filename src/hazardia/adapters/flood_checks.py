"""Acceptance of a genuinely empty native REFlEx optimizer case, not a fallback."""
import math
from hazardia.io import HazardError

def verify_dry_map(eligible_streams,values):
    if eligible_streams!=0:raise HazardError('INVALID_OUTPUT','Empty REFlEx optimizer table despite eligible runoff')
    seen=False
    for value in values:
        seen=True
        if not math.isfinite(float(value)) or float(value)!=0:raise HazardError('INVALID_OUTPUT','Dry REFlEx result must contain valid native zero depths')
    if not seen:raise HazardError('INVALID_OUTPUT','Dry REFlEx raster has no valid cells')
