"""
This file contains the stack class. It allows to generate books in a stacks
"""

# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================

import random
import logging
from math import radians

import bpy
from mathutils import Vector, Matrix

from .book import Book

from .utils import get_shelf_collection, get_bookgen_collection


class Stack:
    """
    Describes a stack of books.
    """
    log = logging.getLogger("bookGen.Shelf")
    origin = Vector((0, 0, 0))
    forward = Vector((1, 0, 0))
    height = 3.0
    up = Vector((0, 0, 1))
    parameters = {}
    books = []

    def __init__(self, name, origin, forward, up, height, parameters):
        self.name = name
        self.origin = Vector(origin)
        self.forward = Vector(forward)
        self.up = Vector(up)
        self.height = height

        self.rotation_matrix = Matrix([self.forward, -self.forward.cross(self.up), self.up]).transposed()
        self.parameters = parameters
        self.collection = None
        self.books = []

        self.align_offset = 0
        self.cur_height = 0
        self.cur_offset = 0

    def add_book(self, book, first):
        """ Adds a single book to a stack

        Args:
            book (Book): the book that is added
            first (bool): True if it is the first book of the stack. Otherwise false.
        """

        self.books.append(book)

        if first:
            self.align_offset = book.depth / 2

        # book alignment
        #offset_dir = -1 if self.parameters["alignment"] == "1" else 1

        # if(not first and not self.parameters["alignment"] == "2"):
            # location alignment
        #    book.location += Vector((0, offset_dir * (book.depth / 2 - self.align_offset), 0))

        # distribution

        rotation = random.random() * self.parameters["rotation"] * 180

        book.location += Vector((0, 0, self.cur_offset))
        book.location = self.rotation_matrix @ book.location
        book.rotation = Matrix.Rotation(
            radians(rotation), 3, 'Z') @ self.rotation_matrix @ Matrix.Rotation(radians(90), 3, 'Y')

        book.location += self.origin

    def to_collection(self, context):
        """
        Converts the stack to a blender collection and adds the books as blender objects
        """
        self.collection = get_shelf_collection(context, self.name)
        for book in self.books:
            obj = book.to_object()
            self.collection.objects.link(obj)

    def fill(self):
        """
        Fills the stack with books
        """
        self.cur_height = 0
        self.cur_offset = 0

        random.seed(self.parameters["seed"])

        first = True

        params = self.apply_parameters()
        current = Book(**params,
                       subsurf=self.parameters["subsurf"],
                       cover_material=self.parameters["cover_material"],
                       page_material=self.parameters["page_material"])
        self.cur_offset += current.width / 2
        self.add_book(current, first)

        while self.cur_height < self.height:
            self.log.debug("remaining height to be filled: %.3f", (self.height - self.cur_height))
            params = self.apply_parameters()
            last = current
            current = Book(**params,
                           subsurf=self.parameters["subsurf"],
                           cover_material=self.parameters["cover_material"],
                           page_material=self.parameters["page_material"])

            self.cur_height = self.cur_offset + current.width

            self.cur_offset += current.width / 2 + last.width / 2

            if self.cur_height < self.height:
                self.add_book(current, first)

            first = False

    def clean(self, context):
        """
        Removes all object from the stack and removes meshes from the scene
        """
        collection = None
        if self.collection is not None:
            collection = self.collection
        else:
            bookgen = get_bookgen_collection(context)
            for child in bookgen.children:
                if child.name == self.name:
                    collection = child
        if collection is None:
            return
        for obj in collection.objects:
            collection.objects.unlink(obj)
            bpy.data.meshes.remove(obj.data)

    def get_geometry(self):
        """ Returns the raw geometry of the stack for previz

        Returns:
            (List[Vector], List[Vector]): a tuple containing a list of vertices and a list of indices
        """
        index_offset = 0
        verts = []
        faces = []

        for book in self.books:
            b_verts, b_faces = book.get_geometry()
            verts += b_verts
            offset_faces = map(
                lambda f: [
                    f[0] + index_offset,
                    f[1] + index_offset,
                    f[2] + index_offset,
                    f[3] + index_offset],
                b_faces)
            faces += offset_faces
            index_offset = len(verts)

        return verts, faces

    def apply_parameters(self):
        """Return book parameters with all randomization applied"""

        p = self.parameters

        rndm_book_height = (random.random() * 0.4 - 0.2) * p["rndm_book_height_factor"]
        rndm_book_width = (random.random() * 0.4 - 0.2) * p["rndm_book_width_factor"]
        rndm_book_depth = (random.random() * 0.4 - 0.2) * p["rndm_book_depth_factor"]

        rndm_textblock_offset = (random.random() * 0.4 - 0.2) * p["rndm_textblock_offset_factor"]

        rndm_cover_thickness = (random.random() * 0.4 - 0.2) * p["rndm_cover_thickness_factor"]

        rndm_spine_curl = (random.random() * 0.4 - 0.2) * p["rndm_spine_curl_factor"]

        rndm_hinge_inset = (random.random() * 0.4 - 0.2) * p["rndm_hinge_inset_factor"]
        rndm_hinge_width = (random.random() * 0.4 - 0.2) * p["rndm_hinge_width_factor"]

        book_height = p["scale"] * p["book_height"] * (1 + rndm_book_height)
        book_width = p["scale"] * p["book_width"] * (1 + rndm_book_width)
        book_depth = p["scale"] * p["book_depth"] * (1 + rndm_book_depth)

        cover_thickness = p["scale"] * p["cover_thickness"] * (1 + rndm_cover_thickness)

        textblock_height = book_height - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_depth = book_depth - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_thickness = book_width - 2 * cover_thickness

        spine_curl = p["scale"] * p["spine_curl"] * (1 + rndm_spine_curl)

        hinge_inset = p["scale"] * p["hinge_inset"] * (1 + rndm_hinge_inset)
        hinge_width = p["scale"] * p["hinge_width"] * (1 + rndm_hinge_width)

        return {"cover_height": book_height,
                "cover_thickness": cover_thickness,
                "cover_depth": book_depth,
                "page_height": textblock_height,
                "page_depth": textblock_depth,
                "page_thickness": textblock_thickness,
                "spine_curl": spine_curl,
                "hinge_inset": hinge_inset,
                "hinge_width": hinge_width
                }
