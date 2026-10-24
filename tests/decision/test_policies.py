import copy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest
import subprocess
import sys
from unittest.mock import patch

from hazardia.decision.policies import EXPOSURE, FIRE_IDEAL, POLICIES, policy_for, validate_header
from hazardia.decision.problem import validate
from hazardia.decision.verifier import verify, losses
from hazardia.io import HazardError
from tests.decision.test_fire_ideal import fixture as ideal_fixture
from tests.decision.test_verifier import fixture as exposure_fixture


class PolicyTests(unittest.TestCase):
    def test_policy_module_has_no_solver_or_validator_dependencies(self):
        code="from hazardia.decision.policies import FIRE_IDEAL;import sys;assert not {'jsonschema','highspy','numpy','rasterio','propagator'}.intersection(sys.modules)"
        r=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_legacy_exposure_semantics(self):
        p=exposure_fixture();self.assertIs(validate_header(p),EXPOSURE)
        self.assertEqual(EXPOSURE.loss_unit,'people');self.assertEqual(EXPOSURE.effect,'IMPACT_ONLY')
        self.assertFalse(EXPOSURE.exclusive_targets);self.assertFalse(EXPOSURE.verified_fallback)
        self.assertEqual(EXPOSURE.equipment_for(p['resources'][0]),'VEHICLE')
        self.assertEqual(EXPOSURE.verification_reserve_s,.1)

    def test_ideal_semantics_are_distinct(self):
        p=ideal_fixture();self.assertIs(validate_header(p),FIRE_IDEAL)
        self.assertEqual(FIRE_IDEAL.loss_unit,'weighted_priority_points')
        self.assertEqual(FIRE_IDEAL.required_skill,'FIRE_SUPPRESSION')
        self.assertTrue(FIRE_IDEAL.exclusive_targets);self.assertTrue(FIRE_IDEAL.verified_fallback)
        self.assertTrue(FIRE_IDEAL.empty_is_no_action);self.assertEqual(FIRE_IDEAL.verification_reserve_s,2)
        self.assertEqual(FIRE_IDEAL.equipment_for(p['resources'][0]),'waterline_action')

    def test_policy_metadata_is_immutable_and_declarations_are_copies(self):
        with self.assertRaises(FrozenInstanceError):FIRE_IDEAL.effect='IMPACT_ONLY'
        with self.assertRaises(TypeError):POLICIES['other']=EXPOSURE
        d=FIRE_IDEAL.declaration();d['loss_unit']='people'
        self.assertEqual(FIRE_IDEAL.declaration()['loss_unit'],'weighted_priority_points')

    def test_unknown_schema_policy_and_unit_do_not_default(self):
        for version in ['new',None,[],{},1]:
            with self.assertRaises(HazardError):policy_for(dict(schema_version=version))
        for key,value in [('domain','UNKNOWN'),('loss_unit','people'),('benefit_model','PHYSICAL_SUPPRESSION')]:
            p=ideal_fixture();p['policy'][key]=value
            with self.assertRaises(HazardError):validate(p)
            self.assertEqual(verify(p,[])['status'],'INVALID')

    def test_policy_headers_do_not_migrate_payloads(self):
        for p in [exposure_fixture(),ideal_fixture()]:
            before=copy.deepcopy(p);self.assertIs(validate(p),p);self.assertEqual(p,before)
        p=exposure_fixture();p['policy']=FIRE_IDEAL.declaration()
        with self.assertRaises(HazardError):validate(p)
        p=ideal_fixture();del p['policy']
        with self.assertRaises(HazardError):validate(p)

    def test_independent_checker_does_not_trust_changed_solver_skill(self):
        p=ideal_fixture();p['resources'][0]['record']['payload']['skills']=['UNQUALIFIED_SKILL']
        altered=replace(FIRE_IDEAL,required_skill='UNQUALIFIED_SKILL')
        with patch('hazardia.decision.policies.POLICIES',{'0.5.0':EXPOSURE,'0.6.0':altered}):
            validate(p)
            result=verify(p,[p['options'][0]['id']])
        self.assertIn('QUALIFICATION',{r['id'] for r in result['rules']})
        self.assertFalse(result['operationally_approvable'])

    def test_unknown_critical_constraints_are_still_rejected(self):
        for factory in [exposure_fixture,ideal_fixture]:
            for field in ['maintenance','skills','schedule','consumables']:
                p=factory();p['resources'][0]['record']['payload'][field]=None
                result=verify(p,[p['options'][0]['id']])
                self.assertNotEqual(result['status'],'VALIDATED_FOR_SIMULATION')
                self.assertFalse(result['operationally_approvable'])

    def test_loss_units_remain_independently_reported(self):
        self.assertIn('people',losses(exposure_fixture(),[])['unit'])
        self.assertIn('not people',losses(ideal_fixture(),[])['unit'])
        source=(Path(__file__).resolve().parents[2]/'src/hazardia/decision/verifier.py').read_text()
        self.assertNotIn('decision.policies',source);self.assertNotIn('highspy',source)
