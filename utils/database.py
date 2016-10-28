

import pymongo

from . import connection, db

def create_indexes():
    """
    Create mongodb indexes.

    """

    # VCF collection indexes
    db.vcfs.drop_indexes()
    db.vcfs.create_index("name")
    db.vcfs.create_index("samples")
    db.vcfs.create_index( [ ("filename", pymongo.ASCENDING), ("fileformat", pymongo.ASCENDING), ("filedate", pymongo.ASCENDING) ], sparse=True )
    db.vcfs.create_index("INFO")
    db.vcfs.create_index("FORMAT")
    db.vcfs.create_index("FILTER")

    # Variant collection indexes
    db.variants.drop_indexes()
    db.variants.create_index("samples.sample")
    db.variants.create_index([("samples.sample", pymongo.ASCENDING),("samples.filter", pymongo.ASCENDING)], sparse=True)
    db.variants.create_index("samples.vcf_id")
    # Filter indexes
    db.variants.create_index([("chr",pymongo.ASCENDING),("pos",pymongo.ASCENDING),("info.END",pymongo.ASCENDING),("info.SVTYPE",pymongo.ASCENDING),("samples.sample",pymongo.ASCENDING)], sparse=True)
    db.variants.create_index([("alt",pymongo.ASCENDING),("info.SVTYPE",pymongo.ASCENDING),("samples.sample",pymongo.ASCENDING)], sparse=True)


def resetdb():
    """
    Drop database and recreate indexes.
    """
    connection.drop_database('vcf_explorer')
    create_indexes()
