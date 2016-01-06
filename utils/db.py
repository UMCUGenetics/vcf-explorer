

import pymongo

from . import connection

def create_indexes():
    """
    Create mongodb indexes.

    """
    db = connection.vcf_explorer
    variants = db.variants
    runs = db.runs
    runs.drop_indexes()
    runs.create_index("name")
    runs.create_index("samples")

    variants.drop_indexes()
    variants.create_index("samples.id")
    variants.create_index("samples.run")
    variants.create_index([("samples.id", pymongo.ASCENDING),("samples.filter", pymongo.ASCENDING)], sparse=True)

def resetdb():
    """
    Drop database and recreate indexes.
    """
    connection.drop_database('vcf_explorer')
    create_indexes()
