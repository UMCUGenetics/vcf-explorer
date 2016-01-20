"""
    Helper.py

    Helper utility functions
"""
import collections

def deep_update(source, overrides):
    """Update a nested dictionary or similar mapping.

    Modify ``source`` in place.
    """
    for key, value in overrides.iteritems():
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        elif isinstance(value, list):
            source[key] = source.get(key, []) + value
        else:
            source[key] = overrides[key]
    return source
