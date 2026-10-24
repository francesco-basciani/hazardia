"""Catalog-backed selection of reviewed existing workers, never dynamic imports.

Only this table contains executable module names. Descriptors describe bindings;
they cannot supply commands, environments, policies or importable entry points.
"""
import os
from types import MappingProxyType
from hazardia.io import HazardError

# package id -> (legacy hazard, interpreter configuration key, fixed worker)
WORKERS = MappingProxyType({
    'hazardia.wildfire': ('FIRE', 'fire_python', 'hazardia.adapters.workers.fire'),
    'hazardia.flood': ('FLOOD', 'geo_python', 'hazardia.adapters.workers.flood'),
})
LEGACY_PACKAGES = MappingProxyType({hazard: package for package, (hazard, _, _) in WORKERS.items()})


def prepare(request, config, directory, environ):
    """Return the same two commands/environment plus an immutable-run receipt.

    Hash guards remain in pipeline before and after all work; timeout, process
    group isolation, cancellation and product validation remain in JobStore.
    """
    hazard = request['hazard']
    if hazard not in LEGACY_PACKAGES:
        raise HazardError('UNSUPPORTED_HAZARD', 'No adapter for ' + hazard)
    if hazard == 'FLOOD' and not request['options']['allow_experimental_patch']:
        raise HazardError('UNSUPPORTED_CONFIGURATION', 'Current terrain adapter requires declared experimental HAND/merge compatibility patch')
    # Import/discovery happens only in the isolated pipeline, never API startup.
    from hazardia.package_catalog import discover
    package_id = LEGACY_PACKAGES[hazard]
    try:
        description = discover().get(package_id).describe()
    except OSError as exc:
        raise HazardError('PACKAGE_IO', 'Reviewed local catalog unavailable') from exc
    except ValueError as exc:
        raise HazardError('PACKAGE_INVALID', 'Invalid local catalog JSON') from exc
    expected_hazard, python_key, worker = WORKERS[package_id]
    if description['legacy_hazard'] != expected_hazard:
        raise HazardError('PACKAGE_BINDING', 'Package does not match legacy hazard')
    versions = next(c['versions'] for c in description['contracts'] if c['kind'] == 'simulation_request')
    if request['schema_version'] not in versions:
        raise HazardError('PACKAGE_CONTRACT', 'Request version not described by selected package')
    for model in description['models']:
        if config.get('engines', {}).get(model['engine_ref']) != model['source_revision']:
            raise HazardError('PACKAGE_RUNTIME', 'Frozen runtime revision differs from reviewed package: ' + model['engine_ref'])
    env = dict(environ)
    if hazard == 'FIRE':
        env['PYTHONPATH'] = env['PYTHONPATH'] + os.pathsep + config['fire_source']
    command = [config[python_key], '-m', worker, str(directory)]
    product = [config['geo_python'], '-m', 'hazardia.adapters.workers.product', str(directory)]
    receipt = dict(schema='hazardia.adapter-binding/0.1.0', package=description,
                   command=command, product_command=product,
                   qualification='UNQUALIFIED_RESEARCH', operational_authorization='NOT_GRANTED')
    return command, product, env, receipt
