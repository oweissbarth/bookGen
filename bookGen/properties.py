"""
This file contains the property definitions used to describe the book and shelf layouts.
"""

from math import pi, radians
import logging
import time
import functools

import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    IntVectorProperty,
    EnumProperty,
    BoolProperty,
    FloatVectorProperty,
    PointerProperty,
    StringProperty)

from .utils import (
    get_bookgen_collection,
    get_shelf_collection_by_index,
    get_shelf_parameters,
    get_settings_by_name,
    get_stack_parameters)
from .shelf import Shelf
from .stack import Stack
from .ui_outline import BookGenShelfOutline
from .ui_preview import BookGenShelfPreview

partial = None


def remove_previews(previews):
    """
    Remove previews and rebuild all books.
    """
    for preview in previews:
        preview.remove()

    bpy.ops.bookgen.rebuild()
    bpy.ops.ed.undo_push()
    return None


class BookGenAddonProperties(bpy.types.PropertyGroup):
    """
    This store the current state of the bookGen add-on.
    """
    #outline = None
    outline = BookGenShelfOutline()

    def update_outline_active(self, context):
        """
        If the outline was activated, generate the shelf and draw the outline.
        Otherwise disable the outline.
        """
        properties = context.scene.BookGenAddonProperties
        if properties.outline_active and properties.active_shelf != -1:
            grouping_collection = get_shelf_collection_by_index(context, properties.active_shelf)
            if not grouping_collection:
                return
            grouping_props = grouping_collection.BookGenGroupingProperties
            settings = get_settings_by_name(context, grouping_props.settings_name)
            if grouping_props.grouping_type == 'SHELF':
                parameters = get_shelf_parameters(context, grouping_props.id, settings)
                shelf = Shelf(
                    grouping_collection.name,
                    grouping_props.start,
                    grouping_props.end,
                    grouping_props.normal,
                    parameters)
                shelf.fill()
                self.outline.enable_outline(*shelf.get_geometry(), context)
            else:
                parameters = get_stack_parameters(context, grouping_props.id, settings)
                shelf = Stack(
                    grouping_collection.name,
                    grouping_props.origin,
                    grouping_props.forward,
                    grouping_props.normal,
                    grouping_props.height,
                    parameters)
                shelf.fill()
                self.outline.enable_outline(*shelf.get_geometry(), context)
        else:
            self.outline.disable_outline()

    auto_rebuild: BoolProperty(
        name="auto rebuild",
        description="Automatically rebuild all books if settings are changed",
        default=True,
        options=set())
    active_shelf: IntProperty(name="Active grouping", update=update_outline_active, options=set())
    outline_active: BoolProperty(
        name="Highlight active",
        description="Draws an overlay to highlight the active grouping",
        default=False,
        update=update_outline_active,
        options=set())
    collection: PointerProperty(type=bpy.types.Collection, name="collection", description="master collection containing all groupings")
    version: IntVectorProperty(name="version", description="the version of the bookgen add-on", default=(-1, -1, -1))

