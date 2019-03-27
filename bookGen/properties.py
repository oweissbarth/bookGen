import bpy
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty

from .utils import get_bookgen_collection

from math import pi, radians
import logging

class BookGenProperties(bpy.types.PropertyGroup):
    log = logging.getLogger("bookGen.properties")
    
    def update(self, context):
        properties = bpy.context.collection.BookGenProperties
        self.log.debug("auto rebuild: %r" % properties.auto_rebuild)
        if properties.auto_rebuild:
            """col = get_bookgen_collection()
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)"""
            bpy.ops.object.book_gen()

    # general
    auto_rebuild: BoolProperty(name="auto rebuild", default=True)

    #shelf
    width: FloatProperty(name="width", default=1, min=0, update=update)
    scale: FloatProperty(name="scale", default=1, min=0, update=update)
    seed: IntProperty(name="seed", default=0, update=update)

    axis: EnumProperty(name="axis",
                                  items=(("0", "x", "distribute along the x-axis"),
                                         ("1", "y", "distribute along the y-axis"),
                                         ("2", "custom", "distribute along a custom axis")), update=update)

    angle: FloatProperty(name="angle", unit='ROTATION', update=update)

    alignment:  EnumProperty(name="alignment", items=(("0", "spline", "align books at the spline (usually front in a shelf)"), (
        "1", "fore egde", "align books along there fore edge (usually back in a shelf)"), ("2", "center", "align along center")), update=update)

    lean_amount:  FloatProperty(
        name="lean amount", subtype="FACTOR", min=.0, soft_max=1.0, update=update)

    lean_direction: FloatProperty(
        name="lean direction", subtype="FACTOR", min=-1, max=1, default=0, update=update)

    lean_angle: FloatProperty(
        name="lean angle", unit='ROTATION', min=.0, max=pi / 2.0, default=radians(30), update=update)
    rndm_lean_angle_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    book_height: FloatProperty(
        name="height", default=3.0, min=.0, unit="LENGTH", update=update)
    rndm_book_height_factor: FloatProperty(
        name=" random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    book_width: FloatProperty(
        name="width", default=0.5, min=.01, unit="LENGTH", update=update)
    rndm_book_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    book_depth: FloatProperty(
        name="depth", default=3.0, min=.0, unit="LENGTH", update=update)
    rndm_book_depth_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    cover_thickness: FloatProperty(
        name="cover thickness", default=0.05, min=.0, step=.02, unit="LENGTH", update=update) # TODO hinge_inset_guard
    rndm_cover_thickness_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    textblock_offset: FloatProperty(
        name="textblock offset", default=0.1, min=.0, unit="LENGTH", update=update)
    rndm_textblock_offset_factor: FloatProperty(
        name="randon", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    spline_curl: FloatProperty(
        name="spline curl", default=0.01, step=.02, min=.0, unit="LENGTH", update=update)
    rndm_spline_curl_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    hinge_inset: FloatProperty(
        name="hinge inset", default=0.03, min=.0, step=.01, unit="LENGTH", update=update) #TODO hinge inset guard
    rndm_hinge_inset_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    hinge_width: FloatProperty(
        name="hinge width", default=0.08, min=.0, step=.05, unit="LENGTH", update=update)
    rndm_hinge_width_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    spacing: FloatProperty(
        name="spacing", default=0.05, min=.0, unit="LENGTH", update=update)
    rndm_spacing_factor: FloatProperty(
        name="random", default=1, min=.0, soft_max=1, subtype="FACTOR", update=update)

    subsurf: BoolProperty(
        name="Add Subsurf-Modifier", default=False, update=update)
    smooth: BoolProperty(name="shade smooth", default=False, update=update)
    unwrap: BoolProperty(name="unwrap", default=True, update=update)