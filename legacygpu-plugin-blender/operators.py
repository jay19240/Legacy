import bpy
import os
import bmesh
from . import functions
from . import utils
# ----------------------------------------------------------------------------------

ATTR_NAME = "grf_node_id"
VISUAL_NAME = "GRF_Node_Visual"

GROUP_NAME = "GRF_Nodes"
ATTR_ID = "grf_node_id"

COLOR_ATTR_NAME = "GRF_Visual"

def register():
  bpy.utils.register_class(WARME_OT_export_pack)
  bpy.utils.register_class(WARME_OT_export_world_json)
  bpy.utils.register_class(WARME_OT_export_camera_json)
  bpy.utils.register_class(WARME_OT_export_objects)
  bpy.utils.register_class(WARME_OT_export_objects_as_wavefront)
  bpy.utils.register_class(WARME_OT_copy_object_matrix)
  bpy.utils.register_class(WARME_OT_copy_object_position) 
  bpy.utils.register_class(WARME_OT_copy_object_rotation)
  bpy.utils.register_class(WARME_OT_add_animation)
  bpy.utils.register_class(WARME_OT_remove_animation)
  bpy.utils.register_class(WARME_OT_material_add_animation)
  bpy.utils.register_class(WARME_OT_material_remove_animation)
  bpy.utils.register_class(WARME_OT_add_particles_tweens_color)
  bpy.utils.register_class(WARME_OT_remove_particles_tweens_color)
  bpy.utils.register_class(WARME_OT_add_particles_tweens_size)
  bpy.utils.register_class(WARME_OT_remove_particles_tweens_size)
  bpy.utils.register_class(WARME_OT_add_particles_tweens_opacity)
  bpy.utils.register_class(WARME_OT_remove_particles_tweens_opacity)
  bpy.utils.register_class(WARME_OT_add_particles_tweens_acceleration)
  bpy.utils.register_class(WARME_OT_remove_particles_tweens_acceleration)
  bpy.utils.register_class(WARME_OT_grf_apply_node_meta)


def unregister():
  bpy.utils.unregister_class(WARME_OT_export_pack)
  bpy.utils.unregister_class(WARME_OT_export_world_json)
  bpy.utils.unregister_class(WARME_OT_export_camera_json)
  bpy.utils.unregister_class(WARME_OT_export_objects)
  bpy.utils.unregister_class(WARME_OT_export_objects_as_wavefront)
  bpy.utils.unregister_class(WARME_OT_copy_object_matrix)
  bpy.utils.unregister_class(WARME_OT_copy_object_position) 
  bpy.utils.unregister_class(WARME_OT_copy_object_rotation)
  bpy.utils.unregister_class(WARME_OT_add_animation)
  bpy.utils.unregister_class(WARME_OT_remove_animation)
  bpy.utils.unregister_class(WARME_OT_material_add_animation)
  bpy.utils.unregister_class(WARME_OT_material_remove_animation)
  bpy.utils.unregister_class(WARME_OT_add_particles_tweens_color)
  bpy.utils.unregister_class(WARME_OT_remove_particles_tweens_color)
  bpy.utils.unregister_class(WARME_OT_add_particles_tweens_size)
  bpy.utils.unregister_class(WARME_OT_remove_particles_tweens_size)
  bpy.utils.unregister_class(WARME_OT_add_particles_tweens_opacity)
  bpy.utils.unregister_class(WARME_OT_remove_particles_tweens_opacity)
  bpy.utils.unregister_class(WARME_OT_add_particles_tweens_acceleration)
  bpy.utils.unregister_class(WARME_OT_remove_particles_tweens_acceleration)
  bpy.utils.unregister_class(WARME_OT_grf_apply_node_meta)


class WARME_OT_export_pack(bpy.types.Operator):
  """Export Pack""" 
  bl_idname = "object.export_pack"
  bl_label = "Export Scene"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    functions.pack(bpy.path.abspath(context.scene.export_assets_path), context)
    self.report({'INFO'}, "Export successful ✔")
    return {"FINISHED"}


class WARME_OT_export_world_json(bpy.types.Operator):
  """Export World""" 
  bl_idname = "object.export_world_json"
  bl_label = "World (JSON)"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    functions.world_export_json(bpy.path.abspath(context.scene.export_assets_path), "scene")
    self.report({'INFO'}, "Export successful ✔")
    return {"FINISHED"}


class WARME_OT_export_camera_json(bpy.types.Operator):
  """Export Camera""" 
  bl_idname = "object.export_camera_json"
  bl_label = "Camera (JSON)"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    functions.camera_export_json(bpy.path.abspath(context.scene.export_assets_path), "scene")
    self.report({'INFO'}, "Export successful ✔")
    return {"FINISHED"}


