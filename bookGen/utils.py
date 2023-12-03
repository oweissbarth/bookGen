""" This file contains utility functions.
TODO split this file.
"""

import os

import bpy
import bpy_extras.view3d_utils
from mathutils import Vector


def get_bookgen_version():
    """Returns the version number of bookgen

    Returns:
        (int, int, int): the version of bookgen
    """
    return bookgen_version


def has_bookgen_collection(context):
    """Check if a bookgen collection exists in the active scene

    Args:
        context (bpy.types.Context): the current execution context

    Returns:
        bool: true if the scene contains a bookgen collection, otherwise false
    """
    return bool(context.scene.BookGenAddonProperties.collection)


def get_bookgen_collection(context, create=True):
    """Retrieves the bookgen collection

    Args:
        create (bool, optional): Create the collection if none found. Defaults to True.

    Returns:
        bpy.types.Collection: the bookgen collection
    """

    if context.scene.BookGenAddonProperties.collection:
        return context.scene.BookGenAddonProperties.collection

    name = "BookGen"

    if name in bpy.data.collections.keys():
        collection = bpy.data.collections[name]
        context.scene.BookGenAddonProperties.collection = collection
        return collection

    if create:
        collection = bpy.data.collections.new(name)
        context.scene.collection.children.link(collection)
        context.scene.BookGenAddonProperties.collection = collection

    else:
        collection = None
    return collection


def get_shelf_collection(context, name):  # TODO make name generic
    """Retrieves a shelf collection by name

    Args:
        name (str): name of the collection

    Returns:
        bpy.types.Collection: the shelf collection or None
    """
    bookgen = get_bookgen_collection(context)
    for collection in bookgen.children:
        if collection.name == name:
            return collection

    col = bpy.data.collections.new(name)
    bookgen.children.link(col)
    return col


def get_shelf_collection_by_index(context, index, create=False):
    """Retrieves a shelf collection by index

    Args:
        index (int): index of the collection

    Returns:
        bpy.types.Collection: the shelf collection or None
    """
    bookGen = get_bookgen_collection(context, create)
    if bookGen is None or index < 0 or index >= len(bookGen.children):
        return None
    return bookGen.children[index]


def visible_objects_and_duplis(context):
    """Loop over (object, matrix) pairs (mesh only)"""

    depsgraph = context.evaluated_depsgraph_get()
    for dup in depsgraph.object_instances:
        if dup.is_instance:  # Real dupli instance
            obj = dup.instance_object
            yield (obj, dup.matrix_world.copy())
        else:  # Usual object
            obj = dup.object
            yield (obj, obj.matrix_world.copy())


def obj_ray_cast(context, obj, matrix, ray_origin, ray_target):
    """Wrapper for ray casting that moves the ray into object space"""

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, face = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location, normal, face
    else:
        return None, None, None


def project_to_screen(context, world_space_point):
    """Returns the 2d location of a world space point inside the 3D viewport"""
    region = context.region
    rv3d = context.space_data.region_3d
    return bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, world_space_point, default=(0, 0))


bookGen_directory = os.path.dirname(os.path.realpath(__file__))


def get_shelf_parameters(context, shelf_id=0, settings=None):
    """Collects the parameters for a specific shelf

    Args:
        shelf_id (int, optional): The id of the shelf for which the parameters are collected. Defaults to 0.

    Returns:
        Dict[str, any]: a dictionary of the shelf parameters
    """
    if settings:
        properties = settings
    else:
        properties = get_bookgen_collection(context).BookGenProperties

    parameters = {
        "scale": properties.scale,
        "seed": properties.seed + shelf_id,
        "alignment": properties.alignment,
        "lean_amount": properties.lean_amount,
        "lean_direction": properties.lean_direction,
        "lean_angle": properties.lean_angle,
        "rndm_lean_angle_factor": properties.rndm_lean_angle_factor,
        "book_height": properties.book_height,
        "rndm_book_height_factor": properties.rndm_book_height_factor,
        "book_width": properties.book_width,
        "rndm_book_width_factor": properties.rndm_book_width_factor,
        "book_depth": properties.book_depth,
        "rndm_book_depth_factor": properties.rndm_book_depth_factor,
        "cover_thickness": properties.cover_thickness,
        "rndm_cover_thickness_factor": properties.rndm_cover_thickness_factor,
        "textblock_offset": properties.textblock_offset,
        "rndm_textblock_offset_factor": properties.rndm_textblock_offset_factor,
        "spine_curl": properties.spine_curl,
        "rndm_spine_curl_factor": properties.rndm_spine_curl_factor,
        "hinge_inset": properties.hinge_inset,
        "rndm_hinge_inset_factor": properties.rndm_hinge_inset_factor,
        "hinge_width": properties.hinge_width,
        "rndm_hinge_width_factor": properties.rndm_hinge_width_factor,
        "subsurf": properties.subsurf,
        "cover_material": properties.cover_material,
        "page_material": properties.page_material,
    }
    return parameters


