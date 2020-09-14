"""
Contains the UIList item for shelf
"""

import bpy


class BOOKGEN_UL_Shelves(bpy.types.UIList):
    """Defines the custom UIList item for shelf
    """

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname):
        """ Draws the UIList item for shelf
        """
        layout.prop(item, "name", text="", emboss=False)
