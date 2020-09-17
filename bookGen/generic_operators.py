"""
Contains operators that are not specific to shelves of stacks
"""

import time
import logging

import bpy
from bpy.props import EnumProperty, StringProperty

from .utils import (
    get_shelf_parameters,
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

        for shelf_collection in get_bookgen_collection().children:
            shelf_props = shelf_collection.BookGenShelfProperties

            settings = get_settings_by_name(context, shelf_props.settings_name)
            parameters = get_shelf_parameters(shelf_props.id, settings)

            shelf = Shelf(shelf_collection.name, shelf_props.start,
                          shelf_props.end, shelf_props.normal, parameters)
            shelf.clean()
            shelf.fill()

            shelf.to_collection()

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

    def execute(self, _context):
        """ Rebuild called from a script

        Args:
            _context (bpy.types.Context): the execution context for the operator

        Returns:
            Set[str]: operator return code
        """
        self.run()
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

    def run(self):
        """
        Collect new parameters, remove existing books,
        generate new books based on the parameters and add them to the  scene.
        """
        setting = bpy.context.scene.BookGenSettings.add()
        setting.name = self.name

        active_grouping = get_active_grouping()
        if active_grouping:
            active_grouping.BookGenShelfProperties.settings_name = self.name


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

    def execute(self, _context):
        """  Assign settings called from a script

        Args:
            _context (bpy.types.Context): the execution context for the operator

        Returns:
            Set[str]: operator return code
        """
        active_grouping = get_active_grouping()
        active_grouping.BookGenShelfProperties.settings_name = self.enum
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
        return context.mode == 'OBJECT'


class BOOKGEN_OT_RemoveSettings(bpy.types.Operator):
    """Remove bookGen settings and apply to all groupings"""
    bl_idname = "bookgen.remove_settings"
    bl_label = "BookGen"
    bl_options = {'INTERNAL', 'UNDO'}

    context = None

    def invoke(self, context, event):
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
        print(settings_name, settings_id)
        if settings_id == -1:
            return {'CANCELLED'}

        context.scene.BookGenSettings.remove(settings_id)

        for collection in get_bookgen_collection().children:
            if collection.BookGenShelfProperties.settings_name == settings_name:
                collection.BookGenShelfProperties.settings_name = ""

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
        return context.mode == 'OBJECT'
