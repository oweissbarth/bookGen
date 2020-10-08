"""
Contains operators that are not specific to shelves of stacks
"""

import time
import logging

import bpy
from bpy.props import EnumProperty, StringProperty
from mathutils import Vector

from .utils import (
    get_shelf_parameters,
    get_stack_parameters,
    get_bookgen_collection,
    get_active_grouping,
    get_active_settings,
    get_settings_by_name)
from .shelf import Shelf
from .stack import Stack


class BOOKGEN_OT_Rebuild(bpy.types.Operator):
    """Regenerate all books"""
    bl_idname = "bookgen.rebuild"
    bl_label = "BookGen"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    """def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8"""

    log = logging.getLogger("bookGen.operator")

    def invoke(self, context, _event):
        """ Rebuild called from the UI

        Args:
            _context (bpy.types.Context): the execution context for the operator
            _event (bpy.type.Event): the invocation event

        Returns:
            Set[str]: operator return code
        """
        self.run(context)
        return {'FINISHED'}

    def execute(self, context):
        """ Rebuild called from a script

        Args:
            _context (bpy.types.Context): the execution context for the operator

        Returns:
            Set[str]: operator return code
        """
        self.run(context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """ Check if we are in object mode before calling the operator

        Args:
            context (bpy.types.Context): the execution context for the operator

        Returns:
            bool: True if the operator can be executed, otherwise false.
        """
        return context.mode == 'OBJECT'

    def run(self, context):
        """
        Collect new parameters, remove existing books,
        generate new books based on the parameters and add them to the  scene.
        """
        time_start = time.time()

        for grouping_collection in get_bookgen_collection(context).children:
            grouping_props = grouping_collection.BookGenGroupingProperties
            settings = get_settings_by_name(context, grouping_props.settings_name)
            if not settings:
                continue

            if grouping_props.grouping_type == 'SHELF':
                parameters = get_shelf_parameters(context, grouping_props.id, settings)

                shelf = Shelf(grouping_collection.name, grouping_props.start,
                              grouping_props.end, grouping_props.normal, parameters)
                shelf.clean(context)
                shelf.fill()

                shelf.to_collection(context, with_uvs=True)
            else:
                parameters = get_stack_parameters(context, grouping_props.id, settings)
                stack = Stack(grouping_collection.name, grouping_props.origin,
                              grouping_props.forward, grouping_props.normal, grouping_props.height, parameters)
                stack.clean(context)
                stack.fill()

                stack.to_collection(context)

        self.log.info("Finished populating shelf in %.4f secs", (time.time() - time_start))


class BOOKGEN_OT_CreateSettings(bpy.types.Operator):
    """Regenerate all books"""
    bl_idname = "bookgen.create_settings"
    bl_label = "Create new BookGen Settings"
    bl_options = {'INTERNAL'}

    name: StringProperty(name="name")

    def invoke(self, context, _event):
        """ Rebuild called from the UI

        Args:
            _context (bpy.types.Context): the execution context for the operator
            _event (bpy.type.Event): the invocation event

        Returns:
            Set[str]: operator return code
        """
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        return {'FINISHED'}

    def execute(self, context):
        """ Rebuild called from a script

        Args:
            _context (bpy.types.Context): the execution context for the operator

        Returns:
            Set[str]: operator return code
        """
        self.run(context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """ Check if we are in object mode before calling the operator

        Args:
            context (bpy.types.Context): the execution context for the operator

        Returns:
            bool: True if the operator can be executed, otherwise false.
        """
        return context.mode == 'OBJECT'

    def run(self, context):
        """
        Collect new parameters, remove existing books,
        generate new books based on the parameters and add them to the  scene.
        """
        setting = context.scene.BookGenSettings.add()
        setting.name = self.name

        active_grouping = get_active_grouping(context)
        if active_grouping:
            active_grouping.BookGenGroupingProperties.settings_name = self.name
        context.area.tag_redraw()


class BOOKGEN_OT_SetSettings(bpy.types.Operator):
    """Assign bookGen settings to grouping"""
    bl_idname = "bookgen.set_settings"
    bl_label = "BookGen"
    bl_options = {'INTERNAL', 'UNDO'}
    bl_property = "enum"

    context = None

    def get_settings_names(self, context):
        settings_names = []
        for index, settings in enumerate(context.scene.BookGenSettings):
            settings_names.append((settings.name, settings.name, "", "PRESET", index))

        return settings_names

    enum: EnumProperty(items=get_settings_names, name="Items")

    def invoke(self, context, _event):
        """ Assign settings called from the UI

        Args:
            _context (bpy.types.Context): the execution context for the operator
            _event (bpy.type.Event): the invocation event

        Returns:
            Set[str]: operator return code
        """
        self.context = context
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        """  Assign settings called from a script

        Args:
            _context (bpy.types.Context): the execution context for the operator

        Returns:
            Set[str]: operator return code
        """
        active_grouping = get_active_grouping(context)
        active_grouping.BookGenGroupingProperties.settings_name = self.enum
        bpy.ops.bookgen.rebuild()

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """ Check if we are in object mode before calling the operator

        Args:
            context (bpy.types.Context): the execution context for the operator

        Returns:
            bool: True if the operator can be executed, otherwise false.
        """
        active_grouping = get_active_grouping(context)
        return active_grouping and context.mode == 'OBJECT'


class BOOKGEN_OT_RemoveSettings(bpy.types.Operator):
    """Remove bookGen settings and apply to all groupings"""
    bl_idname = "bookgen.remove_settings"
    bl_label = "BookGen"
    bl_options = {'INTERNAL', 'UNDO'}

    context = None

    def invoke(self, context, _event):
        """ Remove settings called from the UI

        Args:
            _context (bpy.types.Context): the execution context for the operator
            _event (bpy.type.Event): the invocation event

        Returns:
            Set[str]: operator return code
        """
        active_settings = get_active_settings(context)
        settings_name = active_settings.name
        settings_id = context.scene.BookGenSettings.find(settings_name)
        if settings_id == -1:
            return {'CANCELLED'}

        context.scene.BookGenSettings.remove(settings_id)

        for collection in get_bookgen_collection(context).children:
            if collection.BookGenGroupingProperties.settings_name == settings_name:
                collection.BookGenGroupingProperties.settings_name = ""

        # bpy.ops.bookgen.rebuild()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """ Check if we are in object mode before calling the operator

        Args:
            context (bpy.types.Context): the execution context for the operator

        Returns:
            bool: True if the operator can be executed, otherwise false.
        """
        settings_exist = bool(context.scene.BookGenSettings)
        active_settings = get_active_settings(context)

        return settings_exist and active_settings and context.mode == 'OBJECT'
