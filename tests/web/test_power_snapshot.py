import hashlib,json,tempfile,unittest,time
from pathlib import Path
from hazardia.web.power_snapshot import cached_power_snapshot
from hazardia.web.observed_layers import ObservedLayers
class CachedPowerTests(unittest.TestCase):
 def fixture(self,root):
  p=root/'runs/map-detail-20261015T204352Z/osm-map-final-raw.json';p.parent.mkdir(parents=True);raw=json.dumps({'osm3s':{'timestamp_osm_base':'2026-10-15T00:00:00Z'},'elements':[{'type':'way','id':1,'tags':{'power':'line','voltage':'132000'},'geometry':[{'lat':42.3,'lon':13.3},{'lat':42.4,'lon':13.4}]},{'type':'node','id':2,'lat':42.35,'lon':13.35,'tags':{'power':'tower'}},{'type':'node','id':3,'lat':42.35,'lon':13.35,'tags':{'shop':'yes'}}]}).encode();p.write_bytes(raw);meta=root/'web-assets/priority-areas.json';meta.parent.mkdir();meta.write_text(json.dumps(dict(source_sha256=hashlib.sha256(raw).hexdigest(),coverage_bbox_wgs84=[13.2,42.2,13.5,42.5],source_url='https://overpass.private.coffee/api/interpreter')));return p
 def test_tamper_and_missing_never_accepted(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.assertIsNone(cached_power_snapshot(root,[13,42,14,43]));p=self.fixture(root);p.write_bytes(p.read_bytes()+b' ');self.assertIsNone(cached_power_snapshot(root,[13,42,14,43]))
 def test_filter_coverage_and_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=self.fixture(root);before=p.read_bytes();v=cached_power_snapshot(root,[13,42,14,43]);self.assertEqual(v['bounds'],[13.2,42.2,13.5,42.5]);self.assertEqual(len(json.loads(v['raw'])['elements']),2);self.assertTrue(v['quality']['fallback']);self.assertFalse(v['quality']['complete']);self.assertEqual(p.read_bytes(),before);self.assertIsNone(cached_power_snapshot(root,[15,42,16,43]))
 def test_source_failure_preserves_aged_snapshot_identity(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root);(root/'web-state').mkdir()
   def fail(url):raise TimeoutError('upstream unavailable')
   service=ObservedLayers(root/'web-state','power',fetch=fail);r=service.prepare({'bounds':[13,42,14,43]})
   for _ in range(100):
    value=service.snapshot(r['request_id'])
    if value['status']!='LOADING':break
    time.sleep(.01)
   self.assertEqual(value['status'],'READY');self.assertEqual(value['bounds'],[13.2,42.2,13.5,42.5]);self.assertEqual(value['quality']['osm_base'],'2026-10-15T00:00:00Z');self.assertIn('upstream unavailable',value['quality']['upstream_error']);self.assertFalse(value['coupled_to_optimizer']);self.assertFalse(value['features'][0]['properties']['optimization_eligible'])

 def test_way_dependencies_are_preserved_without_invented_geometry(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=self.fixture(root);source=json.loads(p.read_text());source['elements'][0].pop('geometry');source['elements'][0]['nodes']=[10,11];source['elements'].extend([{'type':'node','id':10,'lat':42.3,'lon':13.3},{'type':'node','id':11,'lat':42.4,'lon':13.4}]);raw=json.dumps(source).encode();p.write_bytes(raw);m=root/'web-assets/priority-areas.json';meta=json.loads(m.read_text());meta['source_sha256']=hashlib.sha256(raw).hexdigest();m.write_text(json.dumps(meta))
   from hazardia.web.observed_layers import power_features
   value=cached_power_snapshot(root,[13,42,14,43]);features,quality=power_features(value['raw']);line=next(f for f in features if f['properties']['power_kind']=='line');self.assertEqual(line['geometry']['coordinates'],[[13.3,42.3],[13.4,42.4]]);self.assertEqual(len(features),2);self.assertEqual(quality['skipped_geometry'],0)