def get_stack_parameters(context, shelf_id=0, settings=None):
    """Collects the parameters for a specific stack

    Args:
        shelf_id (int, optional): The id of the shelf for which the parameters are collected. Defaults to 0.

    Returns:
        Dict[str, any]: a dictionary of the shelf parameters
    """
    if settings:
        properties = settings
    else:
        properties = get_bookgen_collection(context).BookGenProperties

    parameters = {
        "scale": properties.scale,
        "seed": properties.seed + shelf_id,
        "rotation": properties.rotation,
        "book_height": properties.book_height,
        "rndm_book_height_factor": properties.rndm_book_height_factor,
        "book_width": properties.book_width,
        "rndm_book_width_factor": properties.rndm_book_width_factor,
        "book_depth": properties.book_depth,
        "rndm_book_depth_factor": properties.rndm_book_depth_factor,
        "cover_thickness": properties.cover_thickness,
        "rndm_cover_thickness_factor": properties.rndm_cover_thickness_factor,
        "textblock_offset": properties.textblock_offset,
        "rndm_textblock_offset_factor": properties.rndm_textblock_offset_factor,
        "spine_curl": properties.spine_curl,
        "rndm_spine_curl_factor": properties.rndm_spine_curl_factor,
        "hinge_inset": properties.hinge_inset,
        "rndm_hinge_inset_factor": properties.rndm_hinge_inset_factor,
        "hinge_width": properties.hinge_width,
        "rndm_hinge_width_factor": properties.rndm_hinge_width_factor,
        "subsurf": properties.subsurf,
        "cover_material": properties.cover_material,
        "page_material": properties.page_material,
        "stack_top_face": properties.stack_top_face,
    }
    return parameters


def ray_cast(context, mouse_x, mouse_y):
    """Shoots a ray from the cursor position into the scene and returns the closest intersection

    Args:
        mouse_x (float): x position of the cursor in pixels
        mouse_y (float): y position of the cursor in pixels

    Returns:
        (Vector, Vector, int, bpy.types.Object): A tuple containing the position, normal,
                                                 face id and object of the closest intersection
    """
    region = context.region
    region_data = context.space_data.region_3d

    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, region_data, (mouse_x, mouse_y))
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, region_data, (mouse_x, mouse_y))

    ray_target = ray_origin + view_vector

    best_length_squared = -1.0
    closest_loc = None
    closest_normal = None
    closest_obj = None
    closest_face = None

    for obj, matrix in visible_objects_and_duplis(context):
        if obj.type == "MESH":
            hit, normal, face = obj_ray_cast(context, obj, matrix, ray_origin, ray_target)
            if hit is not None:
                _, rot, _ = matrix.decompose()
                hit_world = matrix @ hit
                normal_world = rot.to_matrix() @ normal
                length_squared = (hit_world - ray_origin).length_squared
                if closest_loc is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    closest_loc = hit_world
                    closest_normal = normal_world
                    closest_face = face
                    closest_obj = obj

    return closest_loc, closest_normal, closest_face, closest_obj


def get_click_on_plane(context, mouse_x, mouse_y, position, normal):
    """Returns the 3d position of the intersection of the mouse ray with a given plane

    Args:
        context (bpy.types.Context): the current execution context
        mouse_x (int): mouse position in pixels
        mouse_y (int): mouse y position in pixels
        position (mathutils.Vector): a point on the plane
        normal (mathutils.Vector): the normal of the plane
    """
    region = context.region
    region_data = context.space_data.region_3d

    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, region_data, (mouse_x, mouse_y))
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, region_data, (mouse_x, mouse_y))

    denominator = view_vector.dot(normal)
    if denominator == 0:
        return None
    t = (position - ray_origin).dot(normal) / denominator

    return ray_origin + t * view_vector


