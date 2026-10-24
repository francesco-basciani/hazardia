"""Reviewed, immutable policy semantics for existing decision contracts only.

Not a universal formulation or a dynamic plugin registry. No solver predicates,
constraint rows, resource data, or verifier implementation are shared here.
"""
from dataclasses import dataclass
from types import MappingProxyType

from hazardia.io import HazardError

def require(condition,code,message):
    if not condition:raise HazardError(code,message)

BASE_FIELDS = frozenset({'schema_version','kind','id','planning_at','data_cutoff','mode',
                         'resources','events','scenarios','options','regions','commitments','settings'})
RESOURCE_FIELDS = frozenset({'id','home_region','record'})


@dataclass(frozen=True)
class DecisionPolicy:
    policy_id: str
    schema_version: str
    mode: str
    declaration_items: tuple
    resource_categories: tuple
    required_skill: str
    fixed_equipment: str | None
    effect: str
    exclusive_targets: bool
    verification_reserve_s: float
    empty_is_no_action: bool
    verified_fallback: bool
    loss_unit: str

    def declaration(self):
        return dict(self.declaration_items)

    def equipment_for(self, resource):
        return self.fixed_equipment if self.fixed_equipment is not None else resource.get('category')

    @property
    def problem_fields(self):
        return BASE_FIELDS | ({'policy'} if self.declaration_items else set())

    @property
    def resource_fields(self):
        return RESOURCE_FIELDS | ({'category'} if self.resource_categories else set())


EXPOSURE = DecisionPolicy('RESEARCH_EXPOSURE','0.5.0','RESEARCH_RETROSPECTIVE',(),(),
                          'EVACUATION','VEHICLE','IMPACT_ONLY',False,.1,False,False,'people')
FIRE_IDEAL = DecisionPolicy('FIRE_IDEAL_ASSIGNMENT','0.6.0','RESEARCH_IDEAL',
                           (('domain','FIRE_IDEAL_ASSIGNMENT'),('loss_unit','weighted_priority_points'),
                            ('benefit_model','EXCLUSIVE_AREA_COVERAGE_PROXY')),
                           ('waterline_action','canadair','helicopter','heavy_action'),
                           'FIRE_SUPPRESSION',None,'IDEAL_ASSET_COVERAGE',True,2,True,True,
                           'weighted_priority_points')
POLICIES = MappingProxyType({p.schema_version:p for p in (EXPOSURE,FIRE_IDEAL)})


def policy_for(problem):
    """Version selection cannot silently default an unknown policy to exposure."""
    require(isinstance(problem,dict) and problem.get('schema_version') in ('0.5.0','0.6.0'),
            'INVALID_INPUT','Strict decision_problem0.5.0 required')
    policy = POLICIES[problem['schema_version']]
    if policy.declaration_items:
        require(problem.get('policy') == policy.declaration(),
                'INVALID_INPUT','Explicit ideal priority policy required')
    return policy


def validate_header(problem):
    # Match the old order/messages: shape/version, declaration, then mode.
    ideal = isinstance(problem,dict) and problem.get('schema_version') == '0.6.0'
    fields = FIRE_IDEAL.problem_fields if ideal else EXPOSURE.problem_fields
    require(isinstance(problem,dict) and set(problem) == fields and
            problem.get('schema_version') in ('0.5.0','0.6.0') and problem.get('kind') == 'decision_problem',
            'INVALID_INPUT','Strict decision_problem0.5.0 required')
    policy = policy_for(problem)
    require(problem['mode'] == policy.mode,'INVALID_INPUT','Only retrospective research decisions enabled')
    return policy
