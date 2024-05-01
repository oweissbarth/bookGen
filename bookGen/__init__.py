# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2023 Oliver Weissbarth
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
from .utils import get_bookgen_version, set_bookgen_version
from .shelf_list import BOOKGEN_UL_Shelves
from .versioning import handle_version_upgrade
from .panel import (
    BOOKGEN_PT_ShelfPanel,
    BOOKGEN_PT_MainPanel,
    BOOKGEN_PT_LeaningPanel,
    BOOKGEN_PT_ProportionsPanel,
    BOOKGEN_PT_DetailsPanel,
    BOOKGEN_PT_BookPanel,
    BOOKGEN_PT_StackPanel,
)

from .generic_operators import (
    BOOKGEN_OT_Rebuild,
    BOOKGEN_OT_CreateSettings,
    BOOKGEN_OT_SetSettings,
    BOOKGEN_OT_RemoveSettings,
    BOOKGEN_OT_RemoveGrouping,
    BOOKGEN_OT_UnlinkGrouping,
)
from .shelf_operator import BOOKGEN_OT_SelectShelf

from .stack_operator import BOOKGEN_OT_SelectStack

from .preferences import BOOKGEN_AddonPreferences

bl_info = {
    "name": "BookGen",
    "description": "Generate books to fill shelves",
    "author": "Oliver Weissbarth, Seojin Sim",
    "version": (1, 0, 5),
    "blender": (3, 30, 0),
    "location": "View3D > Toolshelf > BookGen",
    "tracker_url": "https://github.com/oweissbarth/bookGen/issues",
    "support": "COMMUNITY",
    "wiki_url": "",
    "category": "Add Mesh",
}


classes = [
    BookGenProperties,
    BookGenGroupingProperties,
    BookGenAddonProperties,
    BOOKGEN_OT_Rebuild,
    BOOKGEN_OT_RemoveGrouping,
    BOOKGEN_OT_UnlinkGrouping,
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
    BOOKGEN_PT_StackPanel,
]


def register():
    """
    Register all custom operators, panels, ui-lists and properties.
    """
    from bpy.utils import register_class, previews
    import bpy
    import os

    bookgen_icons = previews.new()
    bpy.types.Scene.bookgen_icons = bookgen_icons
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    bookgen_icons.load("shelf", os.path.join(icons_dir, "shelf.png"), "IMAGE")
    bookgen_icons.load("stack", os.path.join(icons_dir, "stack.png"), "IMAGE")
    bookgen_icons.load("rebuild", os.path.join(icons_dir, "rebuild.png"), "IMAGE")

    for cls in classes:
        register_class(cls)

    bpy.types.Collection.BookGenGroupingProperties = bpy.props.PointerProperty(type=BookGenGroupingProperties)
    bpy.types.Scene.BookGenSettings = bpy.props.CollectionProperty(type=BookGenProperties)
    bpy.types.Scene.BookGenAddonProperties = bpy.props.PointerProperty(type=BookGenAddonProperties)

    bpy.app.handlers.load_post.append(bookgen_startup)
    bpy.app.handlers.save_pre.append(bookgen_mark_version)

    set_bookgen_version(bl_info["version"])


def unregister():
    """
    Unregister all custom operators, panels, ui-lists and properties.

    """
    import bpy
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    bpy.app.handlers.load_post.remove(bookgen_startup)

    bpy.utils.previews.remove(bpy.context.scene.bookgen_icons)


@persistent
def bookgen_mark_version(_dummy):
    """Stores the version of bookgen in the properties"""
    import bpy

    for s in bpy.data.scenes:
        s.BookGenAddonProperties.version = get_bookgen_version()


@persistent
def bookgen_startup(_dummy):
    """
    Ensure that the outline is disabled on start-up.
    """
    import bpy

    bpy.context.scene.BookGenAddonProperties.outline_active = False

    if not bpy.context.scene.BookGenSettings:
        bpy.context.scene.BookGenSettings.add()

    for s in bpy.data.scenes:
        handle_version_upgrade(s)