class WARME_OT_export_objects(bpy.types.Operator):
  """Export Objects""" 
  bl_idname = "object.export_objects"
  bl_label = "Selected Objects"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    for object in bpy.context.selected_objects:
      if (object.type == 'CAMERA'):
        functions.camera_export(bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
        continue
      #endif

      if (utils.belong_to_collection(object, "JSM")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jsm_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jsm_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        functions.mat_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JAM")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jam_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jam_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        functions.mat_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JWM")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jwm_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jwm_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JNM")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jnm_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jnm_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JSV")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jsv_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jsv_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JWA")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jwa_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jwa_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "GRF")):
        functions.grf_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JLM")):
        if (context.scene.world_properties.enable_export_has_binary):
          functions.jlm_export_binary(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        else:
          functions.jlm_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        #endif
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "JLT")):
        functions.jlt_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      # Special ------------------------------------------------------------------------------------------------------

      if (utils.belong_to_collection(object, "DCL")):
        functions.special_export_dcl_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "SKY")):
        functions.special_export_sky_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "PRT")):
        functions.special_export_prt_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif

      if (utils.belong_to_collection(object, "ENT")):
        functions.ent_export_json(object, bpy.path.abspath(context.scene.export_assets_path), object.name)
        self.report({'INFO'}, "Export successful ✔")
      #endif
    #endfor
    return {"FINISHED"}


class WARME_OT_export_objects_as_wavefront(bpy.types.Operator):
  """Export As Wavefront""" 
  bl_idname = "object.export_objects_as_wavefront"
  bl_label = "Selected Objects As Wavefront"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    scene_name = os.path.basename(bpy.data.filepath)
    functions.obj_export(bpy.path.abspath(context.scene.export_assets_path), scene_name)
    self.report({'INFO'}, "Export successful ✔")
    return {"FINISHED"}


class WARME_OT_add_animation(bpy.types.Operator):
  """Add animation""" 
  bl_idname = "object.add_animation"
  bl_label = "Add"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}
  
  def execute(self, context):
    temp = context.object.jam_animations[-1].end_frame if len(context.object.jam_animations) > 0 else 0
    item = context.object.jam_animations.add()
    item.start_frame = temp
    item.end_frame = temp
    return {"FINISHED"}


class WARME_OT_remove_animation(bpy.types.Operator):
  """Remove last animation""" 
  bl_idname = "object.remove_animation"
  bl_label = "Remove"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    context.object.jam_animations.remove(len(bpy.context.object.jam_animations) - 1)
    return {"FINISHED"}


class WARME_OT_copy_object_matrix(bpy.types.Operator):
  """Copy object matrix""" 
  bl_idname = "object.copy_object_matrix"
  bl_label = "Matrix"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    matrix = utils.get_object_matrix_converted_for_engine(bpy.context.object)
    matrix_string = f"{matrix[0][0]}, {matrix[0][1]}, {matrix[0][2]}, {matrix[0][3]}, {matrix[1][0]}, {matrix[1][1]}, {matrix[1][2]}, {matrix[1][3]}, {matrix[2][0]}, {matrix[2][1]}, {matrix[2][2]}, {matrix[2][3]}, {matrix[3][0]}, {matrix[3][1]}, {matrix[3][2]}, {matrix[3][3]}"
    context.window_manager.clipboard = matrix_string
    return {"FINISHED"}


class WARME_OT_copy_object_position(bpy.types.Operator):
  """Copy object position""" 
  bl_idname = "object.copy_object_position"
  bl_label = "Position"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    # Fetch selected object
    pos = utils.get_position_of_object(bpy.context.object)
    position_string = f"{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}"
    context.window_manager.clipboard = position_string
    return {'FINISHED'}


class WARME_OT_copy_object_rotation(bpy.types.Operator):
  """Copy object rotation""" 
  bl_idname = "object.copy_object_rotation"
  bl_label = "Rotation"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    # Fetch selected object
    rot = utils.get_rotation_of_object(bpy.context.object)
    rotation_string = f"{rot[0]:.4f}, {rot[1]:.4f}, {rot[2]:.4f}"
    context.window_manager.clipboard = rotation_string
    return {"FINISHED"}


class WARME_OT_material_add_animation(bpy.types.Operator):
  """Add animation""" 
  bl_idname = "object.material_add_animation"
  bl_label = "Add"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    item = context.object.material_animations.add()
    return {"FINISHED"}


class WARME_OT_material_remove_animation(bpy.types.Operator):
  """Remove last animation""" 
  bl_idname = "object.material_remove_animation"
  bl_label = "Remove"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    context.object.material_animations.remove(len(bpy.context.object.material_animations) - 1)
    return {"FINISHED"}


