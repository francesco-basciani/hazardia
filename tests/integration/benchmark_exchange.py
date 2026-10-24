"""Metadata view/check microbenchmark on frozen native jobs, no model execution."""
import argparse,json,platform,statistics,time,resource
from pathlib import Path
from hazardia.io import load,sha256,write_new
from hazardia.adapters.legacy_exchange import export_legacy_product
from hazardia.exchange import check_compatibility
from tests.integration.verify_exchange_runtime import requirement

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();assert platform.system()=='Linux'
    root=Path(a.run);out=Path(a.output);out.mkdir(parents=True,exist_ok=False);cases=load(root/'verification.json')['cases']
    protocol=dict(scope='FROZEN_NATIVE_METADATA_AND_HASH_MICROBENCHMARK',repetitions=30,meaning='Warm same process, caches not cleared; no simulation/browser/SLO claim',source_metadata={c['case']:sha256(root/(c['case']+'-jobs')/c['isolated_job']/'exchange-product.json') for c in cases},script_sha256=sha256(__file__),platform=platform.platform());write_new(out/'protocol.json',protocol);rows=[]
    for case in cases:
        folder=root/(case['case']+'-jobs')/case['isolated_job'];product=load(folder/'exchange-product.json');need=requirement(product);view=[];check=[]
        for _ in range(30):
            start=time.perf_counter();again=export_legacy_product(folder,available_at=product['time']['available_at']['value']);view.append((time.perf_counter()-start)*1000);assert again==product
            start=time.perf_counter();result=check_compatibility(product,need,root=folder);check.append((time.perf_counter()-start)*1000);assert result['status']=='COMPATIBLE'
        def stats(v):return dict(p50_ms=statistics.median(v),p95_ms=sorted(v)[28],max_ms=max(v),samples_ms=v)
        rows.append(dict(case=case['case'],status='PASS',exchange_bytes=(folder/'exchange-product.json').stat().st_size,legacy_export=stats(view),compatibility_with_hashes=stats(check)))
    result=dict(status='PASS',protocol=protocol,cases=rows,process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024);write_new(out/'verification.json',result);print(json.dumps(result),flush=True)