def get_click_face(context, mouse_x, mouse_y):
    """Shoots a ray from the cursor position into the scene and returns the closest intersection object and face id

    Args:
        mouse_x (float): x position of the cursor in pixels
        mouse_y (float): y position of the cursor in pixels

    Returns:
        (bpy.types.Object, int): A tuple containing the object and face id
    """
    _, _, closest_face, closest_obj = ray_cast(context, mouse_x, mouse_y)
    return closest_obj, closest_face


def get_click_position_on_object(context, mouse_x, mouse_y):
    """Shoots a ray from the cursor position into the scene and returns the closest intersection

    Args:
        mouse_x (float): x position of the cursor in pixels
        mouse_y (float): y position of the cursor in pixels

    Returns:
        (Vector, Vector): A tuple containing the position and normal
    """
    closest_loc, closest_normal, _, _ = ray_cast(context, mouse_x, mouse_y)

    return closest_loc, closest_normal


def vector_scale(vector_a, vector_b):
    """Multiply two vectors component-wise

    Args:
        vector_a (Vector): Vector a
        vector_b (Vector): Vector b

    Returns:
        Vector: Result
    """
    return Vector(x * y for x, y in zip(vector_a, vector_b))


def get_grouping_index_by_name(context, name):
    """Returns the grouping index based on a given name

    Args:
        context (bpy.types.Context): the execution context
        name (str): the name of the grouping

    Returns:
        int: the grouping index
    """
    for i, c in enumerate(get_bookgen_collection(context).children):
        if c.name == name:
            return i
    return -1


def compose_grouping_name(context, grouping_type, grouping_id):
    """Constructs a grouping name from the grouping type, context and id

    Args:
        context (bpy.types.Context): the current execution context
        grouping_type (str): shelf or stack
        grouping_id (int): the id of the grouping

    Returns:
        str: the name of the grouping
    """
    return grouping_type + "_" + str(grouping_id) + "_" + context.scene.name


def get_free_shelf_id(context):
    """Finds the next unused shelf id

    Returns:
        int: the next unused shelf id
    """
    return get_free_id(context, "shelf")


def get_free_stack_id(context):
    """Finds the next unused stack id

    Returns:
        int: the next unused shelf id
    """
    return get_free_id(context, "stack")


def get_free_id(context, grouping_type: str):
    """Finds the next unused id of the given type

    Args:
        grouping_type (str) : the type of id to find

    Returns:
        int: the next unused id
    """
    groupings = get_bookgen_collection(context).children

    names = list(map(lambda x: x.name, groupings))
    element_id = 0
    while True:
        if compose_grouping_name(context, grouping_type, element_id) not in names:
            return element_id
        element_id += 1


def get_active_grouping(context, create=True):
    """Get the collection of the active grouping

    Returns:
        bpy.types.Collection: the collection of the active grouping
    """
    shelf_id = context.scene.BookGenAddonProperties.active_shelf
    return get_shelf_collection_by_index(context, shelf_id, create=create)


def get_active_settings(context, create=True):
    """Retrieve the currently active bookGen settings

    Args:
        context (bpy.types.Context): the execution context

    Returns:
        BookGenProperties: the active settings or None
    """
    collection = get_active_grouping(context, create)
    if collection is None:
        return None
    settings_name = collection.BookGenGroupingProperties.settings_name
    for settings in context.scene.BookGenSettings:
        if settings.name == settings_name:
            return settings
    return None


def get_settings_by_name(context, name):
    """Retrieve the bookGen settings by name

    Args:
        context (bpy.types.Context): the execution context
        name (str): the name of the settings

    Returns:
        BookGenProperties: the settings or None
    """
    for settings in context.scene.BookGenSettings:
        if settings.name == name:
            return settings
    return None


def get_settings_for_new_grouping(context):
    """Retrieve settings for a new grouping.
    If there are active settings return them.
    Otherwise select the first settings the list
    Otherwise create new default settings

    Args:
        context ([type]): [description]

    Returns:
        [type]: [description]
    """

    # check for active settings
    active_settings = get_active_settings(context)
    if active_settings:
        return active_settings

    # otherwise  check for existing settings
    if len(context.scene.BookGenSettings) > 0:
        return context.scene.BookGenSettings[0]

    # otherwise create default settings
    settings = context.scene.BookGenSettings.add()
    settings.name = settings.name  # While this looks useless it actually sets the name to the default name
    return settings
