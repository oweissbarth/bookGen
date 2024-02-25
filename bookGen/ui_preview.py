"""
Contains the class for drawing a preview of a book grouping
"""

import logging

import bpy
import gpu
from gpu.types import GPUShaderCreateInfo, GPUStageInterfaceInfo
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .utils import bookGen_directory


class BookGenShelfPreview:
    """Draws a preview of a group of books"""

    log = logging.getLogger("bookGen.preview")

    def __init__(self):
        with open(bookGen_directory + "/shaders/simple_flat.vert") as file:
            vertex_shader_source = file.read()

        with open(bookGen_directory + "/shaders/simple_flat.frag") as file:
            fragment_shader_source = file.read()

        shader_interface = GPUStageInterfaceInfo("preview_interface")
        shader_interface.smooth("VEC3", "vNormal")
        shader_interface.smooth("VEC3", "vLighting")
        shader_info = GPUShaderCreateInfo()
        shader_info.vertex_in(0, "VEC3", "pos")
        shader_info.vertex_in(1, "VEC3", "nrm")
        shader_info.vertex_out(shader_interface)
        shader_info.fragment_out(0, "VEC4", "fragColor")
        shader_info.push_constant("MAT4", "modelviewprojection_mat")
        shader_info.push_constant("MAT4", "normal_mat")
        shader_info.push_constant("VEC3", "color")
        shader_info.vertex_source(vertex_shader_source)
        shader_info.fragment_source(fragment_shader_source)

        self.shader = gpu.shader.create_from_info(shader_info)
        del shader_info
        del shader_interface

        self.batch = None

        self.draw_handler = None
        self.color = [0.8, 0.8, 0.8]

    def draw(self, context):
        """Draws the preview based on the current configuration

        Args:
            _op ([type]): [description]
            context ([type]): [description]
        """

        if self.batch is None:
            return

        view_projection_matrix = context.region_data.perspective_matrix
        normal_matrix = context.region_data.view_matrix.inverted().transposed()

        self.shader.bind()
        gpu.state.depth_test_set("LESS")
        self.shader.uniform_float("color", self.color)
        self.shader.uniform_float("modelviewprojection_mat", view_projection_matrix)
        self.shader.uniform_float("normal_mat", normal_matrix)
        self.batch.draw(self.shader)
        gpu.state.depth_test_set("NONE")

    def update(self, verts, faces, context):
        """Updates the vertices and faces of the preview

        Args:
            verts (List[Vector]): vertices of the mesh to preview in world-space
            faces (List[Vector]): faces indices of the mesh to preview
            context (bpy.types.Context): the blender context in which the preview is drawn
        """

        normals = []
        vertices = []
        for f in faces:
            vertices += [verts[f[0]], verts[f[1]], verts[f[2]], verts[f[0]], verts[f[2]], verts[f[3]]]
            a = Vector(verts[f[1]]) - Vector(verts[f[0]])
            b = Vector(verts[f[2]]) - Vector(verts[f[0]])
            nrm = (a.cross(b)).normalized()
            normals += [nrm] * 6

        self.batch = batch_for_shader(self.shader, "TRIS", {"pos": vertices, "nrm": normals})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (context,), "WINDOW", "POST_VIEW")

    def remove(self):
        """
        Remove the preview by removing the draw handler
        """
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            self.draw_handler = None
