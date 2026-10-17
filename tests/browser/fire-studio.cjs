// Native verification is explicit and uses the VM API; no scientific host runtime.
const {spawnSync}=require('child_process');
const result=spawnSync(process.env.HAZARDIA_TEST_PYTHON||'python3',['tests/native/fire_sandbox_api.py',process.argv[2]],{stdio:'inherit'});
process.exitCode=result.status??1;
