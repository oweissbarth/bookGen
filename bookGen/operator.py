import bpy
import bpy_extras.view3d_utils
from mathutils import Vector, Matrix
import random
import logging
import time
from math import pi, radians, sin, cos, tan, asin, degrees, sqrt

from .shelf import Shelf
from .utils import visible_objects_and_duplis, obj_ray_cast


class OBJECT_OT_BookGen(bpy.types.Operator):
    bl_idname = "object.book_gen"
    bl_label = "BookGen"
    bl_options = {'REGISTER'}

    """def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8"""

    

    cur_width = 0

    cur_offset = 0
    log = logging.getLogger("bookGen.operator")

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
            self.log.debug("adding shelf")
            properties.shelfs = [Shelf("shelf1", properties.start,
                      properties.end, parameters)]

        shelf = properties.shelfs[0]
        shelf.clean()
        shelf.fill()

        self.log.info("Finished populating shelf in %.4f secs" % (time.time() - time_start))


class BookGen_SelectShelf(bpy.types.Operator):
    bl_idname = "object.book_gen_select_shelf"
    bl_label = "Select BookGen Shelf"
    log = logging.getLogger("bookGen.select_shelf")

    def get_click_position(self, x,y):
        view_layer = bpy.context.view_layer
        region = bpy.context.region
        regionData = bpy.context.space_data.region_3d

        view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, regionData, (x,y))
        ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, regionData, (x,y))

        ray_target = ray_origin + view_vector

        best_length_squared = -1.0
        closest_loc = None

        for obj, matrix in visible_objects_and_duplis(bpy.context):
            if obj.type == 'MESH':
                hit = obj_ray_cast(obj, matrix, ray_origin, ray_target)
                if hit is not None:
                    hit_world = matrix @ hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if closest_loc is None or length_squared < best_length_squared:
                        best_length_squared = length_squared
                        closest_loc = hit_world

        self.log.debug("hit: %r" % hit)

        return closest_loc

    def modal(self, context, event):
        if event.type == 'MOUSEMOVED':
            self.log.debug("mouse moved")

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self.start is None:
                self.start = self.get_click_position(event.mouse_region_x, event.mouse_region_y)
                return { 'RUNNING_MODAL' }
            else:
                self.end = self.get_click_position(event.mouse_region_x, event.mouse_region_y)
                properties = bpy.context.collection.BookGenProperties
                properties.start = self.start
                properties.end = self.end
                return { 'FINISHED' }
        elif event.type in { 'RIGHTMOUSE', 'ESC' }:
            return { 'CANCELED' }
        return { 'RUNNING_MODAL' }

    def invoke(self, context, event):

        self.start = None
        self.end = None

        context.window_manager.modal_handler_add(self)
        return { 'RUNNING_MODAL' }
