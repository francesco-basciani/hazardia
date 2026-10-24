"""Strict exchange metadata, independent of hazard IDs and native data formats."""
import json
import math
from pathlib import Path
from jsonschema import Draft7Validator
from hazardia.io import HazardError, timestamp, verify_asset

MAX_BYTES = 262144
SCHEMAS = Path(__file__).parents[1] / 'schemas'


def require(condition, message):
    if not condition:raise HazardError('INVALID_EXCHANGE', message)


def _local_schema(document):
    # jsonschema 3.2 in the supported VM mishandles fragment refs with URN IDs.
    # Expand only our local definitions, without invoking any remote resolver.
    definitions=document.get('definitions',{})
    def expand(value, stack=()):
        if isinstance(value,dict):
            if '$ref' in value:
                ref=value['$ref'];require(set(value)=={'$ref'} and ref.startswith('#/definitions/'),'Only local schema references are supported')
                name=ref[len('#/definitions/'):];require(name in definitions and name not in stack,'Missing or cyclic schema definition')
                return expand(definitions[name],stack+(name,))
            return {k:expand(v,stack) for k,v in value.items()}
        if isinstance(value,list):return [expand(v,stack) for v in value]
        return value
    return expand({k:v for k,v in document.items() if k!='definitions'})


def _validate(value, kind):
    try:
        raw=json.dumps(value,allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError) as exc:
        raise HazardError('INVALID_EXCHANGE','Finite JSON metadata required') from exc
    require(len(raw)<=MAX_BYTES,'Exchange metadata exceeds 256 KiB')
    schema=_local_schema(json.loads((SCHEMAS/(kind+'.schema.json')).read_bytes()))
    errors=sorted(Draft7Validator(schema).iter_errors(value),key=lambda e:str(list(e.path)))
    require(not errors, str(list(errors[0].path))+': '+errors[0].message if errors else '')
    g=value['grid'];a,b,c,d,e,f=g['transform']
    require(a>0 and e<0 and b==d==0,'Regular north-up grid required; no implicit reprojection')
    require(g['horizontal_unit']['state']!='NOT_APPLICABLE','Grid scale must be known or unknown')
    t=value['time'];require(timestamp(t['valid_from'])<timestamp(t['valid_until']),'Nonempty UTC window required')
    names=[v['id'] for v in value['variables']]
    require(len(names)==len(set(names)),'Unique variable IDs required')
    return value


def validate_product(value, root=None):
    _validate(value,'exchange_product')
    t=value['time'];timestamp(t['source_cutoff'])
    if t['available_at']['state']=='KNOWN':
        available=timestamp(t['available_at']['value'])
        require(timestamp(t['source_cutoff'])<=available,'Product availability precedes source cutoff')
    for v in value['variables']:
        s=v['statistics'];require(s['minimum']<=s['maximum'] and s['positive_cells']<=s['valid_cells']<=math.prod(value['grid']['shape']),'Invalid grid statistics')
        if root is not None:verify_asset(root,v['asset'])
    records=value['provenance']['records'];roles=[r['role'] for r in records]
    require(len(roles)==len(set(roles)),'Unique provenance roles required')
    if root is not None:
        for record in records:verify_asset(root,record['asset'])
    return value


def validate_requirement(value):
    _validate(value,'exchange_requirement');timestamp(value['time']['as_of'])
    return value
