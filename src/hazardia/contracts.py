"""Public compatibility facade plus domain-independent exchange boundaries.

Existing public validators retain signatures and behavior through the legacy
adapter; new exchange consumers use the generic names without hazard enums.
"""
from hazardia.adapters.legacy_contracts import (
    VERSION, SCHEMAS, validate, validate_request, validate_weather,
    validate_product, validate_observation, migrate_observation_010,
    migrate_run_manifest_020,
)
from hazardia.exchange import (
    validate_product as validate_exchange_product,
    validate_requirement as validate_exchange_requirement,
    check_compatibility as check_exchange_compatibility,
)

__all__ = [
    'VERSION', 'SCHEMAS', 'validate', 'validate_request', 'validate_weather',
    'validate_product', 'validate_observation', 'migrate_observation_010',
    'migrate_run_manifest_020', 'validate_exchange_product',
    'validate_exchange_requirement', 'check_exchange_compatibility',
]
