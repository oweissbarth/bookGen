import bpy


class BOOKGEN_UL_Shelves(bpy.types.UIList):
    @staticmethod
    def draw_item(_context, layout, _data, item, _icon, _active_data, _active_propname):
        layout.prop(item, "name", text="", emboss=False)
