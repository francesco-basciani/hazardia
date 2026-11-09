import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const code=readFileSync('src/hazardia/web/static/ideal-planner.js','utf8').replace("import {comparisonVerdict} from '/fire-comparison-status.js';","const comparisonVerdict=()=>'';");
const {savedPlanMatches}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const b={ignitions:[{id:'i',point:[42,13],at_minutes:0}],resources:[],hours:12,seed:1729,moisture_percent:10,weather_source:'FORECAST',weather_changes:[],start_at:'2026-10-18T18:00:00Z',moisture_model:'MANUAL',realizations:4,antecedent_hours:0};
const unit={id:'u',category:'waterline_action',area:[[42,13],[42.001,13],[42.001,13.001]],at_minutes:0,effect:'fuel_removal'};
assert(savedPlanMatches(b,b,[unit]));assert(savedPlanMatches({...b,resources:[unit]},b,[{...unit,target_name:'display metadata'}]));
for(const [key,value] of [['hours',24],['seed',7],['moisture_model','HFFMC_1977'],['start_at','2026-10-19T18:00:00Z'],['realizations',8],['antecedent_hours',168]])assert(!savedPlanMatches({...b,[key]:value},b,[unit]),key);
assert(!savedPlanMatches({...b,resources:[{...unit,at_minutes:30}]},b,[unit]));assert(!savedPlanMatches({...b,ignitions:[{...b.ignitions[0],point:[42.01,13]}]},b,[unit]));assert(!savedPlanMatches({...b,ignitions:[]},b));assert(!savedPlanMatches(b,null));
console.log('PASS saved plan matches frozen context and proposed resources; rejects changed location/time/model/ensemble/antecedent/actions and missing context');
