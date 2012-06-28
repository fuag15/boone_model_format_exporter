# -*- coding: iso-8859-1 -*-
bl_info = {
  "name": "Export Boone Model Data",
  "author": "Michael Boone",
  "version": (0, 5),
  "blender": (2, 5, 3),
  "api": 31847,
  "location": "File > Export > Boone Mode (.bmdl / .bbne)",
  "description": "Exporte Boone Engine (.bmdl / .bbne)",
  "warning": "",
  "wiki_url" : "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
    "Scripts/Import-Export/Boone",
  "category": "Import-Export" }


import bpy
import os
from mathutils import *
from math import *
from bpy.props import *


#f v1(x,y,z) n1(x,y,z) uv(x,y, [z]) <variable list of bones that have influence> #not implimented -> <material> NOTE: points relative to first bone with ifluence


class FileMaker:
  def __init__(self, fileName):
    self.Name = fileName
    self.Handle = open(fileName, 'w')
    
  def close(self):
    self.Handle.close()


def export_verts(fileName):
  modelHandle = FileMaker(fileName)
  modelFile = modelHandle.Handle

  for selObj in bpy.context.selected_objects:
    if selObj.type == 'MESH':
      MainMeshObject = selObj
    elif selObj.type == 'ARMATURE':
      MainArmatureObject = selObj

  ArmatureData = MainArmatureObject.data
  ArmatureBones = ArmatureData.bones
  FirstBoneName = ArmatureBones[0].basename

  MeshDataObject = MainMeshObject.data
  MeshFaces = MeshDataObject.faces
  meshFaceLength = len(MeshFaces)


  for i, face in enumerate(MeshFaces):
    verticesIndex = face.vertices
    uvIndex = []
    uvIndex.append(MeshDataObject.uv_textures[0].data[i].uv1)
    uvIndex.append(MeshDataObject.uv_textures[0].data[i].uv2)
    uvIndex.append(MeshDataObject.uv_textures[0].data[i].uv3)
    if len(verticesIndex) > 3:
      '''SHOULD NEVER HAPPEN POP WARNING HERE THAT MESH IS NOT TRI'''
      verticesIndex = verticesIndex[:-1]
    string = []
    string.append('f')
    for j, currentIndex in enumerate(verticesIndex):
      currentVertex = MeshDataObject.vertices[currentIndex]
      normal = currentVertex.normal
      point = currentVertex.co
      vertGroups = currentVertex.groups
      boneSet = []
      for vertGroup in vertGroups:
        groupId = vertGroup.group
        weight = vertGroup.weight
        bone_name = MainMeshObject.vertex_groups[groupId].name
        boneSet.append([weight, bone_name]) 
      boneReference = ArmatureBones[boneSet[0][1]]
      transFrom = MainArmatureObject.matrix_world.copy()
      transFrom = transFrom.invert()
      transFrom = transFrom * MainMeshObject.matrix_world
      normal = normal * transFrom
      point = point * transFrom
      string.append(str(point.x) + ' ' + str(point.y) + ' ' + str(point.z))
      string.append(str(normal.x) + ' ' + str(normal.y) + ' ' + str(normal.z))
      string.append('[')
      string.append(str(uvIndex[j].x) + ' ' + str(uvIndex[j].y))
      string.append(']')
      string.append('[')
      for boneGroup in boneSet:
        string.append(str(boneGroup[0]) + ' ' + str(boneGroup[1]))
      string.append(']')
    modelFile.write(' '.join(string) + '\n')

  modelHandle.close()


#b b bone_name root_bone_name p[parent bone list] c[child bone list] <bone center> <bone vector> <bone length> <bone vector x> <bone vector y> <bone vector z> #not implimented <ik_start> <ik_end> #NOTE: bone coordinates should be in root bone space

def export_bones(fileName):
  boneHandle = FileMaker(fileName)
  boneFile = boneHandle.Handle

  for selObj in bpy.context.selected_objects:
    if selObj.type == 'MESH':
      MainMeshObject = selObj
    elif selObj.type == 'ARMATURE':
      MainArmatureObject = selObj

  ArmatureData = MainArmatureObject.data
  ArmatureBones = ArmatureData.bones
  FirstBoneName = ArmatureBones[0].basename

  root_bone = ArmatureData.bones['Root']

  for bone in ArmatureData.bones:
    bone_matrix = bone.matrix_local.copy()
    bone_matrix = bone_matrix.invert()
    bone_name = bone.basename
    bone_center = Vector([0,0,0]) * bone_matrix
    parent_list = bone.parent
    string = []
    child_list = []
    for child in bone.children:
      child_list.append[child.basename]
    bone_vector = bone.vector * bone_matrix
    bone_x = bone.x_axis * bone_matrix
    bone_y = bone.y_axis * bone_matrix
    bone_z = bone.z_axis * bone_matrix
    bone_length = bone.length
    ''' WARNING: IK chains not implimented yet '''
    string.append('b ' + bone_name + ' ' + root_bone.basename)
    if parent_list != None:
      string.append('p[' + parent_list + ']')
    else:
      string.append('p[]')
    if child_list != None:
      string.append('p[' + ' '.join(child_list) + ']')
    string.append(str(bone_center.x) + ' ' + str(bone_center.y) + ' ' + str(bone_center.z))
    string.append(str(bone_vector.x) + ' ' + str(bone_vector.y) + ' ' + str(bone_vector.z))
    string.append(str(bone_length))
    string.append(str(bone_x.x) + ' ' + str(bone_x.y) + ' ' + str(bone_x.z))
    string.append(str(bone_y.x) + ' ' + str(bone_y.y) + ' ' + str(bone_y.z))
    string.append(str(bone_z.x) + ' ' + str(bone_z.y) + ' ' + str(bone_z.z))
    boneFile.write(' '.join(string) + '\n')

  boneHandle.close()

def do_export(filename):
  modelFile = filename + '.bmdl'
  boneFile = filename + '.bbne'
  export_verts(modelFile)
  export_bones(boneFile)

class ExportBooneData(bpy.types.Operator):
  '''Export everything '''
  bl_idname = "export.boone_data"
  bl_label = "Export Boone Things"
  __doc__ = "Chose one mesh and one armature for now :)"
  
  # List of operator properties, the attributes will be assigned
  # to the class instance from the operator settings before calling.
  
  filepath = StringProperty(name="File Path", description="Filepath used for exporting the files", maxlen=1024, default="", subtype='FILE_PATH')
  
  @classmethod
  def poll(cls, context):
    return context.active_object != None
  
  def execute(self, context):
    do_export(self.filepath)
    return {'FINISHED'}
  
  def invoke(self, context, event):
    wm = context.window_manager
    wm.fileselect_add(self)
    return {'RUNNING_MODAL'}

class OBJECT_OT_BooneExport(bpy.types.Operator):
    bl_idname = "OBJECT_OT_BooneExport"
    bl_label = "Boone Export"
    __doc__ = "Select export setting for Boone Models."
    
    def invoke(self, context, event):
        default_path = os.path.splitext(bpy.data.filepath)[0]   
        do_export(default_path)
        return{'FINISHED'}

def menu_func(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0]
    self.layout.operator("export.boone_data", text="Boone Mesh / Bone structure (.bmdl / .bbne )").filepath = default_path

def register():
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
  