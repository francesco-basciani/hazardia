"""Read-only descriptions of existing domains; never dispatch or import adapters.

Discovery is opt-in, not part of web/worker startup or request admission. Digests
check bundled bytes, not publisher authenticity or scientific qualification.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from types import MappingProxyType

from jsonschema import Draft7Validator
from hazardia import __version__
from hazardia.io import HazardError

ROOT = Path(__file__).parent
MAX_DESCRIPTOR_BYTES = 16384
MAX_PACKAGES = 16
# Reviewed local references only: these strings are metadata, never imported.
APPROVED_MODELS = MappingProxyType({
    'FIRE': (('PROPAGATOR', 'hazardia.adapters.workers.fire:run',
              '48b45078093692aa8dcca98f51849a5fbcd981a5'),),
    'FLOOD': (('HMC', 'hazardia.adapters.workers.flood:run',
               'e6e95ecbc794431c4e6d09a81b3292704f3cca42'),
              ('REFLEX', 'hazardia.adapters.workers.flood:run',
               '0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd')),
})


def reject(code, message):
    raise HazardError(code, message)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            reject('PACKAGE_INVALID', 'Duplicate JSON field: ' + key)
        result[key] = value
    return result


@dataclass(frozen=True)
class DomainPackage:
    package_id: str
    package_version: str
    legacy_hazard: str
    digest: str
    _json: str

    def describe(self):
        """Return an independent JSON view; caller edits cannot mutate the catalog."""
        return dict(json.loads(self._json), digest=self.digest)


def parse_descriptor(raw, expected_digest, *, core_version=__version__):
    """Validate bounded bytes, identity and approved bindings, without execution."""
    if not isinstance(raw, bytes) or len(raw) > MAX_DESCRIPTOR_BYTES:
        reject('PACKAGE_SIZE', 'Descriptor exceeds bounded byte input')
    digest = sha256(raw).hexdigest()
    if digest != expected_digest:
        reject('PACKAGE_DIGEST', 'Descriptor bytes differ from the reviewed digest')
    try:
        value = json.loads(raw, object_pairs_hook=_unique_pairs,
                           parse_constant=lambda _: reject('PACKAGE_INVALID', 'Nonfinite JSON'))
    except (ValueError, UnicodeError, RecursionError) as exc:
        reject('PACKAGE_INVALID', 'Invalid descriptor JSON: ' + type(exc).__name__)
    schema = json.loads((ROOT / 'schemas/domain_package.schema.json').read_bytes())
    errors = sorted(Draft7Validator(schema).iter_errors(value), key=lambda e: str(list(e.path)))
    if errors:
        reject('PACKAGE_INVALID', str(list(errors[0].path)) + ': ' + errors[0].message)
    if core_version not in value['core_versions']:
        reject('PACKAGE_CORE_VERSION', 'Core version is not explicitly supported')
    hazard = value['legacy_hazard']
    bindings = tuple((m['engine_ref'], m['adapter_ref'], m['source_revision']) for m in value['models'])
    if bindings != APPROVED_MODELS[hazard]:
        reject('PACKAGE_BINDING', 'Unknown or changed model/adapter/revision binding')
    expected_id = 'hazardia.wildfire' if hazard == 'FIRE' else 'hazardia.flood'
    if value['package_id'] != expected_id:
        reject('PACKAGE_BINDING', 'Existing hazard identity must be preserved')
    expected_contracts = ['simulation_request', 'hazard_product']
    if [c['kind'] for c in value['contracts']] != expected_contracts:
        reject('PACKAGE_CONTRACT', 'Both existing boundaries are required once')
    for c in value['contracts']:
        expected = 'hazardia.contracts:' + ('validate_request' if c['kind'] == 'simulation_request' else 'validate_product')
        legacy = json.loads((ROOT / 'schemas' / (c['kind'] + '.schema.json')).read_bytes())
        versions = legacy['properties']['schema_version']
        supported = versions.get('enum', [versions.get('const')])
        if c['validator_ref'] != expected or any(v not in supported for v in c['versions']):
            reject('PACKAGE_CONTRACT', 'Unknown validator or unsupported contract version')
    policies = ['decision_problem/0.5.0'] + (['FIRE_IDEAL_ASSIGNMENT/0.6.0'] if hazard == 'FIRE' else [])
    if value['decision']['policy_refs'] != policies:
        reject('PACKAGE_POLICY', 'Unknown or cross-domain decision policy')
    return DomainPackage(value['package_id'], value['package_version'], hazard, digest,
                         json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False))


class DomainCatalog:
    """Immutable metadata lookup. No eligibility, execution or authorization API."""
    def __init__(self, packages):
        entries = tuple(packages)
        if len(entries) > MAX_PACKAGES or any(not isinstance(p, DomainPackage) for p in entries):
            reject('PACKAGE_INVALID', 'Bounded validated package set required')
        ids = [p.package_id for p in entries]
        hazards = [p.legacy_hazard for p in entries]
        if len(set(ids)) != len(ids) or len(set(hazards)) != len(hazards):
            reject('PACKAGE_COLLISION', 'Duplicate package identity or legacy hazard')
        self._entries = MappingProxyType({p.package_id: p for p in sorted(entries, key=lambda p: p.package_id)})

    def get(self, package_id):
        try:
            return self._entries[package_id]
        except KeyError:
            reject('PACKAGE_NOT_FOUND', 'Unknown local package')

    def describe(self):
        return dict(schema='hazardia.domain-catalog/0.1.0', mode='READ_ONLY_DESCRIPTIONS',
                    packages=[p.describe() for p in self._entries.values()],
                    runtime_assessed=False, data_assessed=False, dispatch_changed=False)


def discover():
    """Only bundled allowlisted filenames; no directory scan, network or importlib."""
    index = json.loads((ROOT / 'domain_packages/index.json').read_bytes())
    if set(index) != {'wildfire.json', 'flood.json'}:
        reject('PACKAGE_INVALID', 'Bundled index must name the two reviewed packages')
    packages = []
    for filename, digest in sorted(index.items()):
        with (ROOT / 'domain_packages' / filename).open('rb') as stream:
            raw = stream.read(MAX_DESCRIPTOR_BYTES + 1)
        packages.append(parse_descriptor(raw, digest))
    return DomainCatalog(packages)


def main():
    try:
        print(json.dumps(discover().describe(), ensure_ascii=False, allow_nan=False))
        return 0
    except (HazardError, OSError, ValueError) as exc:
        print(json.dumps(dict(status='ERROR', code=getattr(exc, 'code', 'PACKAGE_IO'), message=str(exc))))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
