"""Create an opt-in two-map case from an audited completed optimizer replay. Never overwrite."""
import argparse,copy,re
from pathlib import Path
from hazardia.io import load,write_new,HazardError

def prepare(runtime,comparison,ident):
 root=Path(runtime)
 if not re.fullmatch('ideal-native-[a-f0-9]{32}',comparison) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',ident):raise HazardError('INVALID_INPUT','Known comparison and safe new case id required')
 folder=root/'web-state'/comparison;replay=load(folder/'replay.json');evaluation=load(folder/'evaluation-native.json');decision=load(root/'web-state'/replay['decision_id']/'ideal-result.json');scenarios=[]
 if evaluation['status']!='COMPARISON_EVALUATED':raise HazardError('DEPENDENCY_UNAVAILABLE','Completed native evaluation required')
 for kind in ['A','B']:
  job=root/'jobs'/replay['jobs'][kind]
  if not (job/'manifest.json').is_file():raise HazardError('DEPENDENCY_UNAVAILABLE','Completed native pair required')
  input=copy.deepcopy(decision['ideal']['baseline_input'])
  if kind=='B':input['resources']=[{k:v for k,v in u.items() if k not in ['target_id','target_name']} for u in decision['ideal']['proposed_resources']]
  scenarios.append(dict(id='optimized-pair-'+kind.lower(),name='Senza interventi' if kind=='A' else 'Squadre · piano ottimizzatore',input=input,submitted_input=copy.deepcopy(input),job_id=replay['jobs'][kind]))
 rows={r['case']:r for r in evaluation['rows']};hours=scenarios[0]['input']['hours'];members=scenarios[0]['input'].get('realizations',2)
 description=f"Innesco ipotetico, terreno e previsione meteorologica congelati, stessi semi, {members} realizzazioni per {hours} ore. Interventi ideali dal piano verificato, non efficacia operativa. Superficie media A/B: {rows['A']['area_ha']:.3f}/{rows['B']['area_ha']:.3f} ha; indice sulle priorità A/B: {rows['A']['native_priority_index']:.3f}/{rows['B']['native_priority_index']:.3f}. Confronto {comparison}; non ricostruzione di evento osservato."
 case=dict(id=ident,title='Confronto fisico · senza interventi / piano ottimizzato',description=description,qualification='PAIRED_REAL_INPUTS_IDEAL_INTERVENTIONS_UNCALIBRATED',source_url='https://open-meteo.com/en/docs/dwd-api',initial_hour=hours,scenarios=scenarios)
 path=root/'web-assets/fire-cases'/(ident+'.json');path.parent.mkdir(parents=True,exist_ok=True);write_new(path,case);return path
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',required=True);p.add_argument('--comparison',required=True);p.add_argument('--case',required=True);a=p.parse_args();print(prepare(a.runtime,a.comparison,a.case))
