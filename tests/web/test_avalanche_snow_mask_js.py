import json,re,unittest
from pathlib import Path
import quickjs
BASE=Path(__file__).resolve().parents[2]/'src/hazardia/web/static'
class SnowMaskTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context()
  for name in ['avalanche-real-snow.js','avalanche-overview.js','avalanche-gran-sasso.js']:
   self.js.eval(re.sub(r'^import .*?$','',(BASE/name).read_text(),flags=re.M).replace('export ',''))
  self.js.eval('''var now=Date.parse('2026-11-04T12:00Z'),p={width:4,height:1,crs:'EPSG:3857',projected_bounds:[0,0,400,100],sources:[{observed_at:'2026-10-31T10:00Z'},{observed_at:'2026-11-04T10:00Z'},{observed_at:'2026-11-05T10:00Z'}],index_view:new DataView(new Uint8Array([9,2,4,2,11,2,11,3]).buffer),memory_views:[new DataView(new Uint8Array([11,1,4,2,11,2,0,0]).buffer),new DataView(new Uint8Array(8).buffer)],comparison_view:new DataView(new Uint8Array(4).buffer)},g={width:4,height:1,crs:'EPSG:3857',projected_bounds:[0,0,400,100],labels:{1:'A',2:'B',3:'C'}},view=new DataView(new Uint16Array([1,2,3,3]).buffer);''')
 def test_cloud_preserves_dated_snow_bare_removes_future_excluded(self):
  self.assertEqual(self.js.eval('JSON.stringify(Array.from(satelliteSnowMask(p,now)))'),'[2,0,1,0]')
 def test_observed_render_and_mask_are_identical(self):
  self.js.eval('var rgba=new Uint8Array(16);paintSatelliteSnow(p,0,1,rgba,now);')
  self.assertEqual(self.js.eval('JSON.stringify([0,1,2,3].map(i=>rgba[i*4+3]>0))'),'[true,false,true,false]')
 def test_snow_tint_keeps_terrain_visible_without_extending_mask(self):
  self.js.eval('var rgba=new Uint8Array(16);paintSatelliteSnow(p,0,1,rgba,now);')
  self.assertEqual(self.js.eval('JSON.stringify([0,1,2,3].map(i=>rgba[i*4+3]>0))'),'[true,false,true,false]')
  self.assertLessEqual(self.js.eval('Math.max(...rgba.filter((_,i)=>i%4===3))'),210)
  self.assertLess(self.js.eval('rgba[8]'),100)  # Cyan tint, not an opaque white replacement.
 def test_condition_surface_is_strict_subset(self):
  self.js.eval('var palette=new Uint8Array(65536*4);for(var i=1;i<=3;i++)palette.set(conditionColor("factors"),i*4);var out=new Uint8Array(16);paintConditionRows({width:4,height:1,view},palette,0,1,out,satelliteSnowMask(p,now));')
  self.assertEqual(self.js.eval('JSON.stringify([0,1,2,3].map(i=>out[i*4+3]>0))'),'[true,false,true,false]')
 def test_grid_mismatch_is_rejected(self):
  self.assertTrue(self.js.eval('intersectObservedTerrain(p,{...g,width:3},view,now)===null'))
  self.assertTrue(self.js.eval('intersectObservedTerrain(p,{...g,projected_bounds:[1,0,400,100]},view,now)===null'))
 def test_pins_are_inside_observed_pixels_not_profile_anchor(self):
  self.js.eval('var intersection=intersectObservedTerrain(p,g,view,now);var pins=observedPinLocations([{id:"A",lon:99,lat:99},{id:"B"},{id:"C"}],g,intersection);')
  self.assertEqual(self.js.eval('pins.length'),2)
  self.assertEqual(self.js.eval('JSON.stringify(pins.map(x=>realSnowCell(p,x.lon,x.lat,now).pixel))'),'[0,2]')
  self.assertEqual(self.js.eval('pins[0].snowEvidence'),'HISTORICAL')
 def test_highlight_stays_inside_satellite(self):
  self.js.eval('var out=new Uint8Array(16),selected=new Uint8Array(65536);selected.fill(1);var count=paintSelectedTerrain({width:4,height:1,view},selected,0,1,out,null,satelliteSnowMask(p,now));')
  self.assertEqual(self.js.eval('count'),2)
  self.assertEqual(self.js.eval('JSON.stringify([0,1,2,3].map(i=>out[i*4+3]>0))'),'[true,false,true,false]')
 def test_legacy_old_clear_snow_is_still_historical(self):
  self.js.eval('delete p.memory_views;p.index_view.setUint8(0,11);p.index_view.setUint8(1,1)')
  self.assertEqual(self.js.eval('satelliteSnowMask(p,now)[0]'),2)