class BookGenProperties(bpy.types.PropertyGroup):
    """
    This contains the settings of a shelf including book-shape, alignment and leaning.
    """
    log = logging.getLogger("bookGen.properties")
    previews = {}
    f = None

    def update(self, context):
        """ Use immediate or lazy update based on add-on preferences

        Args:
            context (bpy.types.Context): the execution context
        """
        preferences = context.preferences.addons["bookGen"].preferences
        if "lazy_update" in preferences.keys() and preferences["lazy_update"]:
            self.update_delayed(context)
        else:
            self.update_immediate(context)

    def update_immediate(self, context):
        """
        Updates the scene using the settings in this property group.
        """
        time_start = time.time()
        properties = context.scene.BookGenAddonProperties

        if properties.auto_rebuild:
            bpy.ops.bookgen.rebuild()
            # bpy.ops.ed.undo_push()

        self.log.info("Finished populating shelf in %.4f secs", (time.time() - time_start))

    def update_delayed(self, context):
        """
        Generates a preview of the current shelve configuration and draw it.
        Sets up a timer to update the scene after a delay of 1 second
        """

        global partial
        time_start = time.time()
        properties = context.scene.BookGenAddonProperties

        if not properties.auto_rebuild:
            return

        for grouping_collection in get_bookgen_collection(context).children:

            grouping_props = grouping_collection.BookGenGroupingProperties
            settings = get_settings_by_name(context, grouping_props.settings_name)
            if not settings:
                continue

            bpy.ops.bookgen.rebuild(clear=True)

            if grouping_props.grouping_type == 'SHELF':
                parameters = get_shelf_parameters(context, grouping_props.id, settings)

                grouping = Shelf(grouping_collection.name, grouping_props.start,
                                 grouping_props.end, grouping_props.normal, parameters)
                # grouping.clean(context)
                grouping.fill()

            else:
                parameters = get_stack_parameters(context, grouping_props.id, settings)
                grouping = Stack(grouping_collection.name, grouping_props.origin,
                                 grouping_props.forward, grouping_props.normal, grouping_props.height, parameters)
                # grouping.clean(context)
                grouping.fill()

            if grouping_props.id not in self.previews.keys():
                preview = BookGenShelfPreview()
                self.previews.update({grouping_props.id: preview})
            else:
                preview = self.previews[grouping_props.id]

            preview.update(*grouping.get_geometry(), context)

        self.log.info("Finished populating shelf in %.4f secs", (time.time() - time_start))

        if partial is not None and bpy.app.timers.is_registered(partial):
            bpy.app.timers.unregister(partial)

        partial = functools.partial(remove_previews, self.previews.values())
        bpy.app.timers.register(partial, first_interval=1.0)

    def get_name(self):
        return self.get("name", "BookGenSettings")

    def set_name(self, name):
        old_name = self.name
        self["name"] = name
        if name != old_name:
            for collection in get_bookgen_collection(
                    bpy.context).children:  # TODO we should not use the global context here
                if collection.BookGenGroupingProperties.settings_name == old_name:
                    collection.BookGenGroupingProperties.settings_name = name

    # general
    name: StringProperty(name="name", default="BookGenSettings", set=set_name, get=get_name, options=set())

    # shelf
    scale: FloatProperty(name="scale", min=0.1, default=1, update=update, options=set())

    seed: IntProperty(name="seed", default=0, update=update, options=set())

    alignment: EnumProperty(
        name="alignment",
        items=(
            ("0",
             "fore edge",
             "align books at the fore edge"),
            ("1",
             "spine",
             "align books at the spine"),
            ("2",
             "center",
             "align at center")),
        update=update_immediate, options=set())

    lean_amount: FloatProperty(
        name="lean amount", subtype="FACTOR", min=.0, soft_max=1.0, update=update, options=set())

    lean_direction: FloatProperty(
        name="lean direction", subtype="FACTOR", min=-1, max=1, default=0, update=update, options=set())

    lean_angle: FloatProperty(
        name="lean angle",
        unit='ROTATION',
        min=.0,
        soft_max=radians(30),
        max=pi / 2.0,
        default=radians(8),
        update=update,
        options=set())
    rndm_lean_angle_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    # stack
    rotation: FloatProperty(name="rotation", subtype='FACTOR', min=.0, max=1.0, update=update, options=set())

    # books

    book_height: FloatProperty(
        name="height", default=0.15, min=.05, step=0.005, unit="LENGTH", update=update, options=set())
    rndm_book_height_factor: FloatProperty(
        name=" random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    book_width: FloatProperty(
        name="width", default=0.03, min=.002, step=0.001, unit="LENGTH", update=update, options=set())
    rndm_book_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    book_depth: FloatProperty(
        name="depth", default=0.12, min=.0, step=0.005, unit="LENGTH", update=update, options=set())
    rndm_book_depth_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    cover_thickness: FloatProperty(
        name="cover thickness",
        default=0.002,
        min=.0,
        step=.02,
        unit="LENGTH",
        update=update, options=set())
    rndm_cover_thickness_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    textblock_offset: FloatProperty(
        name="textblock offset", default=0.005, min=.0, step=.001, unit="LENGTH", update=update, options=set())
    rndm_textblock_offset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    spine_curl: FloatProperty(
        name="spine curl", default=0.002, step=.002, min=.0, unit="LENGTH", update=update, options=set())
    rndm_spine_curl_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    hinge_inset: FloatProperty(name="hinge inset", default=0.001, min=.0, step=.0001,
                               unit="LENGTH", update=update, options=set())
    rndm_hinge_inset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    hinge_width: FloatProperty(
        name="hinge width", default=0.004, min=.0, step=.05, unit="LENGTH", update=update, options=set())
    rndm_hinge_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update, options=set())

    subsurf: BoolProperty(
        name="Add Subsurf-Modifier", default=False, update=update_immediate, options=set())

    cover_material: PointerProperty(
        name="Cover Material",
        type=bpy.types.Material,
        update=update_immediate,
        options=set())

    page_material: PointerProperty(
        name="Page Material",
        type=bpy.types.Material,
        update=update_immediate,
        options=set())


class BookGenGroupingProperties(bpy.types.PropertyGroup):
    """
    This describes how a grouping of books
    what type of grouping it is
    is positioned in 3d space,
    what settings it uses
    """

    """
    This describes how a shelf is positioned in 3D space.
    """
    start: FloatVectorProperty(name="start")
    end: FloatVectorProperty(name="end")
    normal: FloatVectorProperty(name="normal")

    """
    This describes how a stack is positioned in 3D space.
    """
    origin: FloatVectorProperty(name="origin")
    forward: FloatVectorProperty(name="forward")
    normal: FloatVectorProperty(name="normal")
    height: FloatProperty(name="height")

    grouping_type: EnumProperty(
        items=(
            ("SHELF",
             "shelf",
             ""),
            ("STACK",
             "stack",
             "")),
        name="grouping_type",
        description="Test",
        default="SHELF")
    id: IntProperty(name="id")
    settings_name: StringProperty("Settings name")
