import copy,json,re,unittest
from pathlib import Path
import quickjs

class SnowDepthTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();root=Path(__file__).resolve().parents[2]/'src/hazardia/web/static'
  for name in ['avalanche-gran-sasso.js','avalanche-snow-depth.js']:
   self.js.eval(re.sub(r'^import .*?$','',(root/name).read_text(),flags=re.M).replace('export ',''))
  self.now=1793437200000
  e=dict(hourly=dict(quantities=dict(hs={'0':3,'24':8,'48':15,'72':22})))
  self.p=dict(metadata=dict(reference_utc='2026-10-31T09:00:00Z',weather_run_utc='2026-10-31T00:00:00Z'),models=dict(A=dict(NWP_INITIAL=e,ZERO_INITIAL=copy.deepcopy(e))),features=[dict(properties=dict(profile_id='A'))],raster_index=dict(labels={'1':'A','2':'B'}))
 def value(self,lead=0,now=None,dated=False):
  return json.loads(self.js.eval('JSON.stringify(snowDepthValue('+json.dumps(self.p)+','+json.dumps(self.p['features'][0])+','+str(lead)+','+str(self.now if now is None else now)+','+str(dated).lower()+'))'))
 def test_existing_hs_not_depth_change_or_snowfall(self):self.assertEqual(self.value(24)['max'],8)
 def test_initialization_range_uses_two_states_not_mean_or_probability(self):
  self.p['models']['A']['ZERO_INITIAL']['hourly']['quantities']['hs']['0']=1
  self.assertEqual([self.value()['min'],self.value()['max']],[1,3])
 def test_missing_member_is_not_zero_or_interpolated(self):
  del self.p['models']['A']['ZERO_INITIAL'];self.assertTrue(self.value()['missing'])
 def test_negative_nonnumeric_or_missing_rejected(self):
  for value in [-1,'10',None]:
   self.p['models']['A']['ZERO_INITIAL']['hourly']['quantities']['hs']['0']=value;self.assertTrue(self.value()['missing'])
 def test_stale_hidden_until_explicit_historical_consultation(self):
  self.assertTrue(self.value(now=self.now+13*3600000)['missing']);v=self.value(now=self.now+13*3600000,dated=True);self.assertTrue(v['dated']);self.assertEqual(v['max'],3)
 def test_colors_encode_depth_and_keep_missing_distinct_from_zero(self):
  self.assertEqual(json.loads(self.js.eval('JSON.stringify(snowDepthRGBA({max:0}))')),[0,0,0,0]);self.assertNotEqual(self.js.eval('JSON.stringify(snowDepthRGBA({missing:true}))'),self.js.eval('JSON.stringify(snowDepthRGBA({max:0}))'))
  self.assertNotEqual(self.js.eval('JSON.stringify(snowDepthRGBA({max:4}))'),self.js.eval('JSON.stringify(snowDepthRGBA({max:40}))'))
 def test_raster_preserves_terrain_labels_forest_gaps_and_outside(self):
  self.js.eval('const p='+json.dumps(self.p)+';const pal=snowDepthPalette(p,0,'+str(self.now)+');const out=new Uint8ClampedArray(16);const view=new DataView(new Uint8Array([1,0,2,0,255,255,0,0]).buffer);const counts=paintSnowDepth({width:4,height:1,view},pal,0,1,out);')
  self.assertEqual(json.loads(self.js.eval('JSON.stringify(counts)')),dict(snowPixels=1,missingPixels=2));self.assertEqual(self.js.eval('out[15]'),0)
 def test_chunked_render_matches_whole_and_does_not_mutate_model(self):
  self.js.eval('const p='+json.dumps(self.p)+';const before=JSON.stringify(p);const pal=snowDepthPalette(p,0,'+str(self.now)+');const g={width:1,height:2,view:new DataView(new Uint8Array([1,0,2,0]).buffer)},a=new Uint8ClampedArray(8),b=new Uint8ClampedArray(8);paintSnowDepth(g,pal,0,2,a);paintSnowDepth(g,pal,0,1,b);paintSnowDepth(g,pal,1,2,b);')
  self.assertTrue(self.js.eval('JSON.stringify(a)===JSON.stringify(b)&&before===JSON.stringify(p)'))
 def test_layer_module_parses(self):
  path=Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-layer.js';self.js.eval(re.sub(r'^import .*?$','',path.read_text(),flags=re.M).replace('export ',''))
