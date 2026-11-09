"""Per-resource receipts from the same pinned upstream rasterizers, not efficacy claims."""
import hashlib,json
import numpy as np
from shapely.geometry import LineString,Polygon
from propagator.io.actions import ACTION_CLASSES,build_mask

def action_receipt(resource,geo,vegetation,non_vegetated):
    points=[(p[1],p[0]) for p in resource.get('line',resource.get('area'))]
    geometry=LineString(points) if 'line' in resource else Polygon(points)
    base=build_mask([geometry],geo,src_epsg=4326)
    effect=resource.get('effect','native')
    moisture=None
    if effect=='fuel_removal':affected=base
    else:
        action=ACTION_CLASSES[resource['category']](geometries=[geometry],epsg=4326)
        moisture=action.rasterize_action_moisture(geo)
        fuel=action.rasterize_action_fuel(geo,non_vegetated)
        affected=np.zeros(vegetation.shape,dtype=bool)
        if moisture is not None:affected|=np.isfinite(moisture)&(moisture!=0)
        if fuel is not None:affected|=np.isfinite(fuel)
    values=moisture[affected] if moisture is not None else None
    return dict(resource_id=resource['id'],category=resource['category'],effect=effect,
                input_sha256=hashlib.sha256(json.dumps(resource,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                geometry_cells=int(base.sum()),affected_cells=int(affected.sum()),
                initial_fuel_cells=int(np.count_nonzero(affected&(vegetation!=non_vegetated))),
                added_moisture_percent_range=[float(np.nanmin(values)),float(np.nanmax(values))] if values is not None and values.size else None,
                interpretation='Native input footprint; initial fuel is not the active fire front or measured suppression efficacy')
