"""Differential command/error tests against the unchanged pre-A3 selector."""
import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from hazardia.adapters.dispatch import prepare
from hazardia.adapters.pipeline import main
from hazardia.io import HazardError, load, sha256, write_new
from hazardia.package_catalog import APPROVED_MODELS


def legacy(request, cfg, root, environ):
    # Frozen old selection logic only, independently of new lookup metadata.
    env=dict(environ)
    if request['hazard']=='FIRE':
        env['PYTHONPATH']=env['PYTHONPATH']+os.pathsep+cfg['fire_source']
        command=[cfg['fire_python'],'-m','hazardia.adapters.workers.fire',str(root)]
    elif request['hazard']=='FLOOD':
        if not request['options']['allow_experimental_patch']:
            raise HazardError('UNSUPPORTED_CONFIGURATION','Current terrain adapter requires declared experimental HAND/merge compatibility patch')
        command=[cfg['geo_python'],'-m','hazardia.adapters.workers.flood',str(root)]
    else:raise HazardError('UNSUPPORTED_HAZARD','No adapter for '+request['hazard'])
    return command,[cfg['geo_python'],'-m','hazardia.adapters.workers.product',str(root)],env


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.cfg=dict(fire_python='/isolated/fire python',geo_python='/isolated/geo python',fire_source='/pinned/source',engine_files={},engines={engine:revision for bindings in APPROVED_MODELS.values() for engine,_,revision in bindings})
        self.env=dict(PYTHONPATH='/application/src',NUMBA_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PROJ_LIB='/usr/share/proj',GRASS_ADDON_BASE='/grass',OTHER='preserved')

    def req(self, hazard='FIRE', version='0.2.0'):
        return dict(hazard=hazard,schema_version=version,options=dict(allow_experimental_patch=True))

    def test_same_commands_environment_and_no_input_mutation(self):
        for hazard,versions in [('FIRE',['0.2.0','0.3.0','0.4.0']),('FLOOD',['0.2.0','0.3.0'])]:
            for version in versions:
                req=self.req(hazard,version);before=copy.deepcopy((req,self.cfg,self.env))
                actual=prepare(req,self.cfg,'/jobs/path with spaces',self.env)
                self.assertEqual(actual[:3],legacy(req,self.cfg,'/jobs/path with spaces',self.env))
                self.assertEqual((req,self.cfg,self.env),before)
                self.assertEqual(actual[3]['package']['legacy_hazard'],hazard)
                self.assertEqual(actual[3]['operational_authorization'],'NOT_GRANTED')

    def test_old_guard_codes_and_messages_precede_catalog(self):
        for req in [self.req('UNKNOWN'),self.req('FLOOD')]:
            req['options']['allow_experimental_patch']=False
            with patch('hazardia.package_catalog.discover',side_effect=AssertionError('must not discover')):
                with self.assertRaises(HazardError) as a:prepare(req,self.cfg,'/job',self.env)
            with self.assertRaises(HazardError) as b:legacy(req,self.cfg,'/job',self.env)
            self.assertEqual((a.exception.code,str(a.exception)),(b.exception.code,str(b.exception)))

    def test_missing_or_malformed_catalog_is_classified(self):
        for exception,code in [(FileNotFoundError('missing'),'PACKAGE_IO'),(ValueError('JSON'),'PACKAGE_INVALID')]:
            with patch('hazardia.package_catalog.discover',side_effect=exception):
                with self.assertRaises(HazardError) as e:prepare(self.req(),self.cfg,'/job',self.env)
            self.assertEqual(e.exception.code,code)

    def test_revision_missing_or_changed_is_classified(self):
        for engines in [{},{'PROPAGATOR':'a'*40}]:
            cfg=dict(self.cfg,engines=engines)
            with self.assertRaises(HazardError) as e:prepare(self.req(),cfg,'/job',self.env)
            self.assertEqual(e.exception.code,'PACKAGE_RUNTIME')

    def test_catalog_failure_never_falls_back_or_starts_worker(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_new(root/'request.json',self.req());write_new(root/'runtime.json',self.cfg)
            with patch('hazardia.package_catalog.discover',side_effect=HazardError('PACKAGE_DIGEST','drift')),patch('hazardia.adapters.pipeline.subprocess.run') as run:
                self.assertEqual(main(root),1);run.assert_not_called()
            self.assertEqual(load(root/'worker-error.json')['code'],'PACKAGE_DIGEST')
            self.assertFalse((root/'adapter-binding.json').exists())

    def test_source_hash_guard_before_discovery_and_after_product(self):
        for when in ['before','after']:
            with self.subTest(when=when), tempfile.TemporaryDirectory() as d:
                root=Path(d);engine=root/'engine';engine.write_bytes(b'original')
                cfg=dict(self.cfg,engine_files={str(engine):sha256(engine)})
                write_new(root/'request.json',self.req());write_new(root/'runtime.json',cfg)
                if when=='before':engine.write_bytes(b'changed')
                def mutate(command,**kwargs):
                    if 'hazardia.adapters.workers.product' in command:engine.write_bytes(b'changed')
                with patch.dict(os.environ,self.env),patch('hazardia.adapters.pipeline.subprocess.run',side_effect=mutate) as run:
                    self.assertEqual(main(root),1)
                self.assertEqual(load(root/'worker-error.json')['code'],'ENGINE_SOURCE_DRIFT')
                self.assertEqual(run.call_count,0 if when=='before' else 2)

    def test_receipt_frozen_and_calls_match_old_path(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);req=self.req();write_new(root/'request.json',req);write_new(root/'runtime.json',self.cfg)
            with patch.dict(os.environ,self.env),patch('hazardia.adapters.pipeline.subprocess.run') as run:
                self.assertEqual(main(root),0)
                commands,product,env=legacy(req,self.cfg,root,os.environ)
                self.assertEqual(run.call_args_list[0].args[0],commands)
                self.assertEqual(run.call_args_list[1].args[0],product)
                self.assertEqual(run.call_args_list[0].kwargs,dict(env=env,check=True))
            receipt=load(root/'adapter-binding.json')
            self.assertEqual(receipt['request_sha256'],sha256(root/'request.json'))
            self.assertEqual(receipt['runtime_sha256'],sha256(root/'runtime.json'))
            before=(root/'adapter-binding.json').read_bytes()
            with patch.dict(os.environ,self.env),patch('hazardia.adapters.pipeline.subprocess.run') as run:
                self.assertEqual(main(root),1);run.assert_not_called()
            self.assertEqual((root/'adapter-binding.json').read_bytes(),before)

    def test_native_worker_error_is_preserved_product_not_started(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_new(root/'request.json',self.req());write_new(root/'runtime.json',self.cfg)
            def fail(*args,**kwargs):
                write_new(root/'worker-error.json',dict(code='FIRE_ERROR',message='native failure'))
                raise subprocess.CalledProcessError(1,args[0])
            with patch.dict(os.environ,self.env),patch('hazardia.adapters.pipeline.subprocess.run',side_effect=fail) as run:
                self.assertEqual(main(root),1);self.assertEqual(run.call_count,1)
            self.assertEqual(load(root/'worker-error.json')['code'],'FIRE_ERROR')
