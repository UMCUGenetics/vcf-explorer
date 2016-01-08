

import pymongo

from . import connection

def create_indexes():
    """
    Create mongodb indexes.

    """
    db = connection.vcf_explorer
    variants = db.variants
    vcfs = db.vcfs
    samples = db.samples

    # VCF collection indexes
    vcfs.drop_indexes()
    vcfs.create_index("name")
    vcfs.create_index("samples")
    vcfs.create_index( [ ("filename", pymongo.ASCENDING), ("fileformat", pymongo.ASCENDING), ("filedate", pymongo.ASCENDING) ], sparse=True )
    vcfs.create_index("run")

    # Variant collection indexes
    variants.drop_indexes()
    variants.create_index("samples.id")
    variants.create_index("samples.run")
    variants.create_index([("samples.id", pymongo.ASCENDING),("samples.filter", pymongo.ASCENDING)], sparse=True)
    variants.create_index( [ ("chr", pymongo.ASCENDING), ("pos", pymongo.ASCENDING), ("variant_info.chr2", pymongo.ASCENDING), ("variant_info.end", pymongo.ASCENDING), ("variant_info.svtype",         pymongo.ASCENDING),("variant_info.ct", pymongo.ASCENDING) ], sparse=True )

def resetdb():
    """
    Drop database and recreate indexes.
    """
    connection.drop_database('vcf_explorer')
    create_indexes()
