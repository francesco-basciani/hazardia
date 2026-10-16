"""Configure existing verified engines in one Linux VM; no install/network."""
import argparse,shutil,sys,subprocess,platform
from pathlib import Path
from hazardia.io import load,write_new,sha256,HazardError

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--engine-root',required=True);ap.add_argument('--output',default='runtime.json');ap.add_argument('--core-python',default='/usr/bin/python3');ap.add_argument('--grass-addon-base');args=ap.parse_args()
    root=Path(args.root).resolve();eng=Path(args.engine_root).resolve();app=Path(__file__).resolve().parents[1]
    originals=load(eng/'expected-guest-source-hashes.json')
    for path,digest in originals.items():
        if sha256(eng/path)!=digest:raise HazardError('ENGINE_SOURCE_DRIFT',path)
    target=root/'engines/reflex-compat';target.parent.mkdir(parents=True,exist_ok=True)
    patch=app/'patches/reflex-hand-boundary.patch'
    if not target.exists():
        shutil.copytree(eng/'reflex-src',target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        replacements=[('lib/reflex_tools_basins.py','    grid.clip_to(basin_mask_raster)\n','    grid.clip_to(basin_mask_raster, pad=(1,1,1,1))\n'),('reflex_step4_flood_mapping.py','            chunk_max, out_trans = rio_merge.merge(lista, method=custom_merge)\n','            chunk_max, out_trans = rio_merge.merge(lista, method=custom_merge, bounds=src_grid.bounds, res=src_grid.res)\n')]
        for name,old,new in replacements:
            file=target/name;s=file.read_text()
            if s.count(old)!=1:raise HazardError('PATCH_MISMATCH',name)
            file.write_text(s.replace(old,new,1))
    files={str(eng/p):h for p,h in originals.items()}
    files[str(eng/'hmc-bin/HMC_Model_V3_Exec.x')]=sha256(eng/'hmc-bin/HMC_Model_V3_Exec.x')
    for p in target.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':files[str(p)]=sha256(p)
    fire_import=eng/'fire-src'
    if (fire_import/'src/propagator').is_dir():fire_import=fire_import/'src'
    cfg=dict(schema_version='0.2.0',core_python=args.core_python,fire_python=str(eng/'fire-env/bin/python'),geo_python=str(eng/'reflex-env/bin/python'),fire_source=str(fire_import),reflex_source=str(target),hmc_binary=str(eng/'hmc-bin/HMC_Model_V3_Exec.x'),hmc_template=str(eng/'hmc-src/template.info.txt'),reflex_template=str(eng/'reflex-src/magra.json'),engine_files=files,engines=dict(PROPAGATOR='48b45078093692aa8dcca98f51849a5fbcd981a5',HMC='e6e95ecbc794431c4e6d09a81b3292704f3cca42',REFLEX='0dd5aa9803f7c163a4f6c3b42d9f69bce88a53bd'),reflex_patch_sha256=sha256(patch),minimum_free_bytes=1024**3,max_job_bytes=512*1024**2)
    if args.grass_addon_base:
        cfg['grass_addon_base']=str(Path(args.grass_addon_base).resolve())
        for p in (Path(args.grass_addon_base)/'bin').glob('*'):
            if p.is_file():cfg['engine_files'][str(p.resolve())]=sha256(p)
    cfg['environment']=dict(platform=platform.platform(),core_python=subprocess.check_output([args.core_python,'-VV'],text=True).strip(),fire_freeze=subprocess.check_output([cfg['fire_python'],'-m','pip','freeze','--all'],text=True).splitlines(),flood_freeze=subprocess.check_output([cfg['geo_python'],'-m','pip','freeze','--all'],text=True).splitlines())
    write_new(root/args.output,cfg)
    print('Configured pinned files',len(files))
if __name__=='__main__':main()
