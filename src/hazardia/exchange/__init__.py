"""Domain-independent metadata contracts and conservative compatibility checks.

No simulator/solver imports, dynamic execution, conversions or data resampling.
"""
from hazardia.exchange.contracts import validate_product, validate_requirement
from hazardia.exchange.compatibility import check_compatibility

__all__ = ['validate_product', 'validate_requirement', 'check_compatibility']
