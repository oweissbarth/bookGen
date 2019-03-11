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
import bpy
from mathutils import Vector, Matrix

from math import cos, tan, radians, sin, degrees
import random

from .book import Book

from .utils import get_shelf_collection


class Shelf:
    origin = Vector((0, 0, 0))
    direction = Vector((1, 0, 0))
    width = 3.0
    parameters = {}
    books = []

    def __init__(self, name, origin, direction, width, parameters):
        self.name = name
        self.origin = origin
        self.direction = direction
        self.width = width
        self.parameters = parameters
        self.collection = get_shelf_collection(self.name)

    def add_book(self, book, first):

        

        obj = book.to_object()

        self.collection.objects.link(obj)

        self.books.append(book)

        #book.obj.select_set(True)

        if first:
            self.align_offset = book.depth / 2

        # book alignment
        offset_dir = -1 if self.parameters["alignment"] == "1" else 1
        if(not first and not self.parameters["alignment"] == "2"):
            # location alignment
            book.obj.location += Vector((0, offset_dir * (book.depth / 2 - self.align_offset), 0))

        book.obj.location += Vector((0, 0, book.height / 2))

        # leaning
        if book.lean_angle < 0:
                book.obj.location += Vector((book.width / 2, 0, 0))
        else:
            book.obj.location += Vector((-book.width / 2, 0, 0))
        book.obj.location = Matrix.Rotation(book.lean_angle, 3, 'Y') @ book.obj.location

        book.obj.rotation_euler[1] = book.lean_angle

        # distribution
        book.obj.location += Vector((self.cur_offset, 0, 0))
        book.obj.location = Matrix.Rotation(self.direction, 3, 'Z') @ book.obj.location

        book.obj.rotation_euler[2] = self.direction

        book.obj.location += self.origin

        self.cur_width += sin(book.lean_angle) * book.height + book.width
        print(self.cur_width)

    def fill(self):
        self.cur_width = 0
        self.cur_offset = 0

        random.seed(self.parameters["seed"])

        first = True

        params = self.apply_parameters()
        current = Book(*(list(params.values())), self.parameters["unwrap"], self.parameters["subsurf"], self.parameters["smooth"])
        self.add_book(current, first)

        while(self.cur_width < self.width * self.parameters["scale"]):  # TODO add current book width to cur_width
            print("remaining width to be filled: %.3f"%(self.width - self.cur_width))
            params = self.apply_parameters()
            last = current
            current = Book(*(list(params.values())), self.parameters["unwrap"], self.parameters["subsurf"], self.parameters["smooth"])

            # gathering parameters for the next book

            if last.lean_angle < 0:
                print("case A")
                last.corner_height_left = cos(last.lean_angle)*last.height
                last.corner_height_right =  cos(last.lean_angle) * last.height + sin(last.lean_angle)*last.width
            else:
                print("case B")
                last.corner_height_left =  cos(last.lean_angle) * last.height + sin(last.lean_angle)*last.width
                last.corner_height_right = cos(last.lean_angle)*last.height

            

            if current.lean_angle < 0:
                print("case B")
                current.corner_height_left = cos(current.lean_angle)*current.height
                current.corner_height_right = cos(current.lean_angle) * current.height + sin(current.lean_angle)*current.width

            else:
                print("case A")
                current.corner_height_right = cos(current.lean_angle)*current.height
                current.corner_height_left = cos(current.lean_angle) * current.height + sin(current.lean_angle)*current.width


            print("current - angle: %.3f left: %.3f   right: %.3f"%(degrees(current.lean_angle), current.corner_height_left, current.corner_height_right))


            #old_corner_height = book.height * cos(book.lean_angle)


            #corner_height = cos(params["lean_angle"]) * (params["book_height"] + params["book_width"] / tan(radians(90) - params["lean_angle"]))


            """if(old_corner_height <= corner_height and book.lean_angle >= params["lean_angle"]):
                print("case 1 ")
                self.cur_offset += sin(book.lean_angle) * book.height - cos(book.lean_angle) * book.height / (tan(radians(90) - params["lean_angle"])) + params["book_width"] / cos(params["lean_angle"])
            elif(book.lean_angle < params["lean_angle"]):
                print("case 2")
                self.cur_offset += cos(params["lean_angle"]) * params["book_width"] + sin(params["lean_angle"]) * params["book_width"] / tan(radians(90) - book.lean_angle)
            elif(old_corner_height > corner_height and book.lean_angle >= params["lean_angle"]):
                print("case 3")
                self.cur_offset += (cos(params["lean_angle"]) * params["book_height"] + sin(params["lean_angle"]) * params["book_width"]) / tan(radians(90) - book.lean_angle) + params["book_width"] / cos(params["lean_angle"]) - sin(params["lean_angle"]) * (params["book_height"] + params["book_width"] / tan(radians(90) - params["lean_angle"]))
            else:
                print("doesn't fit a designed case")
            """
            #self.cur_offset += 1
            
            if last.lean_angle >= current.lean_angle and last.corner_height_right < current.corner_height_left:
                print("case 1")
                self.cur_offset += sin(last.lean_angle) * last.height  - (tan(current.lean_angle)*last.corner_height_right - current.width/cos(current.lean_angle))
            elif last.lean_angle >= current.lean_angle and last.corner_height_right > current.corner_height_left:
                self.cur_offset += current.corner_height_left/tan(radians(90)-last.lean_angle) - (sin(current.lean_angle)*current.width)
            elif last.lean_angle <= 0 and current.lean_angle >= 0:
                print("case 4")
                #self.cur_offset += sin(last.lean_angle) * last.width + cos()
            else:
                print("[WARNING] leaning hit a unusual case. This should not happen")

            self.add_book(current, first)

            
            first = False

    def clean(self):
        col = self.collection
        for obj in col.objects:
            col.objects.unlink(obj)
            bpy.data.meshes.remove(obj.data)


    def apply_parameters(self):
        """Return book parameters with all randomization applied"""

        p = self.parameters

        rndm_book_height = (random.random() * 0.4 - 0.2) * p["rndm_book_height_factor"]
        rndm_book_width = (random.random() * 0.4 - 0.2) * p["rndm_book_width_factor"]
        rndm_book_depth = (random.random() * 0.4 - 0.2) * p["rndm_book_depth_factor"]

        rndm_textblock_offset = (random.random() * 0.4 - 0.2) * p["rndm_textblock_offset_factor"]

        rndm_cover_thickness = (random.random() * 0.4 - 0.2) * p["rndm_cover_thickness_factor"]

        rndm_spline_curl = (random.random() * 0.4 - 0.2) * p["rndm_spline_curl_factor"]

        rndm_hinge_inset = (random.random() * 0.4 - 0.2) * p["rndm_hinge_inset_factor"]
        rndm_hinge_width = (random.random() * 0.4 - 0.2) * p["rndm_hinge_width_factor"]

        rndm_spacing = random.random() * p["rndm_spacing_factor"]

        rndm_lean_angle = (random.random() * 0.8 - 0.4) * p["rndm_lean_angle_factor"]

        book_height = p["scale"] * p["book_height"] * (1 + rndm_book_height)
        book_width = p["scale"] * p["book_width"] * (1 + rndm_book_width)
        book_depth = p["scale"] * p["book_depth"] * (1 + rndm_book_depth)

        cover_thickness = p["scale"] * p["cover_thickness"] * (1 + rndm_cover_thickness)

        textblock_height = book_height - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_depth = book_depth - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_thickness = book_width - 2 * cover_thickness

        spline_curl = p["scale"] * p["spline_curl"] * (1 + rndm_spline_curl)

        hinge_inset = p["scale"] * p["hinge_inset"] * (1 + rndm_hinge_inset)
        hinge_width = p["scale"] * p["hinge_width"] * (1 + rndm_hinge_width)

        spacing = p["scale"] * p["spacing"] * (1 + rndm_spacing)

        lean = p["lean_amount"] > random.random()

        lean_dir_factor = 1 if random.random() > (.5 - p["lean_direction"] / 2) else -1

        lean_angle = p["lean_angle"] * (1 + rndm_lean_angle) * lean_dir_factor if lean else 0

        return {"book_height": book_height,
                "cover_thickness": cover_thickness,
                "book_depth": book_depth,
                "textblock_height": textblock_height,
                "textblock_depth": textblock_depth,
                "textblock_thickness": textblock_thickness,
                "spline_curl": spline_curl,
                "hinge_inset": hinge_inset,
                "hinge_width": hinge_width,
                "spacing": spacing,
                "book_width": book_width,
                "lean": lean,
                "lean_angle": lean_angle}
