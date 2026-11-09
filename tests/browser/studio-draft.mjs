import assert from 'node:assert/strict';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../../src/hazardia/web/static/studio-draft.js',import.meta.url),'utf8');
const {snapshot,packDraft,unpackDraft}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const rows=[{id:'s',name:'triangolo',input:{resources:[{area:[[42,13],[43,14],[42,14]],at_minutes:30}]},job_id:null,submitted_input:null,pending:true,error:'transient'}];
const raw=packDraft(rows,'main',119);const d=unpackDraft(raw,'main');assert.deepEqual(d.snapshot,snapshot(rows));assert.deepEqual(d.snapshot.scenarios[0].input.resources,rows[0].input.resources);assert.equal('pending' in d.snapshot.scenarios[0],false);assert.equal(unpackDraft(raw,'example'),null);assert.equal(unpackDraft('{','main'),null);assert.equal(unpackDraft(JSON.stringify({version:1,scope:'main',revision:'119',snapshot:{scenarios:rows}}),'main'),null);assert.throws(()=>packDraft([{...rows[0],name:'x'.repeat(66000)}],'main',119));assert.equal(rows[0].pending,true);
console.log('PASS local draft preserves unsaved geometry/time, excludes transient state, isolates workspace scope, rejects corrupt/oversize payloads and does not mutate inputs');
