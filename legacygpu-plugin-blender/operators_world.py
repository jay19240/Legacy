import bpy
import bmesh
import math
import threading
import subprocess
import os
import signal
import webbrowser
from . import functions
from . import utils
# ----------------------------------------------------------------------------------


def register():
  bpy.utils.register_class(WARME_OT_create_jsm)
  bpy.utils.register_class(WARME_OT_cast_to_jsm)
  bpy.utils.register_class(WARME_OT_create_jam)
  bpy.utils.register_class(WARME_OT_cast_to_jam)
  bpy.utils.register_class(WARME_OT_create_jwm)
  bpy.utils.register_class(WARME_OT_cast_to_jwm)
  bpy.utils.register_class(WARME_OT_create_jnm)
  bpy.utils.register_class(WARME_OT_cast_to_jnm)
  bpy.utils.register_class(WARME_OT_create_jsv)
  bpy.utils.register_class(WARME_OT_cast_to_jsv)
  bpy.utils.register_class(WARME_OT_create_jwa)
  bpy.utils.register_class(WARME_OT_cast_to_jwa)
  bpy.utils.register_class(WARME_OT_create_grf)
  bpy.utils.register_class(WARME_OT_create_jlm_points)
  bpy.utils.register_class(WARME_OT_create_jlm_curve)
  bpy.utils.register_class(WARME_OT_create_jlt_point)
  bpy.utils.register_class(WARME_OT_create_jlt_spot)
  bpy.utils.register_class(WARME_OT_create_special_dcl)
  bpy.utils.register_class(WARME_OT_create_special_sun)
  bpy.utils.register_class(WARME_OT_create_special_shadow_projector)
  bpy.utils.register_class(WARME_OT_create_special_shadow_projector_target)
  bpy.utils.register_class(WARME_OT_create_special_skybox)
  bpy.utils.register_class(WARME_OT_create_special_particles)
  bpy.utils.register_class(WARME_OT_create_entity_aabb)
  bpy.utils.register_class(WARME_OT_create_entity_cylinder)
  bpy.utils.register_class(WARME_OT_create_entity_sphere)
  bpy.utils.register_class(WARME_OT_create_entity_circle)
  bpy.utils.register_class(WARME_OT_create_entity_plane)
  bpy.utils.register_class(WARME_OT_run_auggie)
  bpy.utils.register_class(WARME_OT_run_server)
  bpy.utils.register_class(WARME_OT_kill_server)
  bpy.utils.register_class(WARME_OT_run_game)
  bpy.utils.register_class(WARME_OT_build_game)


def unregister():
  bpy.utils.unregister_class(WARME_OT_create_jsm)
  bpy.utils.unregister_class(WARME_OT_cast_to_jsm)
  bpy.utils.unregister_class(WARME_OT_create_jam)
  bpy.utils.unregister_class(WARME_OT_cast_to_jam)
  bpy.utils.unregister_class(WARME_OT_create_jwm)
  bpy.utils.unregister_class(WARME_OT_cast_to_jwm)
  bpy.utils.unregister_class(WARME_OT_create_jnm)
  bpy.utils.unregister_class(WARME_OT_cast_to_jnm)
  bpy.utils.unregister_class(WARME_OT_create_jsv)
  bpy.utils.unregister_class(WARME_OT_cast_to_jsv)
  bpy.utils.unregister_class(WARME_OT_create_jwa)
  bpy.utils.unregister_class(WARME_OT_cast_to_jwa)
  bpy.utils.unregister_class(WARME_OT_create_grf)
  bpy.utils.unregister_class(WARME_OT_create_jlm_points)
  bpy.utils.unregister_class(WARME_OT_create_jlm_curve)
  bpy.utils.unregister_class(WARME_OT_create_jlt_point)
  bpy.utils.unregister_class(WARME_OT_create_jlt_spot)
  bpy.utils.unregister_class(WARME_OT_create_special_dcl)
  bpy.utils.unregister_class(WARME_OT_create_special_sun)
  bpy.utils.unregister_class(WARME_OT_create_special_shadow_projector)
  bpy.utils.unregister_class(WARME_OT_create_special_shadow_projector_target)
  bpy.utils.unregister_class(WARME_OT_create_special_skybox)
  bpy.utils.unregister_class(WARME_OT_create_special_particles)
  bpy.utils.unregister_class(WARME_OT_create_entity_aabb)
  bpy.utils.unregister_class(WARME_OT_create_entity_cylinder)
  bpy.utils.unregister_class(WARME_OT_create_entity_sphere)
  bpy.utils.unregister_class(WARME_OT_create_entity_circle)
  bpy.utils.unregister_class(WARME_OT_create_entity_plane)
  bpy.utils.unregister_class(WARME_OT_run_auggie)
  bpy.utils.unregister_class(WARME_OT_run_server)
  bpy.utils.unregister_class(WARME_OT_kill_server)
  bpy.utils.unregister_class(WARME_OT_run_game)
  bpy.utils.unregister_class(WARME_OT_build_game)