class WARME_OT_add_particles_tweens_color(bpy.types.Operator):
  """Add tween color""" 
  bl_idname = "object.add_particles_tweens_color"
  bl_label = "Add Color"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}
  
  def execute(self, context):
    item = context.object.particles_properties.tweens_color.add()
    return {"FINISHED"}


class WARME_OT_remove_particles_tweens_color(bpy.types.Operator):
  """Remove tween color""" 
  bl_idname = "object.remove_particles_tweens_color"
  bl_label = "Remove Color"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    context.object.particles_properties.tweens_color.remove(len(bpy.context.object.particles_properties.tweens_color) - 1)
    return {"FINISHED"}


class WARME_OT_add_particles_tweens_size(bpy.types.Operator):
  """Add tween size""" 
  bl_idname = "object.add_particles_tweens_size"
  bl_label = "Add Size"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}
  
  def execute(self, context):
    item = context.object.particles_properties.tweens_size.add()
    return {"FINISHED"}


class WARME_OT_remove_particles_tweens_size(bpy.types.Operator):
  """Remove tween size""" 
  bl_idname = "object.remove_particles_tweens_size"
  bl_label = "Remove Size"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    context.object.particles_properties.tweens_size.remove(len(bpy.context.object.particles_properties.tweens_size) - 1)
    return {"FINISHED"}


class WARME_OT_add_particles_tweens_opacity(bpy.types.Operator):
  """Add tween opacity""" 
  bl_idname = "object.add_particles_tweens_opacity"
  bl_label = "Add Opacity"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}
  
  def execute(self, context):
    item = context.object.particles_properties.tweens_opacity.add()
    return {"FINISHED"}


class WARME_OT_remove_particles_tweens_opacity(bpy.types.Operator):
  """Remove tween opacity""" 
  bl_idname = "object.remove_particles_tweens_opacity"
  bl_label = "Remove Opacity"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    context.object.particles_properties.tweens_opacity.remove(len(bpy.context.object.particles_properties.tweens_opacity) - 1)
    return {"FINISHED"}


class WARME_OT_add_particles_tweens_acceleration(bpy.types.Operator):
  """Add tween acceleration""" 
  bl_idname = "object.add_particles_tweens_acceleration"
  bl_label = "Add Acceleration"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}
  
  def execute(self, context):
    item = context.object.particles_properties.tweens_acceleration.add()
    return {"FINISHED"}


class WARME_OT_remove_particles_tweens_acceleration(bpy.types.Operator):
  """Remove tween acceleration""" 
  bl_idname = "object.remove_particles_tweens_acceleration"
  bl_label = "Remove Acceleration"
  bl_options = {'REGISTER', 'UNDO_GROUPED'}

  def execute(self, context):
    context.object.particles_properties.tweens_acceleration.remove(len(bpy.context.object.particles_properties.tweens_acceleration) - 1)
    return {"FINISHED"}


class WARME_OT_grf_apply_node_meta(bpy.types.Operator):
  """Applique l'ID aux sommets sélectionnés"""
  bl_idname = "mesh.grf_apply_node_meta"
  bl_label = "Assigner ID"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    obj = context.active_object
    if not obj or obj.type != 'MESH' or obj.mode != 'EDIT':
      return {'CANCELLED'}
    #if

    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    # 1. Gérer le type pour l'export
    layer_id = bm.verts.layers.string.get("grf_node_type") or bm.verts.layers.string.new("grf_node_type")
    val = context.scene.grf_node_type

    # Collecter les indices des vertices sélectionnés
    selected_indices = []
    for v in bm.verts:
      if v.select:
        v[layer_id] = val.encode('utf-8')
        selected_indices.append(v.index)
      #if
    #for
    
    bmesh.update_edit_mesh(mesh)
    
    # Passer en mode OBJECT pour créer/modifier l'attribut
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 2. Créer l'attribut de couleur sur le mesh
    if COLOR_ATTR_NAME not in mesh.attributes:
      mesh.attributes.new(name=COLOR_ATTR_NAME, type='FLOAT_COLOR', domain='POINT')
    #if
    
    # Assigner les couleurs
    color_attr = mesh.attributes[COLOR_ATTR_NAME]
    for idx in selected_indices:
      color_attr.data[idx].color = (1.0, 0.0, 0.0, 1.0)
    #for
    
    # Retourner en mode EDIT
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Forcer l'affichage des attributs
    if hasattr(context, 'space_data') and context.space_data:
      context.space_data.shading.color_type = 'VERTEX'
    #if
    
    return {'FINISHED'}