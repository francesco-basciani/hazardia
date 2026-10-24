"""Descriptor metadata tests; no simulated output is evidence of native physics."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from hazardia.io import HazardError
from hazardia.package_catalog import (ROOT, MAX_DESCRIPTOR_BYTES, DomainCatalog,
                                     discover, parse_descriptor)


class PackageCatalogTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads((ROOT / 'domain_packages/wildfire.json').read_text())

    def parse(self, value):
        raw = json.dumps(value).encode()
        return parse_descriptor(raw, hashlib.sha256(raw).hexdigest())

    def rejected(self, value, code):
        with self.assertRaises(HazardError) as caught:
            self.parse(value)
        self.assertEqual(caught.exception.code, code)

    def test_existing_domains_only_and_explicit_unknowns(self):
        result = discover().describe()
        self.assertEqual([v['legacy_hazard'] for v in result['packages']], ['FLOOD', 'FIRE'])
        for v in result['packages']:
            self.assertEqual(v['qualification']['runtime_availability'], 'NOT_ASSESSED')
            self.assertEqual(v['qualification']['data_availability'], 'NOT_ASSESSED')
            self.assertEqual(v['qualification']['operational_authorization'], 'NOT_GRANTED')
        self.assertFalse(result['dispatch_changed'])

    def test_digest_drift_and_bounded_input(self):
        raw = json.dumps(self.value).encode()
        with self.assertRaises(HazardError) as c:
            parse_descriptor(raw, '0' * 64)
        self.assertEqual(c.exception.code, 'PACKAGE_DIGEST')
        with self.assertRaises(HazardError) as c:
            parse_descriptor(b' ' * (MAX_DESCRIPTOR_BYTES + 1), '')
        self.assertEqual(c.exception.code, 'PACKAGE_SIZE')

    def test_strict_schema_missing_unknown_and_versions(self):
        for edit in [lambda v: v.pop('qualification'),
                     lambda v: v.update(command='shell command'),
                     lambda v: v.update(descriptor_schema='next'),
                     lambda v: v.update(package_version='9.0.0'),
                     lambda v: v['qualification'].update(status='QUALIFIED')]:
            value = copy.deepcopy(self.value); edit(value)
            self.rejected(value, 'PACKAGE_INVALID')

    def test_core_mismatch(self):
        self.value['core_versions'] = ['9.0.0']
        self.rejected(self.value, 'PACKAGE_CORE_VERSION')

    def test_unknown_adapter_revision_identity_and_policy(self):
        for field, value in [('adapter_ref', 'os:system'), ('source_revision', 'a' * 40)]:
            v = copy.deepcopy(self.value);v['models'][0][field] = value
            self.rejected(v, 'PACKAGE_BINDING')
        v = copy.deepcopy(self.value);v['package_id'] = 'hazardia.other'
        self.rejected(v, 'PACKAGE_BINDING')
        self.value['decision']['policy_refs'] = ['UNKNOWN']
        self.rejected(self.value, 'PACKAGE_POLICY')

    def test_contract_versions_and_validator_are_not_invented(self):
        for edit in [lambda v: v['contracts'][1].update(versions=['0.4.0']),
                     lambda v: v['contracts'][0].update(validator_ref='os:system'),
                     lambda v: v.update(contracts=v['contracts'][:1])]:
            v = copy.deepcopy(self.value);edit(v)
            self.rejected(v, 'PACKAGE_CONTRACT')

    def test_duplicate_ids_cause_whole_catalog_failure(self):
        p = self.parse(self.value)
        with self.assertRaises(HazardError) as c:
            DomainCatalog([p, p])
        self.assertEqual(c.exception.code, 'PACKAGE_COLLISION')
        with self.assertRaises(HazardError) as c:
            DomainCatalog([p] * 17)
        self.assertEqual(c.exception.code, 'PACKAGE_INVALID')

    def test_duplicate_json_fields_and_invalid_encoding(self):
        for raw in [b'{"x":1,"x":2}', b'\xff', b'{"x":NaN}', b'[' * 2000]:
            with self.assertRaises(HazardError) as c:
                parse_descriptor(raw, hashlib.sha256(raw).hexdigest())
            self.assertEqual(c.exception.code, 'PACKAGE_INVALID')

    def test_returned_views_do_not_change_registry(self):
        catalog = discover();view = catalog.describe()
        view['packages'][0]['models'][0]['engine_ref'] = 'BROKEN'
        self.assertNotEqual(catalog.describe()['packages'][0]['models'][0]['engine_ref'], 'BROKEN')
        with self.assertRaises(HazardError) as c:
            catalog.get('unregistered')
        self.assertEqual(c.exception.code, 'PACKAGE_NOT_FOUND')

    def test_discovery_no_write_network_subprocess_or_engine_imports(self):
        code = '''
import sys
from hazardia.package_catalog import discover
blocked={'numpy','rasterio','propagator','numba','scipy','geopandas','netCDF4','hazardia.jobs','hazardia.adapters.pipeline'}
before=set(sys.modules)
def audit(event,args):
 if event in {'socket.connect','socket.getaddrinfo','subprocess.Popen','os.system','os.mkdir','os.remove','os.rename'}:raise RuntimeError(event)
 if event=='open' and (isinstance(args[1],str) and any(v in args[1] for v in 'wax+') or isinstance(args[2],int) and args[2]&3):raise RuntimeError('write')
sys.addaudithook(audit)
a=discover().describe();b=discover().describe()
assert a==b and not any(m in blocked or any(m.startswith(x+'.') for x in blocked) for m in set(sys.modules)-before)
print('PASS no network, writes, subprocesses or scientific/runtime imports')
'''
        p = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_api_and_scientific_workers_do_not_import_discovery(self):
        # Catalog failures do not prevent API startup; pipeline failures are classified.
        files = ['jobs.py', 'web/server.py', 'firelab.py',
                 'adapters/workers/fire.py', 'adapters/workers/fire_studio.py', 'adapters/workers/flood.py']
        for name in files:
            self.assertNotIn('package_catalog', (ROOT / name).read_text())


if __name__ == '__main__':
    unittest.main()
