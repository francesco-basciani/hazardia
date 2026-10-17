import copy,json,tempfile,unittest,hashlib
from pathlib import Path
from unittest.mock import patch
from hazardia.ingest.attention_worker import classify,FWI,DC,level,topology
from hazardia.ingest.attention import AttentionStore
from hazardia.io import HazardError

class AttentionTests(unittest.TestCase):
    def test_source_classes_and_unknown(self):
        self.assertEqual([classify(v,FWI) for v in [0,1,11.2,21.3,38,50,70,float('nan'),-1]],[None,0,1,2,3,4,4,None,None])
        self.assertEqual(classify(600,DC),4)
        self.assertEqual(level('Ordinaria per rischio temporali / ALLERTA GIALLA'),1)
        self.assertEqual(level('Assenza / NESSUNA ALLERTA'),0)
        self.assertIsNone(level('campo nuovo non noto'))
    def test_topology_shared_reverse_arcs_and_unknown_warning(self):
        reasons={'Per rischio idraulico':'NESSUNA ALLERTA','Per rischio temporali':'ALLERTA GIALLA','Per rischio idrogeologico':'NESSUNA ALLERTA','Nome zona':'Zona test','Comuni':['Uno']}
        g=dict(type='Polygon',arcs=[[0,-2]],properties=reasons)
        t=dict(type='Topology',transform=dict(scale=[.01,.01],translate=[10,40]),arcs=[[[0,0],[100,0],[0,100]],[[0,0],[0,100],[100,0]]],objects={'zones':dict(type='GeometryCollection',geometries=[g]*50)})
        geo=topology(t);self.assertEqual(len(geo['features']),50);self.assertEqual(geo['features'][0]['properties']['level'],1)
        reasons['Per rischio temporali']='UNKNOWN';self.assertIsNone(topology(t)['features'][0]['properties']['level'])
        t['arcs'][1][0]=[40,40]
        with self.assertRaises(ValueError):topology(t)
    def fixture(self,root):
        store=AttentionStore(root,root,clock=lambda:100000.);ident='snapshot-'+'a'*32;folder=Path(root)/ident;folder.mkdir()
        name='effis-1970-01-02.geojson';raw=json.dumps(dict(type='FeatureCollection',features=[])).encode();(folder/name).write_bytes(raw)
        x=dict(local_epoch=99900,reference_epoch=100000,clock_offset_s=100,acquired_at='1970-01-02T03:46:40Z',sources={'effis':dict(status='AVAILABLE',products=[dict(day='1970-01-02',file=name,valid_until='1970-01-03T00:00:00Z')])},files={name:hashlib.sha256(raw).hexdigest()})
        data=json.dumps(x).encode();(folder/'result.json').write_bytes(data);store.write_state(dict(snapshot=ident,sha256=hashlib.sha256(data).hexdigest()))
        return store,ident,name
    def test_stale_future_and_clock_skew(self):
        with tempfile.TemporaryDirectory() as root:
            store,ident,name=self.fixture(root);self.assertEqual(store.snapshot()['sources']['effis']['products'][0]['freshness'],'FRESH')
            store.clock=lambda:120000.;self.assertEqual(store.snapshot()['status'],'STALE')
            store.clock=lambda:90000.;self.assertEqual(store.snapshot()['status'],'STALE');self.assertEqual(store.snapshot()['clock_status'],'CLOCK_DISCONTINUITY')
    def test_cache_integrity_and_path_guard(self):
        with tempfile.TemporaryDirectory() as root:
            store,ident,name=self.fixture(root);self.assertEqual(store.layer(ident,name)['features'],[])
            for i,n in [('../','../a'),(ident,'dpc-bad.geojson')]:
                with self.assertRaises(HazardError):store.layer(i,n)
            (Path(root)/ident/name).write_text('{}')
            with self.assertRaises(HazardError):store.layer(ident,name)
    def test_missing_source_does_not_become_low(self):
        with tempfile.TemporaryDirectory() as root:
            store=AttentionStore(root,root);self.assertEqual(store.snapshot()['status'],'UNAVAILABLE');self.assertEqual(store.snapshot()['sources'],{})
    def test_worker_keeps_fire_when_dpc_fails(self):
        import hazardia.ingest.attention_worker as worker
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/'snapshot';folder.mkdir();profile=Path(root)/'profile.json';profile.write_text(json.dumps(dict(id='test',days=2,native_resolution_km=10,bounds=[6,35,19,48])))
            def fire(acq,profile,day):return dict(day=day,file='test.geojson')
            with patch.object(worker,'dpc',side_effect=ValueError('Source unavailable')),patch.object(worker,'effis',side_effect=fire):worker.run(folder,profile)
            result=json.loads((folder/'result.json').read_text());self.assertEqual(result['sources']['dpc']['status'],'UNAVAILABLE');self.assertEqual(len(result['sources']['effis']['products']),2)
            self.assertIsNone(result['reference_epoch'])
    def test_refresh_throttles_before_network(self):
        with tempfile.TemporaryDirectory() as root:
            store=AttentionStore(root,root,clock=lambda:1000);store.write_state(dict(attempt_at=999))
            with patch('hazardia.ingest.attention.subprocess.run') as run:
                store.refresh();store.busy.acquire();store.busy.release();run.assert_not_called()
if __name__=='__main__':unittest.main()
