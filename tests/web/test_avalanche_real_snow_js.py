import json,unittest
from pathlib import Path
import quickjs
class RealSnowTests(unittest.TestCase):
 def setUp(self):
  import re
  self.js=quickjs.Context();self.js.eval(re.sub(r'^import .*?$','',(Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-real-snow.js').read_text(),flags=re.M).replace('export ',''))
  self.js.eval('const now=Date.parse("2026-10-31T12:00:00Z");const p={width:2,height:1,projected_bounds:[0,0,200,100],sources:[{observed_at:"2026-10-31T11:00:00Z"}],index_view:new DataView(new Uint8Array([11,1,9,1]).buffer)};const lon=x=>x/6378137*180/Math.PI,lat=y=>(2*Math.atan(Math.exp(y/6378137))-Math.PI/2)*180/Math.PI;')
 def test_recent_snow_is_observed_but_cloud_is_unknown(self):
  self.assertTrue(self.js.eval('realSnowCell(p,lon(50),lat(50),now).snow'));self.assertTrue(self.js.eval('realSnowCell(p,lon(150),lat(50),now).snow===null'));self.assertEqual(self.js.eval('realSnowCell(p,lon(150),lat(50),now).status'),'UNCLASSIFIED')
 def test_old_snow_never_becomes_current_observation(self):
  self.assertTrue(self.js.eval('realSnowCell(p,lon(50),lat(50),now+25*3600000).snow===null'));self.assertEqual(self.js.eval('realSnowCell(p,lon(50),lat(50),now+25*3600000).status'),'STALE')
 def test_outside_has_no_invented_snow(self):self.assertEqual(self.js.eval('realSnowCell(p,lon(999),lat(50),now).status'),'OUTSIDE')
 def test_future_acquisition_cannot_be_current_snow(self):self.assertTrue(self.js.eval('realSnowCell(p,lon(50),lat(50),now-2*3600000).snow===null'))
 def test_shared_clock_selects_declared_native_window(self):
  for h,lead in [(0,0),(1,24),(24,24),(25,48),(48,48),(49,72),(72,72)]:self.assertEqual(self.js.eval('avalancheForecastFrame("2026-10-31T12:00Z",new Date(now+'+str(h)+'*3600000).toISOString()).lead'),lead)
 def test_no_forecast_extrapolation_outside72hours(self):
  self.assertTrue(self.js.eval('avalancheForecastFrame("2026-10-31T12:00Z",new Date(now+73*3600000).toISOString())===null'));self.assertTrue(self.js.eval('avalancheForecastFrame("bad","bad")===null'))

class SharedAvalancheClockTests(unittest.TestCase):
 def test_focus_uses_actual_avalanche_horizon_and_restores_other_sources(self):
  js=quickjs.Context();js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/monitor-timeline.js').read_text().replace('export ',''));js.eval('const t=new MonitorTimeline(()=>{},Date.parse("2026-10-31T12:00Z"));t.update("weather",[["2026-10-31T12:00Z","2026-11-05T12:00Z"]]);t.update("avalanche",[["2026-10-31T12:00Z","2026-11-03T12:00:00.001Z"]]);');self.assertEqual(js.eval('t.times().length'),120);js.eval('t.focus("avalanche")');self.assertEqual(js.eval('t.times().length'),73);self.assertEqual(js.eval('t.times()[t.times().length-1]'),'2026-11-03T12:00:00Z');self.assertTrue(js.eval('t.covered("weather","2026-11-04T12:00Z")'));js.eval('t.focus(null)');self.assertEqual(js.eval('t.times().length'),120);js.eval('t.focus("missing")');self.assertEqual(js.eval('t.times().length'),0)

 def test_latest_analysis_remains_accessible_when_reference_precedes_current_hour(self):
  js=quickjs.Context();js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/monitor-timeline.js').read_text().replace('export ',''));js.eval('const t=new MonitorTimeline(()=>{},Date.parse("2026-10-31T20:00Z"));t.update("avalanche",[["2026-10-31T19:00Z","2026-11-03T19:00:00.001Z"]]);t.focus("avalanche")')
  self.assertEqual(js.eval('t.times()[0]'),'2026-10-31T19:00:00Z');self.assertEqual(js.eval('t.times().length'),73)

class PixelMemoryTests(unittest.TestCase):
 setUp=RealSnowTests.setUp
 def test_cloud_keeps_two_dates_without_claiming_current_snow(self):
  self.js.eval('p.memory_views=[new DataView(new Uint8Array([11,1,11,1]).buffer),new DataView(new Uint8Array([4,1,4,1]).buffer)];p.comparison_view=new DataView(new Uint8Array([1,2]).buffer)')
  self.assertTrue(self.js.eval('realSnowCell(p,lon(150),lat(50),now).snow===null'))
  self.assertEqual(self.js.eval('realSnowCell(p,lon(150),lat(50),now).remembered.scl'),11)
  self.assertEqual(self.js.eval('realSnowCell(p,lon(150),lat(50),now).remembered.comparison'),2)

class SatelliteSurfaceTests(unittest.TestCase):
 def setUp(self):
  import re
  self.js=quickjs.Context();self.js.eval(re.sub(r'^import .*?$','',(Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-real-snow.js').read_text(),flags=re.M).replace('export ',''))
  self.js.eval('var now=Date.parse("2026-11-04T12:00Z"),p={width:3,height:1,sources:[{observed_at:"2026-10-31T10:00Z"},{observed_at:"2026-11-04T10:00Z"}],index_view:new DataView(new Uint8Array([9,2,4,2,11,2]).buffer),memory_views:[new DataView(new Uint8Array([11,1,4,2,11,2]).buffer)]};')
 def test_cloud_keeps_old_snow_and_clear_bare_removes_it(self):
  self.assertEqual(self.js.eval('satelliteSnowPixel(p,0,now).kind'),'HISTORICAL_SNOW');self.assertEqual(self.js.eval('satelliteSnowPixel(p,1,now).kind'),'NO_SNOW_OBSERVED');self.assertEqual(self.js.eval('satelliteSnowPixel(p,2,now).kind'),'RECENT_SNOW')
 def test_surface_contains_snow_pixels_only_no_station_or_terrain_fill(self):
  self.js.eval('var rgba=new Uint8Array(12);paintSatelliteSnow(p,0,1,rgba,now)');self.assertGreater(self.js.eval('rgba[3]'),0);self.assertEqual(self.js.eval('rgba[7]'),0);self.assertGreater(self.js.eval('rgba[11]'),0)
 def test_unknown_without_old_evidence_stays_transparent(self):
  self.js.eval('p.memory_views[0]=new DataView(new Uint8Array(6).buffer);var rgba=new Uint8Array(12);paintSatelliteSnow(p,0,1,rgba,now)');self.assertEqual(self.js.eval('rgba[3]'),0)
 def test_future_scene_never_becomes_recent_snow(self):
  self.assertNotEqual(self.js.eval('satelliteSnowPixel(p,2,now-2*86400000).kind'),'RECENT_SNOW')
