import bpy
from mathutils import Vector, Matrix
import random
import time
from math import pi, radians, sin, cos, tan, asin, degrees

from .shelf import Shelf


class OBJECT_OT_BookGen(bpy.types.Operator):
    bl_idname = "object.book_gen"
    bl_label = "BookGen"
    bl_options = {'REGISTER'}

    """def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8"""

    

    cur_width = 0

    cur_offset = 0

    def check(self, context):
        self.run()

    def invoke(self, context, event):
        self.run()
        return {'FINISHED'}

    def execute(self, context):
        self.run()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def run(self):
        properties = bpy.context.collection.BookGenProperties

        time_start = time.time()

        if(properties.axis == "0"):
            angle = radians(0)
        elif(properties.axis == "1"):
            angle = radians(90)
        elif(properties.axis == "2"):
            angle = properties.angle

        parameters = {
            "scale": properties.scale,
            "seed": properties.seed,
            "alignment": properties.alignment,
            "lean_amount": properties.lean_amount,
            "lean_direction": properties.lean_direction,
            "lean_angle": properties.lean_angle,
            "rndm_lean_angle_factor": properties.rndm_lean_angle_factor,
            "book_height": properties.book_height,
            "rndm_book_height_factor": properties.rndm_book_height_factor,
            "book_width": properties.book_width,
            "rndm_book_width_factor": properties.rndm_book_width_factor,
            "book_depth": properties.book_depth,
            "rndm_book_depth_factor": properties.rndm_book_depth_factor,
            "cover_thickness": properties.cover_thickness,
            "rndm_cover_thickness_factor": properties.rndm_cover_thickness_factor,
            "textblock_offset": properties.textblock_offset,
            "rndm_textblock_offset_factor": properties.rndm_textblock_offset_factor,
            "spline_curl": properties.spline_curl,
            "rndm_spline_curl_factor": properties.rndm_spline_curl_factor,
            "hinge_inset": properties.hinge_inset,
            "rndm_hinge_inset_factor": properties.rndm_hinge_inset_factor,
            "hinge_width": properties.hinge_width,
            "rndm_hinge_width_factor": properties.rndm_hinge_width_factor,
            "spacing": properties.spacing,
            "rndm_spacing_factor": properties.rndm_spacing_factor,
            "subsurf": properties.subsurf,
            "smooth": properties.smooth,
            "unwrap": properties.unwrap
        }

        if not hasattr(properties, "shelfs"):
            print("adding shelf")
            properties.shelfs = [Shelf("shelf1",bpy.context.scene.cursor.location,
                      angle, properties.width, parameters)]

        shelf = properties.shelfs[0]
        shelf.clean()
        shelf.fill()

        print("Finished: %.4f sec" % (time.time() - time_start))


class BookGen_SelectShelf(bpy.types.Operator):
    bl_idname = "object.book_gen_select_shelf"
    bl_label = "Select BookGen Shelf"

    def modal(self, context, event):
        if event.type == 'MOUSEMOVED':
            print("mouse moved")

        elif event.type == 'LEFTMOUSE':
            if self.start is None:
                self.start = Vector([0,0,0])
                return { 'RUNNING_MODAL' }
            else:
                self.end = Vector([0,10,0])
                return { 'FINISHED' }
        elif event.type in { 'RIGHTMOUSE', 'ESC' }:
            return { 'CANCELED' }
        return { 'RUNNING_MODAL' }

    def invoke(self, context, event):

        self.start = None
        self.end = None

        context.window_manager.modal_handler_add(self)
        return { 'RUNNING_MODAL' }