# ----------------------------------------------------------------------------------
# JSM
# ----------------------------------------------------------------------------------
class WARME_OT_create_jsm(bpy.types.Operator):
  """Create JSM""" 
  bl_idname = "object.create_jsm"
  bl_label = "Static Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_cube_add()
    cube = context.active_object
    cube.name = "StaticMesh"
    cube.color = (0.6, 0.65, 0.7, 1)

    collection = utils.get_or_create_collection("JSM")
    utils.unlink_from_all_collections(cube)
    collection.objects.link(cube)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_cast_to_jsm(bpy.types.Operator):
  """Cast To JSM""" 
  bl_idname = "object.cast_to_jsm"
  bl_label = "Static Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    collection = utils.get_or_create_collection("JSM")

    for object in bpy.context.selected_objects:
      object.color = (0.6, 0.65, 0.7, 1)
      utils.unlink_from_all_collections(object)
      collection.objects.link(object)
      self.report({'INFO'}, "Cast successful ✔")
    #endfor

    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JAM
# ----------------------------------------------------------------------------------
class WARME_OT_create_jam(bpy.types.Operator):
  """Create JAM""" 
  bl_idname = "object.create_jam"
  bl_label = "Animated Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_cube_add()
    cube = context.active_object
    cube.name = "AnimatedMesh"
    cube.color = (0.3, 0.8, 0.4, 1)

    collection = utils.get_or_create_collection("JAM")
    utils.unlink_from_all_collections(cube)
    collection.objects.link(cube)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_cast_to_jam(bpy.types.Operator):
  """Cast To JAM""" 
  bl_idname = "object.cast_to_jam"
  bl_label = "Animated Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    collection = utils.get_or_create_collection("JAM")

    for object in bpy.context.selected_objects:
      object.color = (0.3, 0.8, 0.4, 1)
      utils.unlink_from_all_collections(object)
      collection.objects.link(object)
      self.report({'INFO'}, "Cast successful ✔")
    #endfor

    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JWM
# ----------------------------------------------------------------------------------
class WARME_OT_create_jwm(bpy.types.Operator):
  """Create JWM""" 
  bl_idname = "object.create_jwm"
  bl_label = "Walk Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_plane_add()
    plane = context.active_object
    plane.name = "WalkMesh"
    plane.color = (0.2, 0.7, 1.0, 1)

    collection = utils.get_or_create_collection("JWM")
    utils.unlink_from_all_collections(plane)
    collection.objects.link(plane)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_cast_to_jwm(bpy.types.Operator):
  """Cast To JWM""" 
  bl_idname = "object.cast_to_jwm"
  bl_label = "Walk Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    collection = utils.get_or_create_collection("JWM")

    for object in bpy.context.selected_objects:
      object.color = (0.2, 0.7, 1.0, 1)
      utils.unlink_from_all_collections(object)
      collection.objects.link(object)
      self.report({'INFO'}, "Cast successful ✔")
    #endfor

    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JNM
