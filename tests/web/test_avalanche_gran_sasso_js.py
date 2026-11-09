import copy,json,unittest
from pathlib import Path
try:import quickjs
except ImportError:quickjs=None
@unittest.skipUnless(quickjs,'QuickJS required')
class LocalTerrainTests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-gran-sasso.js').read_text().replace('export ',''))
  self.now=1793437200000 # 2026-10-31 09:00 UTC
  w={str(i):dict(forecast_hs_max_cm=10,max_net_swe_increase_kg_m2=2,liquid_water_max_kg_m2=0) for i in [0,24,48,72]}
  e=dict(result=dict(forecast_windows=w),hourly=dict(quantities=dict(hs=[10]*73)),recent24=dict(net_swe_increase_kg_m2=1,water_max_kg_m2=0),history_initial_hs_m=0)
  self.p=dict(metadata=dict(reference_utc='2026-10-31T09:00:00Z',weather_run_utc='2026-10-31T00:00:00Z'),models=dict(A=dict(NWP_INITIAL=e,ZERO_INITIAL=copy.deepcopy(e))))
  self.f=dict(properties=dict(profile_id='A',terrain_steep=True))
 def assess(self,lead=0):return json.loads(self.js.eval('JSON.stringify(localAssessment('+json.dumps(self.p)+','+json.dumps(self.f)+','+str(lead)+','+str(self.now)+'))'))
 def test_history_signal_on_snow_steep_terrain(self):self.assertEqual(self.assess()['kind'],'factors')
 def test_flat_snow_remains_visible_without_calling_it_release_area(self):self.f['properties']['terrain_steep']=False;self.assertEqual(self.assess()['kind'],'snow')
 def test_missing_member_not_replaced_by_reset_baseline(self):
  del self.p['models']['A']['ZERO_INITIAL'];self.assertEqual(self.assess()['kind'],'missing')
 def test_unmatched_terrain_not_interpolated(self):self.f['properties']['profile_id']='B';self.assertEqual(self.assess()['kind'],'missing')
 def test_stale_not_low_danger(self):self.now+=13*3600000;self.assertEqual(self.assess()['kind'],'missing')
 def test_retrospective_reconstruction_never_becomes_current_hazard(self):
  self.p['metadata']['temporal_mode']='RETROSPECTIVE_CACHED_FORCING'
  self.assertEqual(self.assess()['kind'],'missing')
  self.assertIn('storica',self.assess()['reason'])
  self.p['features']=[self.f]
  self.assertEqual(self.js.eval('localAvalanchePins('+json.dumps(self.p)+',0,'+str(self.now)+').length'),0)
 def test_noaa_history_gap_is_not_reported_as_other_provider_quota(self):
  self.p['metadata']['weather_provider']='noaa_gfs';self.p['metadata']['failures']={'A':'WEATHER_SUPPORT_UNAVAILABLE_PUBLIC_QUOTA_OR_SOURCE'};self.p['models']={}
  self.assertNotIn('quota',self.assess()['reason']);self.assertIn('storico',self.assess()['reason'])
 def test_fine_weather_keeps_coarse_components_and_horizon_explicit(self):
  text=self.js.eval('localForcingDescription('+json.dumps(dict(weather_provider='icon2i_hybrid',high_resolution_end_utc='2026-11-03T12:00:00Z'))+')')
  for term in ['2,2km','25km','2026-11-03T12:00:00Z','5km']:self.assertIn(term,text)
 def test_temporary_gfs_fallback_does_not_claim_fine_weather(self):
  text=self.js.eval('localForcingDescription('+json.dumps(dict(weather_provider='noaa_gfs',weather_fallback_reason='ICON2I_CYCLE_STALE'))+')')
  for term in ['DEGRADATO','25km','mancante','automatico']:self.assertIn(term,text)
  self.assertNotIn('modello2,2km',text)
 def test_unknown_eo_never_means_no_snow(self):
  result=json.loads(self.js.eval('JSON.stringify(localSnowEvidenceText({properties:{}}))'));self.assertIn('non significano assenza',result[0])
 def test_eo_model_comparison_is_not_claimed_assimilated(self):
  f=dict(properties=dict(snow_observations=[dict(observed_at='2026-10-31T10:08:46Z',snow_pixels=2,clear_land_pixels=0,model_comparison=dict(hs_cm=0,at_utc='2026-10-31T10:00:00Z',offset_seconds=-526,status='MIXED_OR_DISAGREES_REQUIRES_REVIEW'))]))
  text=self.js.eval('localSnowEvidenceText('+json.dumps(f)+')[0]');self.assertIn('discordante',text);self.assertIn('non è stata assimilata',text)
 def test_future_time_rejected(self):self.now-=1;self.assertEqual(self.assess()['kind'],'missing')
 def test_zero_not_candidate_even_when_water_or_load_in_window(self):
  for e in self.p['models']['A'].values():e['hourly']['quantities']['hs'][0]=0
  self.assertEqual(self.assess()['kind'],'zero')
 def test_correct_time_and_hypotheses_not_independent_votes(self):
  for e in self.p['models']['A'].values():e['hourly']['quantities']['hs'][24]=0;e['result']['forecast_windows']['24']['forecast_hs_max_cm']=0
  self.assertEqual(self.assess(24)['kind'],'zero');self.assertEqual(self.assess(72)['kind'],'factors');self.assertTrue(self.assess()['identicalInitial'])
 def test_current_history_gap_never_safe(self):
  self.p['models']['A']['NWP_INITIAL']['recent24']={};self.assertEqual(self.assess()['kind'],'missing')
 def test_no_mutation(self):
  self.js.eval('const p='+json.dumps(self.p)+';const f='+json.dumps(self.f)+';const before=JSON.stringify(p);localAssessment(p,f,24,'+str(self.now)+')');self.assertTrue(self.js.eval('before===JSON.stringify(p)'))

 def test_transient_snow_in_window_still_supports_candidate(self):
  for e in self.p['models']['A'].values():e['hourly']['quantities']['hs'][24]=0
  self.assertEqual(self.assess(24)['kind'],'factors');self.assertEqual(self.assess(24)['hs'],[0,0])

 def test_explicit_zero_alias_has_same_factors_not_extra_confidence(self):
  self.p['models']['A']['ZERO_INITIAL']={'alias':'NWP_INITIAL'};self.assertEqual(self.assess()['kind'],'factors');self.assertTrue(self.assess()['identicalInitial'])
 def test_geographic_query_index_outside_and_forest_are_not_safe(self):
  self.js.eval('const p={raster_index:{width:2,height:2,bounds:[13,42,13.02,42.02],labels:{"1":"A","2":"B"}},index_view:new DataView(new Uint8Array([1,0,255,255,0,0,2,0]).buffer),features_by_id:new Map([["A",{properties:{profile_id:"A"}}],["B",{properties:{profile_id:"B"}}]])}')
  self.assertEqual(self.js.eval('localFeatureAt(p,13.005,42.015).properties.profile_id'),'A');self.assertEqual(self.js.eval('localFeatureAt(p,13.015,42.015).properties.quality_code'),'FOREST_CANOPY_NOT_MODELED');self.assertTrue(self.js.eval('localFeatureAt(p,14,42)===null'))
 def test_mercator_index_matches_projected_cell(self):
  self.js.eval('const p={raster_index:{width:2,height:2,bounds:[13,42,13.02,42.02],crs:"EPSG:3857",projected_bounds:[6378137*13*Math.PI/180,6378137*Math.log(Math.tan(Math.PI/4+42*Math.PI/360)),6378137*13.02*Math.PI/180,6378137*Math.log(Math.tan(Math.PI/4+42.02*Math.PI/360))],labels:{"1":"A","2":"B"}},index_view:new DataView(new Uint8Array([1,0,255,255,0,0,2,0]).buffer),features_by_id:new Map([["A",{properties:{profile_id:"A"}}],["B",{properties:{profile_id:"B"}}]])}')
  self.assertEqual(self.js.eval('localFeatureAt(p,13.005,42.015).properties.profile_id'),'A');self.assertEqual(self.js.eval('localFeatureAt(p,13.015,42.005).properties.profile_id'),'B')

 def test_pins_preserve_every_candidate_at_all_supported_zooms(self):
  self.js.eval('var pins=[{id:"a",lat:42.45,lon:13.55,kind:"candidate"},{id:"b",lat:42.451,lon:13.551,kind:"factors"},{id:"c",lat:46,lon:11,kind:"candidate"}]')
  for z in range(2,21):
   groups=json.loads(self.js.eval('JSON.stringify(groupAvalanchePins(pins,'+str(z)+'))'));self.assertEqual(sum(g['count'] for g in groups),3);self.assertEqual(sorted(m['id'] for g in groups for m in g['members']),['a','b','c'])
  self.assertLess(len(json.loads(self.js.eval('JSON.stringify(groupAvalanchePins(pins,2))'))),len(json.loads(self.js.eval('JSON.stringify(groupAvalanchePins(pins,20))'))))
 def test_cluster_retains_stronger_descriptive_kind_without_inventing_severity(self):
  groups=json.loads(self.js.eval('JSON.stringify(groupAvalanchePins([{lat:42,lon:13,kind:"candidate"},{lat:42,lon:13,kind:"factors"}],2))'));self.assertEqual(groups[0]['kind'],'factors');self.assertEqual(groups[0]['count'],2)
 def test_pins_do_not_promote_missing_stale_or_flat_snow(self):
  self.p['features']=[self.f];self.p['models']['A']['NWP_INITIAL']['terrain_point']=dict(lat=42.45,lon=13.55)
  def pins():return json.loads(self.js.eval('JSON.stringify(localAvalanchePins('+json.dumps(self.p)+',0,'+str(self.now)+'))'))
  self.assertEqual(len(pins()),1);self.f['properties']['terrain_steep']=False;self.assertEqual(pins(),[]);self.f['properties']['terrain_steep']=True;self.now+=13*3600000;self.assertEqual(pins(),[]);self.now-=13*3600000;del self.p['models']['A'];self.assertEqual(pins(),[])
 def test_pin_candidates_follow_selected_forecast_not_whole_period(self):
  self.p['features']=[self.f];self.p['models']['A']['NWP_INITIAL']['terrain_point']=dict(lat=42.45,lon=13.55)
  for e in self.p['models']['A'].values():e['hourly']['quantities']['hs'][0]=0
  def pins(lead):return json.loads(self.js.eval('JSON.stringify(localAvalanchePins('+json.dumps(self.p)+','+str(lead)+','+str(self.now)+'))'))
  self.assertEqual(pins(0),[]);self.assertEqual(len(pins(72)),1)
 def test_bad_pin_coordinates_are_not_drawn(self):
  self.assertEqual(self.js.eval('groupAvalanchePins([{lat:91,lon:13},{lat:null,lon:13},{lat:42,lon:999}],2).length'),0)

 def test_selection_mask_follows_labels_not_rectangular_envelope(self):
  result=json.loads(self.js.eval('JSON.stringify((()=>{const v=new DataView(new Uint8Array([1,0,0,0,2,0,255,255,1,0,2,0]).buffer),selected=selectedTerrainLabels({raster_index:{labels:{"1":"A","2":"B","65535":"A"}}},["A"]),rgba=new Uint8ClampedArray(24),extent=[3,2,0,0],n=paintSelectedTerrain({width:3,height:2,view:v},selected,0,2,rgba,extent);return {n,alpha:[rgba[3],rgba[7],rgba[11],rgba[15],rgba[19],rgba[23]],extent};})())'))
  self.assertEqual(result['n'],2);self.assertEqual(result['alpha'],[255,0,0,0,255,0]);self.assertEqual(result['extent'],[0,0,2,2])
 def test_selection_chunks_equal_whole_raster_and_no_neighbour_bleed(self):
  self.assertTrue(self.js.eval('(()=>{const index={width:3,height:3,view:new DataView(new Uint16Array([1,1,1,1,1,1,1,1,1]).buffer)},selected=new Uint8Array(65536);selected[1]=1;const a=new Uint8ClampedArray(36),b=new Uint8ClampedArray(36);paintSelectedTerrain(index,selected,0,3,a);for(let row=0;row<3;row++)paintSelectedTerrain(index,selected,row,row+1,b);return JSON.stringify([...a])===JSON.stringify([...b])&&a[19]===95;})()'))
 def test_forecast_summary_keeps_fixed_selected_cohort_and_missing(self):
  self.p['features']=[self.f];missing=dict(properties=dict(profile_id='B',terrain_steep=True));self.f['properties']['terrain_steep']=True
  for e in self.p['models']['A'].values():e['hourly']['quantities']['hs'][0]=0
  rows=json.loads(self.js.eval('JSON.stringify(pinForecastRows('+json.dumps(self.p)+','+json.dumps([self.f,missing])+','+str(self.now)+'))'))
  self.assertEqual([r['total'] for r in rows],[2]*4);self.assertEqual([r['missing'] for r in rows],[1]*4);self.assertEqual([r['candidates'] for r in rows],[0,1,1,1]);self.assertEqual(rows[0]['hsMax'],0)
 def test_forecast_summary_stale_does_not_invent_numeric_values(self):
  rows=json.loads(self.js.eval('JSON.stringify(pinForecastRows('+json.dumps(self.p)+','+json.dumps([self.f])+','+str(self.now+13*3600000)+'))'))
  self.assertTrue(all(r['missing']==1 and r['hsMin'] is None and r['loadMax'] is None for r in rows))
 def test_surface_mixed_and_zero_disagreement_are_explained_differently(self):
  f=dict(properties=dict(snow_observations=[dict(observed_at='2026-10-31T10:08:46Z',snow_pixels=2,clear_land_pixels=0,evidence_status='OBSERVED_SNOW_MODEL_ZERO',model_comparison=dict(hs_cm=0,at_utc='2026-10-31T10:00:00Z',offset_seconds=-526,status='MIXED_OR_DISAGREES_REQUIRES_REVIEW'))]))
  text=self.js.eval('localSnowEvidenceText('+json.dumps(f)+')[0]');self.assertIn('possibile sottostima',text)
  f['properties']['snow_observations'][0]['evidence_status']='MIXED_SURFACE'
  text=self.js.eval('localSnowEvidenceText('+json.dumps(f)+')[0]');self.assertIn('non dimostra',text);self.assertNotIn('possibile sottostima',text)
