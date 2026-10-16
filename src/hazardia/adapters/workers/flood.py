"""Real HMC -> REFlEx on the staged grid; physics parameters remain research-only."""
import datetime as dt
import gzip
import math
import os
import re
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from netCDF4 import Dataset
from hazardia.io import load,write_new,verify_asset,HazardError,sha256

def execute(command,log):
    with Path(log).open('xb') as stream:
        p=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=False)
    if p.returncode:
        raise HazardError('MODEL_EXIT',str(command[0])+' exit '+str(p.returncode)+'; see '+str(log))

def run(root):
    req=load(root/'request.json');cfg=load(root/'runtime.json');options=req['options'];demfile=verify_asset(root,next(v for v in req['assets'] if v['role']=='dem'))
    weather=load(verify_asset(root,next(v for v in req['assets'] if v['role']=='weather')))
    work=root/'flood-work';work.mkdir();(work/'logs').mkdir()
    with rasterio.open(demfile) as src:
        if src.crs.to_epsg()!=4326 or list(src.shape)!=req['grid']['shape'] or list(src.transform)[:6]!=req['grid']['transform']:
            raise HazardError('GRID_MISMATCH','Flood native grid mismatch')
        if src.read(1,masked=True).count()!=src.height*src.width:raise HazardError('SOURCE_MISSING','Incomplete DEM')
        transform=src.transform;height,width=src.shape;resolution=transform.a
    if abs(resolution+transform.e)>1e-12:raise HazardError('GRID_MISMATCH','HMC ASCII requires angular square pixels')
    # Exact WGS84 ellipsoid areas bounded by parallels and meridians, per row.
    a=6378137.;e2=6.6943799901413165e-3;e=math.sqrt(e2)
    def primitive(phi):
        u=np.sin(phi);return .5*a*a*(1-e2)*(u/(1-e2*u*u)+np.arctanh(e*u)/e)
    lat_edges=transform.f+np.arange(height+1)*transform.e
    row_area=np.abs(np.diff(primitive(np.radians(lat_edges))))*math.radians(resolution)
    mean_area=float(row_area.mean())
    settings=load(cfg['reflex_template']);settings['algorithm'].update(grass_bin='grass',proj_lib='/usr/share/proj',proj_db='/usr/share/proj')
    settings['domain'].update(name='abruzzo',res_deg=resolution,res_km=math.sqrt(mean_area)/1000,res_str='1arcsec',source_epsg=4326,target_epsg=4326,min_nonnull_value=-9999)
    settings['step_0']['preprocessing'].update(hydrodem_remove_sink=False,richdem_eps_filling=True,pysheds_pit_remove_and_solve_flats=True)
    settings['step_0']['stream_burning']['burning_method']=None
    settings['step_1'].update(stream_definition_method='d8',hand_definition_method='d8',flow_accumulation_threshold_cells=options['flow_threshold_cells'])
    for k in [2,3,4]:settings['step_'+str(k)]['multiprocessing'].update(enable=True,max_cores=2)
    settings['step_2']['buffer_for_coastal_expansion_cells']=3
    settings['step_3']['coastal_expansion'].update(enable=False,manual_activation=False)
    settings['step_4'].update(volume_file_path=str(work/'discharge.csv'),minimum_volume_included=1,return_period=100)
    # The upstream example's 0.1m lower bound forces a volume larger than
    # small research hydrographs. Keep the fit diagnostic, permit shallow water.
    settings['step_4']['optimization']['min_water_depth']=0.000001
    settings['step_4']['merging_maps'].update(multiprocessing_enabled=False,max_cores=1,max_maps_opened_together=10)
    config=work/'settings.json';write_new(config,settings)
    scripts=['reflex_step0_dem_conditioning.py','reflex_step1_hydro_derivatives.py','reflex_step2_static_preprocessing.py','reflex_step3_hand.py','reflex_step4_flood_mapping.py']
    def step(n):
        command=[cfg['geo_python'],str(Path(cfg['reflex_source'])/scripts[n]),'-settings_file',str(config),'-base_path',str(work),'-log_file',str(work/'logs'/('step'+str(n)+'.model.log'))]
        if n==0:command+=['-dem',str(demfile)]
        execute(command,work/'logs'/('step'+str(n)+'.log'))
    for n in range(4):step(n)
    prefix='r_abruzzo_1arcsec_'
    paths=dict(dem=work/'dem_conditioning'/ (prefix+'conddem.tif'),direction=work/'hydro_derivatives/rst'/(prefix+'d8_flow_dir.tif'),streams=work/'hydro_derivatives/rst'/(prefix+'d8_streams.tif'),area=work/'hydro_derivatives/rst'/(prefix+'d8_flowacc.tif'))
    arrays={}
    for key,path in paths.items():
        with rasterio.open(path) as src:
            if src.shape!=(height,width) or not np.allclose(list(src.transform)[:6],list(transform)[:6],rtol=0,atol=1e-12):raise HazardError('GRID_MISMATCH','Derived '+key+' changed authoritative grid')
            arrays[key]=src.read(1)
    features=gpd.read_file(work/'data_static/vct/v_abruzzo_1arcsec_streams_features.shp')
    if len(features)==0:raise HazardError('EMPTY_NETWORK','No usable reaches')
    hand_records=[]
    for sid in features.stream.astype(int):
        path=work/'hand/rst/ext_no_ce'/f'hand_d8_ext_no_ce_{sid}.tif'
        with rasterio.open(path) as src:
            data=src.read(1,masked=True).compressed()
            if not data.size or not np.isfinite(data).all() or (data<0).any():raise HazardError('EMPTY_HAND','Invalid or empty HAND for '+str(sid))
            hand_records.append(dict(stream=int(sid),valid_cells=int(data.size),sha256=sha256(path)))
    write_new(root/'hand-validation.json',dict(reaches=len(features),hands=hand_records))
    hmc=work/'hmc';hmc.mkdir()
    for name in ['static','forcing','output','state','restart']:(hmc/name).mkdir()
    row,col=np.indices((height,width));mask=np.zeros((height,width),int);mask[1:-1,1:-1]=1
    pnt=np.zeros((height,width),int)
    for source,target in {1:9,2:8,3:7,4:4,5:1,6:2,7:3,8:6}.items():pnt[np.abs(arrays['direction'])==source]=target
    if (pnt[mask>0]==0).any():raise HazardError('UNSUPPORTED_GRID','Unresolved flow directions in active cells')
    lon=transform.c+(col+.5)*resolution;lat=transform.f+(row+.5)*transform.e
    streams=arrays['streams'];sections=[]
    for sid in sorted(features.stream.astype(int)):
        score=np.where((streams==sid)&(mask>0),arrays['area'],-1)
        rr,cc=np.unravel_index(np.argmax(score),score.shape)
        if score[rr,cc]<=0:raise HazardError('REACH_MAPPING','No active HMC section for reach '+str(sid))
        sections.append(dict(stream=int(sid),row=int(rr),col=int(cc),longitude=float(lon[rr,cc]),latitude=float(lat[rr,cc])))
    fields=dict(dem=np.where(mask,arrays['dem'],-9999),lon=lon,lat=lat,mask=mask,pnt=np.where(mask,pnt,-9999),choice=np.where(mask,np.where((streams>0)&(streams<100000),1,0),-9999),area=arrays['area'],areacell=np.broadcast_to(row_area[:,None],(height,width)),alpha=np.full((height,width),.1),beta=np.full((height,width),.1),cn=np.full((height,width),75),ct=np.full((height,width),.4),cf=np.full((height,width),.1),uc=np.full((height,width),30),uh=np.full((height,width),1.7))
    xmin=transform.c;ymin=transform.f-height*resolution
    for name,values in fields.items():
        path=hmc/'static'/('abruzzo.'+name+'.txt')
        with path.open('x') as f:
            f.write(f'ncols {width}\nnrows {height}\nxllcorner {xmin:.10f}\nyllcorner {ymin:.10f}\ncellsize {resolution:.12f}\nNODATA_value -9999\n');np.savetxt(f,values,fmt='%.9f')
    (hmc/'static/abruzzo.info_section.txt').write_text(''.join(f"{s['row']+1} {s['col']+1} s{s['stream']}\n" for s in sections))
    start=dt.datetime.fromisoformat(req['valid_from'].replace('Z','+00:00'));hours=options['hours']
    if len(options['rain_mm'])!=hours+1:raise HazardError('INVALID_INPUT','Rain pulse requires hours+1 samples')
    forcing_res=max(height,width)*resolution;fx=xmin-forcing_res;fy=ymin-forcing_res
    text=Path(cfg['hmc_template']).read_text()
    values={'sDomainName':"'abruzzo'",'dCN':'75','dCPI':'.9','iFlagRestart':'0','iFlagFlowDeep':'0','iFlagDynVeg':'0','iFlagEnergyBalance':'0','iFlagSoilParamsType':'1','iFlagInfiltRateVariable':'0','iFlagSnow':'0','iFlagVarDtPhysConv':'0','iFlagReleaseMass':'1','iFlagDebugLevel':'1','iSimLength':str(hours),'iDtModel':'3600','iDtPhysConv':'1','iTcMax':'0','sTimeStart':start.strftime('%Y%m%d%H%M'),'sTimeRestart':(start-dt.timedelta(hours=1)).strftime('%Y%m%d%H%M'),'iFlagTypeData_Output_Point':'1','a1dGeoForcing':f'{fy:.10f},{fx:.10f}','a1dResForcing':f'{forcing_res:.10f},{forcing_res:.10f}','a1iDimsForcing':'3,3'}
    for key,value in values.items():
        text,count=re.subn(r'(?m)^'+re.escape(key)+r'\s*=.*$',key+'='+value,text)
        if count!=1:raise HazardError('ENGINE_TEMPLATE',key)
    for key in re.findall(r'(?m)^(sPathData_\w+)\s*=',text):
        folder='static' if 'Static' in key else 'forcing' if ('Forcing' in key or 'Updating' in key) else 'output' if 'Output' in key else 'state' if 'State' in key else 'restart'
        text=re.sub(r'(?m)^'+re.escape(key)+r'\s*=.*$',key+"='"+str(hmc/folder)+"/'",text)
    (hmc/'model.info.txt').write_text(text)
    samples={v['at']:v['values'] for v in weather['records']}
    for hour in range(hours+1):
        moment=start+dt.timedelta(hours=hour);at=moment.isoformat().replace('+00:00','Z');met=samples[at]
        path=hmc/'forcing'/('hmc.forcing-grid.'+moment.strftime('%Y%m%d%H%M')+'.nc')
        with Dataset(path,'w',format='NETCDF4') as ds:
            ds.createDimension('south_north',3);ds.createDimension('west_east',3)
            for key,value in dict(ncols=3,nrows=3,xllcorner=fx,yllcorner=fy,cellsize=forcing_res,nodata_value=-9999.).items():ds.setncattr(key,value)
            for name,value,unit in [('Rain',options['rain_mm'][hour],'mm'),('AirTemperature',met['temperature_2m'],'C'),('IncRadiation',met['shortwave_radiation'],'W/m2'),('RelHumidity',met['relative_humidity_2m'],'%'),('Wind',met['wind_speed_10m'],'m/s'),('AirPressure',met['surface_pressure'],'hPa'),('Albedo',.23,'1'),('LAI',4,'1'),('AEvt',0,'mm'),('PEvt',0,'mm'),('FC',.5,'1')]:
                var=ds.createVariable(name,'f4',('south_north','west_east'),fill_value=-9999.);var.units=unit;var[:]=value
        with path.open('rb') as src,gzip.open(str(path)+'.gz','wb') as dst:dst.write(src.read())
        path.unlink()
    write_new(root/'hmc-input-mapping.json',dict(sections=sections,row_cell_area_m2=row_area.tolist(),reflex_mean_area_m2=mean_area,reflex_area_max_relative_error=float(np.max(np.abs(row_area/mean_area-1))),synthetic_rain_mm=options['rain_mm'],real_weather_id=weather['id'],static_parameters='Uncalibrated declared research constants',q0_policy='Synthetic reference only, not inferred bankfull'))
    execute([cfg['hmc_binary'],str(hmc/'model.info.txt')],work/'logs/hmc.log')
    log=(work/'logs/hmc.log').read_text(errors='replace');files=sorted((hmc/'output').glob('hmc.output-grid.*.nc.gz'))
    if 'SIMULATION END' not in log or re.search(r'\bERROR\b|\bFATAL\b|\bSTOP\b',log) or len(files)!=hours:raise HazardError('MODEL_INCOMPLETE','HMC log or output count invalid despite possible exit0')
    records=[];qvalues={s['stream']:[] for s in sections}
    for hour,file in enumerate(files):
        with Dataset('memory',memory=gzip.decompress(file.read_bytes())) as ds:
            q=np.ma.asarray(ds['Discharge'][:]);lo=np.asarray(ds['Longitude'][:]);la=np.asarray(ds['Latitude'][:])
            if q.shape!=(height,width) or ds['Discharge'].units!='m^3/s' or not np.isfinite(q.compressed()).all() or (q.compressed()<0).any():raise HazardError('INVALID_OUTPUT','HMC grid/units/values')
            expected_time=(start+dt.timedelta(hours=hour)).strftime('%Y-%m-%d_%H:%M:%S')
            if ds.time_coverage_end!=expected_time:raise HazardError('INVALID_TIME','HMC output timestamp differs')
            for s in sections:
                distance=(lo-s['longitude'])**2+(la-s['latitude'])**2;rr,cc=np.unravel_index(np.argmin(distance),distance.shape);delta=float(np.sqrt(distance[rr,cc]))
                if delta>resolution*.1 or np.ma.is_masked(q[rr,cc]):raise HazardError('REACH_MAPPING','HMC section grid coordinates differ')
                value=float(q[rr,cc]);qvalues[s['stream']].append(value);records.append(dict(stream=s['stream'],time=expected_time,Q_m3_s=value,coordinate_delta_deg=delta))
    rows=[]
    for sid,values in qvalues.items():rows.append(dict(stream=sid,Q0=options['q0_m3_s'],Q100=max(values)))
    if not any(v['Q100']>v['Q0'] for v in rows):raise HazardError('NO_FLOOD_EXCESS','Wet research fixture produced no excess discharge')
    pd.DataFrame(rows).to_csv(work/'discharge.csv',index=False)
    write_new(root/'hmc-reflex-bridge.json',dict(status='PASS',scope='TECHNICAL_IO_ONLY',records=records,reach_rows=rows,q0_evidence=options['q0_evidence'],unit='m3/s',upstream_Q100_label='No return-period claim',tconc_source='REFlEx generated; uncalibrated'))
    step(4)
    stats=pd.read_csv(work/'flood/T100/txt/flood_stats_T100_m.csv')
    if stats.empty or not np.isfinite(stats[['V_cut','v_i','diff_final']].values).all():raise HazardError('INVALID_OUTPUT','Nonfinite/empty REFlEx optimizers')
    write_new(root/'flood-native-result.json',dict(reaches=len(features),optimizer_rows=len(stats),hmc_output_files=len(files),depth_path='flood-work/flood/T100/rst/flood_map_T100_m.tif',qualification='UNQUALIFIED_RESEARCH',max_relative_optimizer_residual=float((stats.diff_final/np.maximum(stats.V_cut,1e-12)).max())))

if __name__=='__main__':
    root=Path(sys.argv[1])
    try:run(root)
    except Exception as exc:
        write_new(root/'worker-error.json',dict(code=exc.code if isinstance(exc,HazardError) else 'FLOOD_ERROR',message=str(exc)));raise
