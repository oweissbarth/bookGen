#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================


bl_info = {
    "name": "BookGen",
    "description": "Generate books to fill shelfs",
    "author": "Oliver Weissbarth",
    "version": (0, 5),
    "blender": (2, 7, 0),
    "location": "View3D > Add > Mesh",
    "warning": "Alpha",
    "wiki_url": "",
    "category": "Add Mesh"}



import bpy
from mathutils import Vector
import random
import time
from math import pi, radians, sin , cos

from bookGen.utils import *


class bookGen(bpy.types.Operator):
    bl_idname = "object.book_gen"
    bl_label = "BookGen"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def hinge_inset_guard(self, context):
        if(self.hinge_inset> self.cover_thickness):
            self.hinge_inset = self.cover_thickness-self.cover_thickness/8

    mode = bpy.props.EnumProperty(name="mode", items=(('stack', "stack", "Generate a stack of books"), ('shelf', "shelf", "Generate a shelf of books")), default='shelf')
    
    width = bpy.props.FloatProperty(name="width", default=1, min=0)
    scale = bpy.props.FloatProperty(name="scale", default=1, min=0)
    seed = bpy.props.IntProperty(name="seed", default=0)

    
    axis = bpy.props.EnumProperty(name="axis", items=(("0","x", "distribute along the x-axis"), ("1","y", "distribute along the y-axis"), ("2", "custom", "distribute along a custom axis")))
    angle = bpy.props.FloatProperty(name="angle", unit='ROTATION')
    
    
    alignment = bpy.props.EnumProperty(name="alignment", items=(("0", "spline", "align books at the spline (usually front in a shelf)"), ("1", "fore egde", "align books along there fore edge (usually back in a shelf)"), ("2", "center", "align along center")))
    

    book_height = bpy.props.FloatProperty(name="height", default=3.0, min=.0, unit="LENGTH")
    rndm_book_height_factor = bpy.props.FloatProperty(name=" random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    book_width = bpy.props.FloatProperty(name="width", default=0.5, min=.01, unit="LENGTH")
    rndm_book_width_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    book_depth = bpy.props.FloatProperty(name="depth", default=3.0, min=.0, unit="LENGTH")
    rndm_book_depth_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    
    cover_thickness = bpy.props.FloatProperty(name="cover thickness", default=0.05, min=.0, step=.02, unit="LENGTH", update=hinge_inset_guard)
    rndm_cover_thickness_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    textblock_offset = bpy.props.FloatProperty(name="textblock offset", default=0.1, min=.0, unit="LENGTH")
    rndm_textblock_offset_factor = bpy.props.FloatProperty(name="randon", default=1, min=.0, soft_max=1, subtype="FACTOR")

    spline_curl = bpy.props.FloatProperty(name="spline curl", default=0.01,  step=.02, min=.0, unit="LENGTH")
    rndm_spline_curl_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    hinge_inset = bpy.props.FloatProperty(name="hinge inset", default=0.03, min=.0, step=.01, unit="LENGTH", update=hinge_inset_guard)
    rndm_hinge_inset_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    hinge_width = bpy.props.FloatProperty(name="hinge width", default=0.08, min=.0, step=.05, unit="LENGTH")
    rndm_hinge_width_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    
    spacing = bpy.props.FloatProperty(name="spacing", default=0.05, min=.0, unit="LENGTH")
    rndm_spacing_factor = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    subsurf = bpy.props.BoolProperty(name="Add Subsurf-Modifier", default=False)
    smooth = bpy.props.BoolProperty(name="shade smooth", default=False)
    unwrap = bpy.props.BoolProperty(name="unwrap", default=True)
    
    #stack additions
    
    height = bpy.props.FloatProperty(name="height", default = 1, min=.0, )
    rotation = bpy.props.FloatProperty(name="rotation", default=0, unit='ROTATION')
    rndm_rotation_factor  = bpy.props.FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")
    
    
    cur_width = 0
    
    cur_offset = 0
       

    
    def check(self, context):
        self.run()
            
    def invoke(self, context, event):
        self.run()
        return {'FINISHED'}
   
    
    def execute(self, context):
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    
    def get_params(self):
        rndm_book_height = (random.random()*0.4-0.2)*self.rndm_book_height_factor
        rndm_book_width = (random.random()*0.4-0.2)*self.rndm_book_width_factor
        rndm_book_depth = (random.random()*0.4-0.2)*self.rndm_book_depth_factor
        
        rndm_textblock_offset = (random.random()*0.4-0.2)*self.rndm_textblock_offset_factor
        
        rndm_cover_thickness = (random.random()*0.4-0.2)*self.rndm_cover_thickness_factor
        
        rndm_spline_curl = (random.random()*0.4-0.2)*self.rndm_spline_curl_factor
        
        rndm_hinge_inset = (random.random()*0.4-0.2)*self.rndm_hinge_inset_factor
        rndm_hinge_width = (random.random()*0.4-0.2)*self.rndm_hinge_width_factor
        
        rndm_spacing = random.random()*self.rndm_spacing_factor
        
        
        book_height = self.scale*self.book_height * ( 1 + rndm_book_height)
        book_width  = self.scale*self.book_width * (1 + rndm_book_width)
        book_depth  = self.scale*self.book_depth * (1 + rndm_book_depth)
        
        cover_thickness = self.scale*self.cover_thickness * (1 + rndm_cover_thickness)

        textblock_height = book_height - self.scale*self.textblock_offset * (1 + rndm_textblock_offset)
        textblock_depth = book_depth - self.scale*self.textblock_offset * (1 + rndm_textblock_offset)
        textblock_thickness = book_width - 2 * cover_thickness

        spline_curl = self.scale*self.spline_curl * (1 + rndm_spline_curl)

        hinge_inset = self.scale*self.hinge_inset * (1 + rndm_hinge_inset)
        hinge_width = self.scale*self.hinge_width * (1 + rndm_hinge_width)
        
        spacing = self.scale *  self.spacing * (1 + rndm_spacing)
        
        return (book_height,
                cover_thickness,
                book_depth,
                textblock_height,
                textblock_depth,
                textblock_thickness,
                spline_curl,
                hinge_inset,
                hinge_width,
                spacing, 
                book_width)
                
    def add_book(self, align_offset, first, book_height,cover_thickness,book_depth,textblock_height,textblock_depth,textblock_thickness,spline_curl,hinge_inset,hinge_width,spacing, book_width):
        
        book = create_book( book_height,
                            cover_thickness,
                            book_depth,
                            textblock_height,
                            textblock_depth,
                            textblock_thickness,
                            spline_curl,
                            hinge_inset,
                            hinge_width,
                            unwrap = self.unwrap)
            
           
            
        book.select = True
        
        if(self.subsurf):
            book.modifiers.new("subd", type='SUBSURF')
            book.modifiers['subd'].levels = 1
        if(self.smooth):
            bpy.ops.object.shade_smooth()
            
            
        if(self.axis == "0"):
            angle = radians(0)
        elif(self.axis == "1"):
            angle = radians(90)
        elif(self.axis == "2"):
            angle = self.angle

            
        book.rotation_euler = [0,0, angle]
        book.location = bpy.context.scene.cursor_location + Vector((cos(angle)*self.cur_offset, sin(angle)*self.cur_offset, book_height/2))
        
        offset_dir = -1 if self.alignment == "1" else 1
        
        if(not first and not self.alignment == "2"):
            book.location += Vector((-offset_dir*sin(angle)*(align_offset+book_depth/2), offset_dir*cos(angle)*(align_offset+book_depth/2),  0))
        
        return book_width 
    
    #TODO
    def stack(self):
        pass        
    
    def shelf(self):
        self.cur_width = 0
        self.cur_offset = 0
        
        random.seed(self.seed)


        first = True
        params = self.get_params()

        align_offset = -params[2]/2

        
        
       
        
        while(self.cur_width + params[-1] < self.width*self.scale):
            old_width = self.add_book(align_offset, first,  *params)
            params = self.get_params()
  
            self.cur_width  += old_width +  params[-2]
            self.cur_offset += params[-1]/2 + old_width/2 + params[-2]
            
            first = False
       

    
    def run(self):
        time_start = time.time()
        
        if(self.mode == 'shelf'):
            self.shelf()
        elif(self.mode == 'stack'):
            self.stack()
        
        print("Finished: %.4f sec" % (time.time() - time_start))
    
    def draw(self, context):
        layout = self.layout
        #layout.prop(self, "mode")
        #layout.separator()
        if(self.mode == 'shelf'):
            layout.prop(self, "width")
            layout.prop(self, "scale")
            layout.prop(self, "seed")
            
            row =  layout.row(align=True)
            row.prop(self, "spacing")
            row.prop(self, "rndm_spacing_factor")
            
            
            
            layout.separator()
            layout.label("axis")
            layout.prop(self, "axis", expand =True)
            sub = layout.column()
            sub.active = self.axis =="2"
            sub.prop(self, "angle")
            
            layout.separator()
            
            layout.label("alignment")
            layout.prop(self, "alignment", expand=True)
            
            layout.separator()
            
 
        
        """elif(self.mode == 'stack'):
            layout.prop(self, "height")
            layout.prop(self, "scale")
            layout.prop(self, "seed")
            
            row =  layout.row(align=True)
            row.prop(self, "rotation")
            row.prop(self, "rndm_rotation_factor")
            
            layout.separator()
        """    
    
        
        proportions = layout.box()
        proportions.label("Proportions:")
        
        row = proportions.row(align=True)
        row.prop(self, "book_height")
        row.prop(self, "rndm_book_height_factor")
        
        row = proportions.row(align=True)
        row.prop(self, "book_depth")
        row.prop(self, "rndm_book_depth_factor")
        
        row = proportions.row(align=True)
        row.prop(self, "book_width")
        row.prop(self, "rndm_book_width_factor")
        
        layout.separator()
        
        details_box = layout.box()
        details_box.label("Details:")
        
        row = details_box.row(align=True)
        row.prop(self, "textblock_offset")
        row.prop(self, "rndm_textblock_offset_factor")
        
        row = details_box.row(align=True)
        row.prop(self, "cover_thickness")
        row.prop(self, "rndm_cover_thickness_factor")
        
        
        row= details_box.row(align=True)
        row.prop(self, "spline_curl")
        row.prop(self, "rndm_spline_curl_factor")
        
        row= details_box.row(align=True)
        row.prop(self, "hinge_inset")
        row.prop(self, "rndm_hinge_inset_factor")

        row= details_box.row(align=True)        
        row.prop(self, "hinge_width")
        row.prop(self, "rndm_hinge_width_factor")
        
        layout.separator()
        
        layout.prop(self, "subsurf")
        layout.prop(self, "smooth")
        layout.prop(self, "unwrap")
            
            
def menu_func(self, context):
    self.layout.operator("object.book_gen", text="Add Books", icon='PLUGIN')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    
if __name__ == "__main__":
    unregister()
    register()
