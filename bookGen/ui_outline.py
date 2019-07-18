import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bgl

from .utils import get_shelf_collection_by_index

class BookGenShelfOutline:
    draw_handler = None
    batch = None

    def __init__(self):
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        col_ref = bpy.context.preferences.themes[0].view_3d.face_select
        self.outline_color = (col_ref[0], col_ref[1], col_ref[2], 0.1)
        self.batch = None 

    def update(self, shelf_id, context):
        verts = []
        col = get_shelf_collection_by_index(shelf_id)
        if col is not None:
            for obj in col.objects:
                for f in obj.data.polygons:
                    # we know that all faces are quads
                    verts.append(obj.matrix_world @ obj.data.vertices[f.vertices[0]].co)
                    verts.append(obj.matrix_world @ obj.data.vertices[f.vertices[1]].co)
                    verts.append(obj.matrix_world @ obj.data.vertices[f.vertices[2]].co)

                    verts.append(obj.matrix_world @ obj.data.vertices[f.vertices[0]].co)
                    verts.append(obj.matrix_world @ obj.data.vertices[f.vertices[2]].co)
                    verts.append(obj.matrix_world @ obj.data.vertices[f.vertices[3]].co)

        self.batch = batch_for_shader(self.shader, "TRIS", {"pos": verts})

    def enable_outline(self, shelf_id, context):
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_outline, (self,context), 'WINDOW', 'POST_VIEW')
        self.update(shelf_id, context)

    def disable_outline(self):
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')


    def draw_outline(self, op, context):
        if self.batch is None:
            return
        self.shader.bind()
        bgl.glEnable(bgl.GL_BLEND)
        self.shader.uniform_float("color", self.outline_color)
        self.batch.draw(self.shader)
        bgl.glDisable(bgl.GL_BLEND)
