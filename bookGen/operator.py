import bpy
import bpy_extras.view3d_utils
from mathutils import Vector, Matrix
import random
import logging
import time
from math import pi, radians, sin, cos, tan, asin, degrees, sqrt

from .shelf import Shelf
from .utils import visible_objects_and_duplis, obj_ray_cast, get_bookgen_collection, get_shelf_parameters, get_shelf_collection


class OBJECT_OT_BookGenRebuild(bpy.types.Operator):
    bl_idname = "object.book_gen_rebuild"
    bl_label = "BookGen"
    bl_options = {'REGISTER'}

    """def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8"""

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

        time_start = time.time()


        parameters = get_shelf_parameters()

        properties = bpy.context.collection.BookGenProperties

        for shelf_collection in get_bookgen_collection().children:
            shelf_props = shelf_collection.BookGenShelfProperties

            parameters["seed"] += shelf_props.id

            shelf = Shelf(shelf_collection.name, shelf_props.start, shelf_props.end, shelf_props.normal, parameters)
            shelf.clean()
            shelf.fill()

            parameters["seed"] -= shelf_props.id

        self.log.info("Finished populating shelf in %.4f secs" % (time.time() - time_start))


class BookGen_SelectShelf(bpy.types.Operator):
    bl_idname = "object.book_gen_select_shelf"
    bl_label = "Select BookGen Shelf"
    log = logging.getLogger("bookGen.select_shelf")

    def get_click_position(self, x,y):
        region = bpy.context.region
        regionData = bpy.context.space_data.region_3d

        view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, regionData, (x,y))
        ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, regionData, (x,y))

        ray_target = ray_origin + view_vector

        best_length_squared = -1.0
        closest_loc = None
        closest_normal = None

        for obj, matrix in visible_objects_and_duplis(bpy.context):
            if obj.type == 'MESH':
                hit, normal = obj_ray_cast(obj, matrix, ray_origin, ray_target)
                if hit is not None:
                    hit_world = matrix @ hit
                    normal_world = matrix @ normal
                    length_squared = (hit_world - ray_origin).length_squared
                    if closest_loc is None or length_squared < best_length_squared:
                        best_length_squared = length_squared
                        closest_loc = hit_world
                        closest_normal = normal

        self.log.debug("hit: %r" % hit)

        return closest_loc, closest_normal

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self.start is None:
                self.start, self.start_normal = self.get_click_position(event.mouse_region_x, event.mouse_region_y)
                return { 'RUNNING_MODAL' }
            else:
                self.end, self.end_normal = self.get_click_position(event.mouse_region_x, event.mouse_region_y)
                shelf_id = len(get_bookgen_collection().children)
                parameters = get_shelf_parameters()
                parameters["seed"] += shelf_id
                shelf = Shelf("shelf_"+str(shelf_id), self.start, self.end, (self.start_normal  + self.end_normal)/2, parameters)
                shelf.clean()
                shelf.fill()
                
                # set properties for later rebuild
                shelf_props = get_shelf_collection(shelf.name).BookGenShelfProperties
                shelf_props.start = self.start
                shelf_props.end = self.end
                shelf_props.normal = (self.start_normal  + self.end_normal)/2
                shelf_props.id = shelf_id
                return { 'FINISHED' }
        elif event.type in { 'RIGHTMOUSE', 'ESC' }:
            return { 'CANCELED' }
        return { 'RUNNING_MODAL' }

    def invoke(self, context, event):

        self.start = None
        self.end = None

        context.window_manager.modal_handler_add(self)
        return { 'RUNNING_MODAL' }