# ----------------------------------------------------------------------------------
class WARME_OT_create_jnm(bpy.types.Operator):
  """Create JNM""" 
  bl_idname = "object.create_jnm"
  bl_label = "Hit Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_plane_add()
    plane = context.active_object
    plane.name = "HitMesh"
    plane.color = (1.0, 0.2, 0.2, 1)

    collection = utils.get_or_create_collection("JNM")
    utils.unlink_from_all_collections(plane)
    collection.objects.link(plane)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_cast_to_jnm(bpy.types.Operator):
  """Cast To JNM""" 
  bl_idname = "object.cast_to_jnm"
  bl_label = "Hit Mesh"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    collection = utils.get_or_create_collection("JNM")

    for object in bpy.context.selected_objects:
      object.color = (1.0, 0.2, 0.2, 1)
      utils.unlink_from_all_collections(object)
      collection.objects.link(object)
      self.report({'INFO'}, "Cast successful ✔")
    #endfor

    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JSV
# ----------------------------------------------------------------------------------
class WARME_OT_create_jsv(bpy.types.Operator):
  """Create JSV""" 
  bl_idname = "object.create_jsv"
  bl_label = "Shadow Volume"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_cube_add()
    cube = context.active_object
    cube.name = "ShadowVolume"
    cube.color = (0.1, 0.05, 0.2, 1)

    collection = utils.get_or_create_collection("JSV")
    utils.unlink_from_all_collections(cube)
    collection.objects.link(cube)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_cast_to_jsv(bpy.types.Operator):
  """Cast To JSV""" 
  bl_idname = "object.cast_to_jsv"
  bl_label = "Shadow Volume"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    collection = utils.get_or_create_collection("JSV")

    for object in bpy.context.selected_objects:
      object.color = (0.1, 0.05, 0.2, 1)
      utils.unlink_from_all_collections(object)
      collection.objects.link(object)
      self.report({'INFO'}, "Cast successful ✔")
    #endfor

    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JWA
# ----------------------------------------------------------------------------------
class WARME_OT_create_jwa(bpy.types.Operator):
  """Create JWA""" 
  bl_idname = "object.create_jwa"
  bl_label = "Water"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_grid_add(
      size=20, 
      x_subdivisions=33, 
      y_subdivisions=33
    )

    grid = context.active_object
    grid.name = "Water"
    grid.color = (0, 0, 1, 1)

    collection = utils.get_or_create_collection("JWA")
    utils.unlink_from_all_collections(grid)
    collection.objects.link(grid)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_cast_to_jwa(bpy.types.Operator):
  """Cast To JWA""" 
  bl_idname = "object.cast_to_jwa"
  bl_label = "Water"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    collection = utils.get_or_create_collection("JWA")

    for object in bpy.context.selected_objects:
      object.color = (0.0, 0.0, 1.0, 1)
      utils.unlink_from_all_collections(object)
      collection.objects.link(object)
      self.report({'INFO'}, "Cast successful ✔")
    #endfor

    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# GRF
# ----------------------------------------------------------------------------------
class WARME_OT_create_grf(bpy.types.Operator):
  """Create GRF""" 
  bl_idname = "object.create_grf"
  bl_label = "Graph Node"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    # 1. Création d'un mesh vide avec un seul sommet à l'origine
    mesh = bpy.data.meshes.new("Graph_Data")
    obj = bpy.data.objects.new("Graph", mesh)
    bm = bmesh.new()
    bm.verts.new((0, 0, 0))
    bm.to_mesh(mesh)
    bm.free()

    collection = utils.get_or_create_collection("GRF")
    collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    if "grf_node_type" not in mesh.attributes:
      mesh.attributes.new(name="grf_node_type", type='STRING', domain='POINT')
    if "grf_visual" not in mesh.attributes:
      mesh.attributes.new(name="grf_visual", type='FLOAT_COLOR', domain='POINT')
    #if

    space = context.space_data
    if space.type == 'VIEW_3D':
      space.shading.color_type = 'VERTEX'
      space.overlay.show_extra_indices = False # Optionnel
      space.shading.type = 'SOLID'
    #if

    self.report({'INFO'}, "Graph prêt")
    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JLM
