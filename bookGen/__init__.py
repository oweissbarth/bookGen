# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================

"""
BookGen is a add-on for the 3D graphics software Blender. It allows to procedurally generate books.
"""

from bpy.app.handlers import persistent

from .properties import BookGenProperties, BookGenGroupingProperties, BookGenAddonProperties
from .utils import get_bookgen_collection
from .shelf_list import BOOKGEN_UL_Shelves
from .panel import (
    BOOKGEN_PT_ShelfPanel,
    BOOKGEN_PT_MainPanel,
    BOOKGEN_PT_LeaningPanel,
    BOOKGEN_PT_ProportionsPanel,
    BOOKGEN_PT_DetailsPanel,
    BOOKGEN_PT_BookPanel,
    BOOKGEN_PT_StackPanel)

from .generic_operators import (
    BOOKGEN_OT_Rebuild,
    BOOKGEN_OT_CreateSettings,
    BOOKGEN_OT_SetSettings,
    BOOKGEN_OT_RemoveSettings
)
from .shelf_operator import (
    BOOKGEN_OT_SelectShelf,
    BOOKGEN_OT_RemoveShelf)

from .stack_operator import (
    BOOKGEN_OT_SelectStack
)

from .preferences import BOOKGEN_AddonPreferences

bl_info = {
    "name": "BookGen",
    "description": "Generate books to fill shelves",
    "author": "Oliver Weissbarth, Seojin Sim",
    "version": (0, 9, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh",
    "warning": "Beta",
    "wiki_url": "",
    "category": "Add Mesh"}


classes = [
    BookGenProperties,
    BookGenGroupingProperties,
    BookGenAddonProperties,
    BOOKGEN_OT_Rebuild,
    BOOKGEN_OT_RemoveShelf,
    BOOKGEN_PT_MainPanel,
    BOOKGEN_PT_BookPanel,
    BOOKGEN_PT_ShelfPanel,
    BOOKGEN_PT_LeaningPanel,
    BOOKGEN_PT_ProportionsPanel,
    BOOKGEN_PT_DetailsPanel,
    BOOKGEN_OT_SelectShelf,
    BOOKGEN_UL_Shelves,
    BOOKGEN_OT_SelectStack,
    BOOKGEN_AddonPreferences,
    BOOKGEN_OT_CreateSettings,
    BOOKGEN_OT_SetSettings,
    BOOKGEN_OT_RemoveSettings,
    BOOKGEN_PT_StackPanel

]


def register():
    """
    Register all custom operators, panels, ui-lists and properties.
    """
    from bpy.utils import register_class
    import bpy

    for cls in classes:
        register_class(cls)

    bpy.types.Collection.BookGenGroupingProperties = bpy.props.PointerProperty(type=BookGenGroupingProperties)
    bpy.types.Scene.BookGenSettings = bpy.props.CollectionProperty(type=BookGenProperties)
    bpy.types.Scene.BookGenAddonProperties = bpy.props.PointerProperty(type=BookGenAddonProperties)

    bpy.app.handlers.load_post.append(bookgen_startup)


def unregister():
    """
    Unregister all custom operators, panels, ui-lists and properties.

    """
    import bpy
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.app.handlers.load_post.remove(bookgen_startup)


@persistent
def bookgen_startup(_dummy):
    """
    Ensure that the outline is disabled on start-up.
    """
    import bpy

    bpy.context.scene.BookGenAddonProperties.outline_active = False

    if not bpy.context.scene.BookGenSettings:
        bpy.context.scene.BookGenSettings.add()
