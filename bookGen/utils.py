import bpy

def get_bookgen_collection():
    for c in bpy.context.scene.collection.children:
        if c.name == "BookGen":
            return c

    col = bpy.data.collections.new("BookGen")
    bpy.context.scene.collection.children.link(col)
    return col

def get_shelf_collection(name):
    bookgen = get_bookgen_collection()
    for c in bookgen.children:
        if c.name == name:
            return c

    col = bpy.data.collections.new(name)
    bookgen.children.link(col)
    return col

def visible_objects_and_duplis(context):
    """Loop over (object, matrix) pairs (mesh only)"""

    for obj in context.visible_objects:
        if obj.type == 'MESH':
            yield (obj, obj.matrix_world.copy())

        if obj.instance_type != 'NONE':
            obj.dupli_list_create(context.scene)
            for dob in obj.dupli_list:
                obj_dupli = dob.object
                if obj_dupli.type == 'MESH':
                    yield (obj_dupli, dob.matrix.copy())


def obj_ray_cast(obj, matrix, ray_origin, ray_target):
    """Wrapper for ray casting that moves the ray into object space"""

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location
    else:
        return None