# ----------------------------------------------------------------------------------
class WARME_OT_create_jlm_points(bpy.types.Operator):
  """Create JLM Points""" 
  bl_idname = "object.create_jlm_points"
  bl_label = "Line Points"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    mesh = bpy.data.meshes.new("LineMesh")
    obj = bpy.data.objects.new("LineObject", mesh)
    obj.name = "LinePoints"
    obj.color = (1.0, 0.3, 0.7, 1)

    bm = bmesh.new()
    v1 = bm.verts.new((0, 0, 0))
    v2 = bm.verts.new((2, 0, 0))
    bm.edges.new((v1, v2))
    bm.to_mesh(mesh)
    bm.free()

    collection = utils.get_or_create_collection("JLM")
    utils.unlink_from_all_collections(obj)
    collection.objects.link(obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_jlm_curve(bpy.types.Operator):
  """Create JLM Curve""" 
  bl_idname = "object.create_jlm_curve"
  bl_label = "Line Curve"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.curve.primitive_nurbs_path_add()
    obj = context.active_object
    obj.name = "CatmullRomPath"
    obj.color = (1.0, 0.3, 0.7, 1)

    group = bpy.data.node_groups.new(name="MonNoeudSpline", type='GeometryNodeTree')
    group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    nodes = group.nodes
    input_node = nodes.new(type='NodeGroupInput')
    output_node = nodes.new(type='NodeGroupOutput')
    spline_node = nodes.new(type='GeometryNodeCurveSplineType')
    spline_node.spline_type = 'CATMULL_ROM'

    links = group.links
    links.new(input_node.outputs['Geometry'], spline_node.inputs['Curve']) # Input -> Set Spline Type
    links.new(spline_node.outputs['Curve'], output_node.inputs['Geometry'])

    modifier = obj.modifiers.new(name="CatmullRomGN", type='NODES')
    modifier.node_group = group

    collection = utils.get_or_create_collection("JLM")
    utils.unlink_from_all_collections(obj)
    collection.objects.link(obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# JLT
# ----------------------------------------------------------------------------------
class WARME_OT_create_jlt_point(bpy.types.Operator):
  """Create JLT Point""" 
  bl_idname = "object.create_jlt_point"
  bl_label = "Point Light"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    light_data = bpy.data.lights.new(name="JLT_Point_Data", type='POINT')
    obj = bpy.data.objects.new(name="PointLight", object_data=light_data)

    collection = utils.get_or_create_collection("JLT")
    utils.unlink_from_all_collections(obj)
    collection.objects.link(obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_jlt_spot(bpy.types.Operator):
  """Create JLT Spot""" 
  bl_idname = "object.create_jlt_spot"
  bl_label = "Spot Light"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    light_data = bpy.data.lights.new(name="JLT_Spot_Data", type='SPOT')
    obj = bpy.data.objects.new(name="SpotLight", object_data=light_data)

    collection = utils.get_or_create_collection("JLT")
    utils.unlink_from_all_collections(obj)
    collection.objects.link(obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# SPECIAL
# ----------------------------------------------------------------------------------
class WARME_OT_create_special_dcl(bpy.types.Operator):
  """Create Decal""" 
  bl_idname = "object.create_special_dcl"
  bl_label = "Decal"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    empty_obj = bpy.data.objects.new("Decal", None)
    collection = utils.get_or_create_collection("DCL")
    utils.unlink_from_all_collections(empty_obj)
    collection.objects.link(empty_obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_special_sun(bpy.types.Operator):
  """Create Sun""" 
  bl_idname = "object.create_special_sun"
  bl_label = "Sun"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    empty_obj = bpy.data.objects.new("Sun", None)
    empty_obj.empty_display_type = 'SINGLE_ARROW'
    empty_obj.empty_display_size = 4.0
    collection = utils.get_or_create_collection("Collection")
    utils.unlink_from_all_collections(empty_obj)
    collection.objects.link(empty_obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_special_shadow_projector(bpy.types.Operator):
  """Create Shadow Projector""" 
  bl_idname = "object.create_special_shadow_projector"
  bl_label = "Shadow Projector"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    empty_obj = bpy.data.objects.new("ShadowProjector", None)
    empty_obj.empty_display_type = 'CUBE'
    collection = utils.get_or_create_collection("Collection")
    utils.unlink_from_all_collections(empty_obj)
    collection.objects.link(empty_obj)
    utils.setup_tracking("ShadowProjector", "ShadowProjectorTarget")

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_special_shadow_projector_target(bpy.types.Operator):
  """Create Shadow Projector Target""" 
  bl_idname = "object.create_special_shadow_projector_target"
  bl_label = "Shadow Projector Target"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    empty_obj = bpy.data.objects.new("ShadowProjectorTarget", None)
    empty_obj.empty_display_type = 'CONE'
    empty_obj.empty_display_size = 0.1
    empty_obj.rotation_euler[0] = math.radians(90)

    collection = utils.get_or_create_collection("Collection")
    utils.unlink_from_all_collections(empty_obj)
    collection.objects.link(empty_obj)
    utils.setup_tracking("ShadowProjector", "ShadowProjectorTarget")

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_special_skybox(bpy.types.Operator):
  """Create Skybox""" 
  bl_idname = "object.create_special_skybox"
  bl_label = "Skybox"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    empty_obj = bpy.data.objects.new("Skybox", None)
    empty_obj.empty_display_type = 'CUBE'
    empty_obj.empty_display_size = 600

    collection = utils.get_or_create_collection("SKY")
    utils.unlink_from_all_collections(empty_obj)
    collection.objects.link(empty_obj)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_special_particles(bpy.types.Operator):
  """Create Particles""" 
  bl_idname = "object.create_special_particles"
  bl_label = "Particles"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_cone_add()
    particles = context.active_object
    particles.name = "Particles"
    particles.color = (0.0, 1.0, 0.0, 0.2)

    collection = utils.get_or_create_collection("PRT")
    utils.unlink_from_all_collections(particles)
    collection.objects.link(particles)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


# ----------------------------------------------------------------------------------
# ENTITIES
# ----------------------------------------------------------------------------------
class WARME_OT_create_entity_aabb(bpy.types.Operator):
  """Create Entity AABB""" 
  bl_idname = "object.create_entity_aabb"
  bl_label = "AABB"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_cube_add()
    cube = context.active_object
    cube.name = "Entity"
    cube["entity_shape"] = "AABB"
    cube.color = (1.0, 0.0, 0.0, 0.2)

    collection = utils.get_or_create_collection("ENT")
    utils.unlink_from_all_collections(cube)
    collection.objects.link(cube)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_entity_cylinder(bpy.types.Operator):
  """Create Entity Cylinder""" 
  bl_idname = "object.create_entity_cylinder"
  bl_label = "Cylinder"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_cylinder_add()
    cylinder = context.active_object
    cylinder.name = "Entity"
    cylinder["entity_shape"] = "CYLINDER"
    cylinder.color = (1.0, 0.0, 0.0, 0.2)

    collection = utils.get_or_create_collection("ENT")
    utils.unlink_from_all_collections(cylinder)
    collection.objects.link(cylinder)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_entity_sphere(bpy.types.Operator):
  """Create Entity Sphere""" 
  bl_idname = "object.create_entity_sphere"
  bl_label = "Sphere"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_uv_sphere_add()
    sphere = context.active_object
    sphere.name = "Entity"
    sphere["entity_shape"] = "SPHERE"
    sphere.color = (1.0, 0.0, 0.0, 0.2)

    collection = utils.get_or_create_collection("ENT")
    utils.unlink_from_all_collections(sphere)
    collection.objects.link(sphere)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_entity_circle(bpy.types.Operator):
  """Create Entity Circle""" 
  bl_idname = "object.create_entity_circle"
  bl_label = "Circle"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_circle_add()
    circle = context.active_object
    circle.name = "Entity"
    circle["entity_shape"] = "CIRCLE"
    circle.color = (1.0, 0.0, 0.0, 0.2)

    collection = utils.get_or_create_collection("ENT")
    utils.unlink_from_all_collections(circle)
    collection.objects.link(circle)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_create_entity_plane(bpy.types.Operator):
  """Create Entity Plane""" 
  bl_idname = "object.create_entity_plane"
  bl_label = "Plane"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    bpy.ops.mesh.primitive_plane_add()
    plane = context.active_object
    plane.name = "Entity"
    plane["entity_shape"] = "PLANE"
    plane.color = (1.0, 0.0, 0.0, 0.2)

    collection = utils.get_or_create_collection("ENT")
    utils.unlink_from_all_collections(plane)
    collection.objects.link(plane)

    self.report({'INFO'}, "Creation successful ✔")
    return {"FINISHED"}


class WARME_OT_run_auggie(bpy.types.Operator):
  bl_idname = "object.run_auggie"
  bl_label = "Send to Agent"

  def execute(self, context):
    scene = context.scene
    prompt = scene.auggie_prompt
    
    if "AUGGIE_TERMINAL" not in bpy.data.texts:
      bpy.data.texts.new("AUGGIE_TERMINAL")
    #endif

    txt = bpy.data.texts["AUGGIE_TERMINAL"]
    txt.write(f"\n>>> PROMPT: {prompt}\n")

    text_area = None
    for area in context.screen.areas:
      if area.type == 'TEXT_EDITOR':
        text_area = area
        break
      #endif
    #endfor

    if text_area:
      text_area.spaces.active.text = txt
    #endif
    else:
      context.area.type = 'TEXT_EDITOR'
      context.area.spaces.active.text = txt
    #endif

    scene.auggie_status = "En cours..."
    thread = threading.Thread(target=self.run_cli, args=(prompt, scene, txt.name, context))
    thread.start()
    return {'FINISHED'}

  def run_cli(self, prompt, scene, txt_name, context):
    txt = bpy.data.texts.get(txt_name)
    try:
      pre_prompt = (
        "Analyse le code source du moteur de jeux Legacy. "
        "Génère ton code dans le dossier game en t'inspirant des examples fournis avec celui-ci. "
        "Indications sur les repères: "
        "- Repère de la main droite "
        "- L'axe X pointe vers la droite "
        "- L'axe Y pointe vers le haut "
        "- L'axe Z pointe vers l'extérieur de l'écran (convention OpenGL) "
        "- Le mouvement des entités sont toujours vers forward (-Z). "
        "- Utilise la fonction VEC3_FORWARD_NEGATIVE_Z pour convertir les angles vers l'axe forward. "
        "- Les exemples airplane et racing_ship sont de bons exemples à suivres pour que tu utilises les orientations correctement "
        "Indications sur la physique: "
        "- Tu dois toujours priorisé les classes Gfx3PhysicsJNM et Gfx3PhysicsJWM quand cela est possible "
        "- Tu dois utilisés les classes physiques de bases et des calcules mathématique en priorité "
        "Les règles sont les suivantes: "
        "- Toujours utilisé les getters et setters plutôt que d'accéder aux variables membres même si elles sont publiques "
        "- Fait bien attention aux fonctionnalités présentes dans le moteur pour éviter de les recoder, ne réinvente pas la roue quand c'est pas necessaire "
        "- Tu dois créer un seul fichier minimaliste couvrant uniquement la demande, fonctionnelle, ni plus ni moins. "
        "- Pour les modifications ultérieur, tu ne dois pas créer de fichiers mais réutiliser et modifier le fichier existant. "
        "- Peu importe la taille du code source à générer, tu dois suivre ces règles. "
        "- Tu dois toujours priorisé la physique manuelle mathématique pure et utilisé les fonctions de rotations, position, scale et utilitaire (UT) autant que possible "
        "- Tu dois toujours utilisé le fichier 'public/scene.blend.pak' pour analyser les ressources que l'utilisateur à créer. "
        "- Tu dois jamais toucher aux dossiers lib et examples. "
        "- Par default, laisse la caméra dans son état d'origine, sauf si l'utilisateur te demande explicitement de la bouger "
        "- Tu peux écrire plusieurs classes dans le même fichier "
        "Quelques Tips: "
        "- Il te demandera d'utiliser certains de ces ressources, tu pourras les retrouver grâce aux différentes catégories d'objets EnginePackItemList (voir l'exemple: pack). "
        "- Tu peux piocher la dedans comme dans un sac à bonbon et récupérer ce que tu as besoin. "
        "- Liste de tous les formats et gestionnaire associés, si tu trouves un format dans l'archive, tu dois appeller sont renderer ou gestionnaire dans la demo: "
        "  - bin = Fichier binaire "
        "  - sst = Fichier Spritesheet "
        "  - jsc = Fichier de Script en format JSON "
        "  - snd = Fichier sonore "
        "  - tex = Fichier de texture "
        "  - mat = Fichier de Material "
        "  - jam = Fichier de Mesh Animés; (gfx3MeshRenderer) "
        "  - jsm = Fichier de Mesh Statique; (gfx3MeshRenderer) "
        "  - obj = Fichier de Mesh Wavefront; (gfx3MeshRenderer) "
        "  - dcl = Fichier de Decal; necessite; (gfx3MeshRenderer) "
        "  - jas = Fichier de Sprite Animés; (gfx3SpriteRenderer) "
        "  - jss = Fichier de Sprite Statique; (gfx3SpriteRenderer) "
        "  - sky = Fichier de Skybox; (gfx3SkyboxRenderer) "
        "  - prt = Fichier de Particles; (gfx3ParticlesRenderer) "
        "  - jwa = Fichier de plan d'eau; (gfx3WaterRenderer) "
        "  - jwm = Fichier Walkmesh (FF7, Metal Gear, ...) "
        "  - jnm = Fichier Hitmesh (UT, Quake, ...) "
        "  - jlm = Fichier de lignes "
        "  - crv = Fichier de courbes Catmull-rom "
        "  - jsv = Fichier d'Ombres volumétriques; (gfx3ShadowVolumeRenderer) "
        "  - jlt = Fichier de Lumières "
        "  - grf = Fichier de Graph 3D "
        "  - grd = Fichier de Grille 3D "
        "  - ent = Fichier d'entité "
        "Fait attention à bien appeller les gestionnaires lorsque cela est necessaires (Le moteur necessite d'appeller ces fonctions pour des raisons de performances), voici une liste complete typique: "
        " gfx3Manager.beginRender(); "
        " gfx3MeshShadowRenderer.render(); "
        " gfx3ShadowVolumeRenderer.render(); "
        " gfx3Manager.setDestinationTexture(gfx3PostRenderer.getSourceTexture()); "
        " gfx3Manager.beginPassRender(0); "
        " gfx3SkyboxRenderer.render(); "
        " gfx3DebugRenderer.render(); "
        " gfx3FlareRenderer.render(); "
        " gfx3MeshRenderer.render(ts); "
        " gfx3SpriteRenderer.render(); "
        " gfx3ParticlesRenderer.render(); "
        " gfx3Manager.endPassRender(); "
        " gfx3PostRenderer.render(ts, gfx3Manager.getCurrentRenderingTexture()); "
        " gfx3Manager.endRender(); "
        "Dernière chose, ne lance jamais le projet. "
        "A présent, voici la demande de l'utilisateur: "
      )

      full_prompt = f"{pre_prompt} {prompt}"
      full_prompt_escaped = full_prompt.replace('"', '\\"')

      cmd = f'npx --yes auggie -w {bpy.path.abspath(context.scene.export_engine_path)} --print "{full_prompt}"'
      process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        shell=True, text=True, bufsize=1
      )

      for line in process.stdout:
        if txt:
          txt.write(line)
        #endif
        print(line.strip())
      #endfor

      process.wait()
      scene.auggie_status = "Terminé !" if process.returncode == 0 else "Erreur"

    except Exception as e:
      if txt: txt.write(f"\nERREUR: {str(e)}\n")
      scene.auggie_status = "Erreur"


class WARME_OT_run_server(bpy.types.Operator):
  bl_idname = "object.run_server"
  bl_label = "Run Server"

  def execute(self, context):
    try:
      subprocess.Popen(
        ["npm", "run", "dev"], 
        cwd=bpy.path.abspath(context.scene.export_engine_path), 
        shell=True
      )
      webbrowser.open("http://localhost:5173")
      context.scene.auggie_status = "Serveurs démarrés"
      self.report({'INFO'}, "Serveurs démarrés sur localhost:5173.")
    except Exception as e:
      print(f"Erreur lors du lancement de npm : {e}")
    #except
    return {'FINISHED'}


class WARME_OT_kill_server(bpy.types.Operator):
  bl_idname = "object.kill_server"
  bl_label = "Stop Server"

  def execute(self, context):
    try:
      if os.name == 'nt':  # Windows
        subprocess.run(['taskkill', '/F', '/IM', 'node.exe', '/T'], capture_output=True)
      else:  # Mac / Linux
        subprocess.run(['pkill', '-9', 'node'], capture_output=True)
      #endif

      context.scene.auggie_status = "Serveurs arrêtés"
      self.report({'INFO'}, "Tous les processus Node ont été coupés.")
    except Exception as e:
      self.report({'ERROR'}, f"Erreur lors du nettoyage : {str(e)}")
    #except
    return {'FINISHED'}


class WARME_OT_build_game(bpy.types.Operator):
  bl_idname = "object.build_game"
  bl_label = "Build Game"

  def execute(self, context):
    try:      
      process = subprocess.Popen(
        ["npm", "run", "build:tauri", "--", "--no-bundle"],
        cwd=bpy.path.abspath(context.scene.export_engine_path), 
        shell=True
      )

      context.scene.auggie_status = "En cours de construction..."
      process.wait()
      context.scene.auggie_status = "Binaire Terminé !" if process.returncode == 0 else "Erreur"
    except Exception as e:
      context.scene.auggie_status = "Erreur lors de la construction !"
      print(f"Erreur lors du lancement de npm : {e}")
    #except
    return {'FINISHED'}


class WARME_OT_run_game(bpy.types.Operator):
  bl_idname = "object.run_game"
  bl_label = "Run Game"

  def execute(self, context):
    base_path = bpy.path.abspath(context.scene.export_engine_path)    
    exe_name = "tauri-app.exe" 
    exe_path = os.path.join(base_path, "src-tauri", "target", "release", exe_name)

    if not os.path.exists(exe_path):
      self.report({'ERROR'}, f"Binaire non trouvé : {exe_path}")
      return {'CANCELLED'}
    #endif

    try:
      subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
      self.report({'INFO'}, "Jeu lancé !")
    except Exception as e:
      self.report({'ERROR'}, f"Erreur au lancement : {e}")
      return {'CANCELLED'}
    #except
    return {'FINISHED'}