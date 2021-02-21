"""This file contains versioning functionality
"""
import logging

log = logging.getLogger("bookGen.versioning")


def handle_version_upgrade(scene):
    """ Upgrades the given scene to the current bookGen version

    Args:
        scene (bpy.types.Scene): the scene that should be upgraded
    """
    if tuple(scene.BookGenAddonProperties.version) < (1,0,1):
        version_upgrade_collection_pointer_property(scene)


def version_upgrade_collection_pointer_property(scene):
    """ In versions before 1.0.1 the bookGen collection was identified by the name.
        Starting from 1.0.1 the collection is identified by a PointerProperty in BookGenAddonProperties

    Args:
        scene (bpy.types.Scene): the scene that should be upgraded
    """
    log.info("Performing version upgrade: collection_pointer_property on scene %s" % scene.name)
    if "BookGen" in scene.collection.children.keys():
        scene.BookGenAddonProperties.collection = scene.collection.children["BookGen"]
