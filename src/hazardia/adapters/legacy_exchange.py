"""Non-destructive metadata view of validated legacy CIMA products; never migrate bytes.

All FIRE/FLOOD-specific interpretation belongs here, outside the exchange kernel.
"""
import copy
from hazardia.io import load, sha256, utcnow, write_new
from hazardia.contracts import validate_request, validate_product as validate_legacy_product
from hazardia.exchange import validate_product

VARIABLES = {
    'FIRE_PROBABILITY': ('urn:hazardia:quantity:fire-reached-probability','CUMULATIVE_REACHED_AT_HORIZON',
                         'EMPIRICAL_FREQUENCY','Simulator realizations, not a weather ensemble or calibrated event probability.'),
    'ARRIVAL_TIME': ('urn:hazardia:quantity:earliest-fire-arrival-offset','EARLIEST_REALIZATION_OFFSET_FROM_WINDOW_START',
                     'MINIMUM_OVER_REALIZATIONS','Earliest realization arrival in seconds from window start; masked where not reached, not expected arrival.'),
    'MAXIMUM_DEPTH': ('urn:hazardia:quantity:flood-depth','WINDOW_MAXIMUM',
                       'NOT_QUANTIFIED','Derived from per-reach window-maximum discharge; not instantaneous or observed water depth.'),
}


def known(value, reason):return dict(state='KNOWN',value=value,reason=reason)
def unknown(reason):return dict(state='UNKNOWN',value=None,reason=reason)


def export_legacy_product(root, *, available_at=None):
    """Explicit availability or UNKNOWN for archives; no inferred historical time."""
    from pathlib import Path
    root=Path(root);request=load(root/'request.json');product=load(root/'product.json')
    validate_request(request,root);validate_legacy_product(product,request,root)
    hazard=request['hazard'];domain={'FIRE':'hazardia.wildfire','FLOOD':'hazardia.flood'}[hazard]
    original=request['grid'];grid=copy.deepcopy(original);datum=grid.pop('vertical_datum')
    grid.update(axis_order='X_Y',vertical_datum=unknown('Legacy datum explicitly unknown') if datum.upper().startswith('UNKNOWN') or datum.upper()=='UNSPECIFIED' else known(datum,'Declared legacy grid datum; qualification unchanged'))
    crs=grid['crs'];code=int(crs[5:]) if crs.startswith('EPSG:') and crs[5:].isdigit() else None
    unit='degree' if code==4326 else 'm' if code is not None and (32601<=code<=32660 or 32701<=code<=32760) else None
    grid['horizontal_unit']=known(unit,'Reviewed legacy EPSG grid family') if unit else unknown('CRS units not resolved by this adapter')
    variables=[]
    for layer in product['layers']:
        quantity,support,kind,note=VARIABLES[layer['name']]
        variables.append(dict(id=layer['name'],quantity=quantity,unit=layer['unit'],support=support,
                              uncertainty=dict(kind=kind,members=request['options']['realizations'] if hazard=='FIRE' else None,
                                               calibration=unknown('No scientific calibration established by technical execution'),note=note),
                              asset={k:layer[k] for k in ['path','sha256']},statistics=copy.deepcopy(layer['statistics'])))
    records=[dict(role='legacy_request',asset=dict(path='request.json',sha256=sha256(root/'request.json'))),
             dict(role='legacy_product',asset=dict(path='product.json',sha256=sha256(root/'product.json')))]
    records += [dict(role='input:'+a['role'],asset={k:a[k] for k in ['path','sha256']}) for a in request['assets']]
    engine=product['engine']
    result=dict(schema='hazardia.exchange-product/0.1.0',id=product['job_id'],domain_id=domain,origin='SIMULATED',
                qualification=product['qualification'],grid=grid,
                time=dict(valid_from=product['valid_from'],valid_until=product['valid_until'],source_cutoff=request['snapshot_at'],
                          available_at=known(available_at,'Explicit product publication time supplied by producer') if available_at is not None else unknown('Original product publication time not supplied; file mtime is not provenance')),
                variables=variables,provenance=dict(records=records,license=unknown('Legacy product has no aggregate license; original input metadata and rights remain authoritative'),
                                                    engine=dict(state='KNOWN',reason='Native engine identity from the original product; no physical qualification inferred',name=engine['name'],source_revision=engine['source_commit'],patch_sha256=engine['patch_sha256'])),
                assumptions=copy.deepcopy(product['assumptions'])+[request['mode']+'; exchange metadata does not qualify physics, calibration or operational use'])
    validate_product(result,root);return result


def write_legacy_exchange(root):
    """Only newly executed jobs call this; archives require explicit export."""
    from pathlib import Path
    value=export_legacy_product(root,available_at=utcnow())
    write_new(Path(root)/'exchange-product.json',value)
    return value
