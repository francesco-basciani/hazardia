"""Offline paired audit of saved results and edited resources; execute only in Linux VM.
No workspace writes, provider acquisition, operational forecast or scientific skill claim.
"""
import argparse,copy,json,os,shutil,sys,time
from pathlib import Path
os.environ.update(NUMBA_NUM_THREADS='1',OMP_NUM_THREADS='1')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',required=True);ap.add_argument('--workspace',required=True);ap.add_argument('--run-id',required=True);a=ap.parse_args()
 if sys.platform!='linux':raise RuntimeError('Run in Linux VM')
 import numpy as np
 from hazardia.adapters.workers.fire_studio import run_studio
 from hazardia.io import sha256
 from propagator.io.actions import build_mask
 from propagator.io.geo import GeographicInfo
 from shapely.geometry import LineString,Polygon
 from rasterio.transform import Affine,array_bounds
 from pyproj import CRS
 root=Path(a.runtime);ws=json.loads(Path(a.workspace).read_text());out=root/'runs'/a.run_id;out.mkdir();base=root/'jobs'/ws['scenarios'][0]['job_id'];req=json.loads((base/'request.json').read_text());original=json.loads((base/'fire-native-result.json').read_text());asset=lambda role:next(x for x in req['assets'] if x['role']==role);plan=json.loads((base/asset('fire_plan')['path']).read_text());arrays=np.load(base/asset('fire_arrays')['path'],allow_pickle=False);dem,veg=arrays['dem'],arrays['veg'];tr=Affine(*req['grid']['transform']);geo=GeographicInfo(crs=CRS.from_user_input(req['grid']['crs']),trans=tr,bounds=array_bounds(*dem.shape,tr),shape=dem.shape)
 cases=[('replay-baseline',[],[]),('user-scenario-1',ws['scenarios'][1]['input']['resources'],[]),('user-scenario-2',ws['scenarios'][2]['input']['resources'],[]),('wind-override',[],[dict(hour=h,speed_ms=max(3,plan['records'][h]['values']['wind_speed_10m']),direction_deg=(plan['records'][h]['values']['wind_direction_10m']+180)%360) for h in range(1,len(plan['records']))])]
 protocol=dict(run_id=a.run_id,parent_sha='96c9959924de024543a161aa60ec62402cb10f26',qualification='OFFLINE_UNQUALIFIED_RESEARCH',workspace_revision=ws['revision'],workspace_sha256=sha256(a.workspace),request_sha256=sha256(base/'request.json'),python=sys.version,seed=req['options']['seed'],duration_s=req['options']['duration_s'],hypotheses=['Exact baseline replay matches every probability array','Moved authored resources are consumed; area change is not assumed','Explicit hypothetical wind override after1h changes native output; speed floor3m/s and uniform override are declared'],cases=[dict(name=n,resources=r,wind_changes=c) for n,r,c in cases])
 (out/'protocol.json').write_text(json.dumps(protocol,indent=2));summary=dict(status='RUNNING',protocol_sha256=sha256(out/'protocol.json'),cases={})
 for name,resources,changes in cases:
  folder=out/name;folder.mkdir();request=copy.deepcopy(req);p=copy.deepcopy(plan);p.update(resources=resources,action_times=sorted({int(r['at_minutes']*60) for r in resources}),weather_changes=changes)
  for c in changes:p['records'][c['hour']]['values'].update(wind_speed_10m=c['speed_ms'],wind_direction_10m=c['direction_deg'])
  for asset_row in request['assets']:
   dest=folder/asset_row['path'];dest.parent.mkdir(exist_ok=True,parents=True)
   if asset_row['role']=='fire_plan':dest.write_text(json.dumps(p,indent=2))
   else:shutil.copyfile(base/asset_row['path'],dest)
   asset_row['sha256']=sha256(dest)
  (folder/'request.json').write_text(json.dumps(request,indent=2));began=time.monotonic();run_studio(folder,request,dem,veg,p);native=json.loads((folder/'fire-native-result.json').read_text());summary['cases'][name]=dict(seconds=time.monotonic()-began,final_ha=native['frames'][-1]['expected_area_ha'],frames=len(native['frames']),resource_count=len(resources),vegetation_changed_cells=sum(e['vegetation_changed_cells'] for e in native['consumed_events']),spatial_forcing_events=sum(e['spatial_forcing'] for e in native['consumed_events']),wind_events=native['consumed_events'][:3]);(out/'verification.json').write_text(json.dumps(summary,indent=2))
 baseline=np.load(out/'replay-baseline/fire-output.npz',allow_pickle=False)['probability'];summary['checks']={'baseline_all_288_probability_arrays_identical':all(np.array_equal(np.load(base/f['path'],allow_pickle=False)['probability'],np.load(out/'replay-baseline'/f['path'],allow_pickle=False)['probability']) for f in original['frames'])}
 for name,resources,_ in cases[1:]:
  values=np.load(out/name/'fire-output.npz',allow_pickle=False)['probability'];summary['cases'][name]['different_probability_cells']=int(np.count_nonzero(baseline!=values))
  intersections=[]
  for u in resources:
   pts=[(p[1],p[0]) for p in u.get('line',u.get('area'))];geom=LineString(pts) if 'line' in u else Polygon(pts);mask=build_mask([geom],geo,src_epsg=4326);intersections.append(dict(id=u['id'],cells=int(mask.sum()),baseline_reached_cells=int(np.count_nonzero(baseline[mask])),at_minutes=u['at_minutes']))
  summary['cases'][name]['resource_intersections']=intersections
  if resources:summary['checks'][name+'_consumed']=summary['cases'][name]['vegetation_changed_cells']>0
 summary['checks']['wind_changes_native_probability']=summary['cases']['wind-override']['different_probability_cells']>0
 summary['status']='PASS' if all(summary['checks'].values()) else 'FAIL';(out/'verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
 if summary['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
