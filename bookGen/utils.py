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