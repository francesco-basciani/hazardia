"""Prepare the production spatial policy against a checksummed frozen context, offline."""
import pathlib,sys
from unittest.mock import patch
from hazardia.io import load,write_new,sha256
from hazardia.decision.fire_ideal import prepare
from hazardia.decision.fire_priorities import DEFAULT_WEIGHTS
r=pathlib.Path('/home/hazardia/hazardia-runtime');out=r/'runs/castelli-dry-v2-plan-20261028';p=load(out/'protocol.json');assets=load(out/'assets.json');assert sha256(out/'assets.json')==p['frozen_context_sha256']
weights=dict(DEFAULT_WEIGHTS,residential=100,settlement=100,hospital=30,healthcare=30,school=25,fire_station=25,power_line=15,railway=15,critical_infrastructure=10)
body=dict(job_id=load(out/'baseline.json')['job_id'],fleet=p['fleet'],weights=weights,robust=.5,assumptions_confirmed=True,planning_minutes=0);write_new(out/'planning-request.json',body)
# Explicit offline fixture dependency injection; no runtime source, provider clock or data rewritten.
with patch('hazardia.territorial_context.acquire',return_value=assets):problem,context=prepare(r,body,out/'prepared')
print({'options':len(problem['options']),'targets':len(problem['events']),'exposed_assets':[(a['feature_id'],a['category'],a['nominal_probability'],a['stress_probability']) for a in context['assets'] if a['stress_probability']>0]})
