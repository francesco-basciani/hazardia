"""Exact metadata compatibility only. UNKNOWN never grants composition/execution."""
from hazardia.exchange.contracts import validate_product, validate_requirement
from hazardia.io import timestamp


def check_compatibility(product, requirement, *, root=None):
    validate_product(product,root);validate_requirement(requirement)
    issues=[]
    def issue(code,field):issues.append(dict(code=code,field=field))
    for field in ['domain_id']:
        if product[field]!=requirement[field]:issue('MISMATCH',field)
    if product['origin'] not in requirement['allowed_origins']:issue('MISMATCH','origin')
    if product['qualification'] not in requirement['allowed_qualifications']:issue('MISMATCH','qualification')
    for field in ['shape','crs','axis_order','transform','nodata']:
        if product['grid'][field]!=requirement['grid'][field]:issue('MISMATCH','grid.'+field)
    for field in ['horizontal_unit','vertical_datum']:
        actual=product['grid'][field];expected=requirement['grid'][field]
        # Explicit consumer waiver, not an inferred match of unknown references.
        if field=='vertical_datum' and expected['state']=='NOT_APPLICABLE':continue
        if actual['state']!='KNOWN' or expected['state']!='KNOWN':issue('UNKNOWN','grid.'+field)
        elif actual['value']!=expected['value']:issue('MISMATCH','grid.'+field)
    for field in ['valid_from','valid_until']:
        # Window maxima/cumulative quantities cannot be reused for a sub-window.
        if timestamp(product['time'][field])!=timestamp(requirement['time'][field]):issue('MISMATCH','time.'+field)
    cutoff=timestamp(requirement['time']['as_of']);t=product['time']
    if timestamp(t['source_cutoff'])>cutoff:issue('MISMATCH','time.source_cutoff')
    if t['available_at']['state']!='KNOWN':issue('UNKNOWN','time.available_at')
    else:
        available=timestamp(t['available_at']['value'])
        if available>cutoff:issue('MISMATCH','time.available_at')
        elif (cutoff-available).total_seconds()>requirement['maximum_age_s']:issue('MISMATCH','freshness')
    variables={v['id']:v for v in product['variables']}
    for needed in requirement['variables']:
        actual=variables.get(needed['id'])
        if actual is None:issue('MISMATCH','variables.'+needed['id']);continue
        for field in ['quantity','unit','support']:
            if actual[field]!=needed[field]:issue('MISMATCH',needed['id']+'.'+field)
        if actual['uncertainty']['kind'] not in needed['accepted_uncertainty']:issue('MISMATCH',needed['id']+'.uncertainty')
        if needed['require_known_calibration'] and actual['uncertainty']['calibration']['state']!='KNOWN':issue('UNKNOWN',needed['id']+'.calibration')
        minimum=needed['minimum_members'];members=actual['uncertainty']['members']
        if minimum is not None:
            if members is None:issue('UNKNOWN',needed['id']+'.members')
            elif members<minimum:issue('MISMATCH',needed['id']+'.members')
    if requirement['require_known_license'] and product['provenance']['license']['state']!='KNOWN':issue('UNKNOWN','provenance.license')
    status='INCOMPATIBLE' if any(i['code']=='MISMATCH' for i in issues) else 'UNKNOWN' if issues else 'COMPATIBLE'
    return dict(status=status,issues=issues,asset_hashes_verified=root is not None,
                scope='METADATA_COMPATIBILITY_ONLY_NO_CONVERSION_OR_EXECUTION',operationally_approvable=False)
