"""
Contains the preferences of bookGen that allow adjust the overall behavior
"""
from bpy.types import AddonPreferences
from bpy.props import BoolProperty


class BOOKGEN_AddonPreferences(AddonPreferences):
    """
    The add-on preferences allow to adjust the overall behavior of bookGen
    """
    bl_idname = __package__

    lazy_update: BoolProperty(
        name="Use lazy update",
        default=False,
        description="Shows a fast preview when changes settings. CAN BE UNSTABLE WITH THE NEW UNDO SYSTEM"
    )

    def draw(self, _context):
        """Draws the add-on preferences

        Args:
            _context (bpy.types.Context): the execution context
        """
        layout = self.layout
        layout.label(text="ATTENTION: THIS CAN BE UNSTABLE WITH THE NEW UNDO SYSTEM. USE WITH CAUTION!")
        layout.prop(self, "lazy_update")
