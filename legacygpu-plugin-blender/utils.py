import bpy
import zipfile
import shutil
import bmesh
import struct
import os
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d
from pathlib import Path
# ----------------------------------------------------------------------------------


def get_xyz_transformed(vec, index):
  if index == 0:
    return round(vec[0], 4)
  elif index == 1:
    return round(vec[2], 4)
  elif index == 2:
    return round(-vec[1], 4)
  else:
    return 0


def get_utf8_file_descriptor(path, filename, extension):
  file = get_available_filename(path, filename, extension)
  with open(file, 'w', encoding='utf-8') as f:
    return f
  #endwith


def get_binary_file_descriptor(path, filename, extension):
  file = get_available_filename(path, filename, extension)
  with open(file, 'wb') as f:
    return f
  #endwith


def get_available_filename(path, filename, extension):
  if path == "":
    path = bpy.path.abspath("//")
  #endif

  file = Path(path + "/" + filename + "." + extension)
  return file


def zip_files(path_list, output_path):
  with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in path_list:
      zipf.write(file, os.path.basename(file))
    #endfor
  #endwith


def triangulate_mesh(obj):
  bpy.context.view_layer.objects.active = obj
  bpy.ops.object.mode_set(mode="EDIT")
  bm = bmesh.from_edit_mesh(obj.data)
  bmesh.ops.triangulate(bm, faces=bm.faces[:])
  bmesh.update_edit_mesh(obj.data)
  bpy.ops.object.mode_set(mode="OBJECT")


def destriangulate_mesh(mesh_obj):
  bpy.context.view_layer.objects.active = mesh_obj
  bpy.ops.object.mode_set(mode="EDIT")
  bpy.ops.mesh.select_all(action="SELECT")
  bpy.ops.mesh.tris_convert_to_quads()
  bpy.ops.object.mode_set(mode="OBJECT")


def get_object_matrix_converted_for_engine(obj):
  matrix = obj.matrix_world.to_4x4().transposed()
  tmp = matrix[0][1]; matrix[0][1] = matrix[0][2]; matrix[0][2] = -tmp
  tmp = matrix[1][1]; matrix[1][1] = matrix[1][2]; matrix[1][2] = -tmp
  tmp = matrix[2][1]; matrix[2][1] = matrix[2][2]; matrix[2][2] = -tmp
  tmp = matrix[3][1]; matrix[3][1] = matrix[3][2]; matrix[3][2] = -tmp
  return matrix


def get_position_of_object(obj):
  pos = obj.matrix_world.to_translation()
  return [
    get_xyz_transformed(pos, 0),
    get_xyz_transformed(pos, 1),
    get_xyz_transformed(pos, 2)
  ]


def get_rotation_of_camera(camera):
  camera_matrix = get_object_matrix_converted_for_engine(camera)
  rot = camera_matrix.to_euler('YXZ')
  return [rot.x, rot.y, rot.z]


def get_rotation_of_object(obj):
  rot = obj.matrix_world.to_euler('YXZ')
  return [-rot.x, -rot.z, -rot.y]


def get_scale_of_object(obj):
  scale = obj.matrix_world.to_scale()
  return [scale.x, scale.z, scale.y]


def draw_foldout(layout, props, attr, label, icon='NONE'):
  box = layout.box()
  row = box.row()
  row.prop(props, attr, 
          icon="TRIA_DOWN" if getattr(props, attr) else "TRIA_RIGHT",
          icon_only=True, emboss=False)
  row.label(text=label, icon=icon)
  return box, getattr(props, attr)


def draw_input_row(layout, props, attr, label, index=None):
  row = layout.row()
  row.label(text=label)

  if index is not None:
    row.prop(props, attr, text="", index=index)
  else:
    row.prop(props, attr, text="")


def draw_title_row(layout, title):
  row = layout.row()
  row.alignment = 'CENTER'
  row.label(text=title)


def get_or_create_collection(collection_name):
  if collection_name in bpy.data.collections:
    collection = bpy.data.collections[collection_name]
    return collection
  else:
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def unlink_from_all_collections(obj):
  for col in obj.users_collection[:]:
    col.objects.unlink(obj)
  #endfor


def belong_to_collection(obj, collection):
  for col in obj.users_collection[:]:
    if col.name == collection:
      return True
    #endif
  #endfor


def setup_tracking(sourceName, destinationName):
  source = bpy.data.objects.get(sourceName)
  destination = bpy.data.objects.get(destinationName)

  if source and destination:
    constraint_name = "AutoTrack"
    con = source.constraints.get(constraint_name)
    
    if not con:
      con = source.constraints.new(type='TRACK_TO')
      con.name = constraint_name
    #endif
    
    con.target = destination
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'


def sampler_export_json(selected_obj, path, filename):
  obj = {
    "Ident": "TEX",
  }

  # Fill json object
  obj["AddressModeU"] = selected_obj.mat_properties.sampler_address_mode_u
  obj["AddressModeV"] = selected_obj.mat_properties.sampler_address_mode_v
  obj["AddressModeW"] = selected_obj.mat_properties.sampler_address_mode_w
  obj["MagFilter"] = selected_obj.mat_properties.sampler_mag_filter
  obj["MinFilter"] = selected_obj.mat_properties.sampler_min_filter
  obj["MipMapFilter"] = selected_obj.mat_properties.sampler_mipmap_filter
  obj["LodMinClamp"] = selected_obj.mat_properties.sampler_lod_min_clamp
  obj["LodMaxClamp"] = selected_obj.mat_properties.sampler_lod_max_clamp
  obj["MaxAnisotropy"] = selected_obj.mat_properties.sampler_max_anisotropy
  obj["Type"] = selected_obj.mat_properties.sampler_type

  file = utils.get_available_filename(path, filename, 'tex')
  with open(file, 'w', encoding='utf-8') as f:
    json.dump(obj, f, ensure_ascii=False)
  #endwith


def copy_texture_file(path, path_list, properties):
  for key, value in properties.items():
    prop_def = properties.rna_type.properties.get(key)
    is_file = prop_def and prop_def.subtype == 'FILE_PATH'
    if value != "" and is_file:
      dest_path = path + bpy.path.basename(value)
      shutil.copyfile(bpy.path.abspath(value), dest_path)
      
      if dest_path not in path_list:
        path_list.append(dest_path)
      #endif
    #endif
  #endfor


def copy_sampler_file(path, path_list, obj, properties, sampler_enabled):
  for key, value in properties.items():
    prop_def = properties.rna_type.properties.get(key)
    is_file = prop_def and prop_def.subtype == 'FILE_PATH'

    if value != "" and is_file and sampler_enabled:
      filename_only = Path(value).stem
      dest_path = path + filename_only + '.tex'
      sampler_export_json(obj, path, filename_only)

      if dest_path not in path_list:
        path_list.append(dest_path)
      #endif
    #endif
  #endfor


def process_tween_vector(collection, prefix, obj_target):
  times = []
  values = []
  for item in collection:
    times.append(item.time)
    values.append(list(item.value))

  obj_target[f"{prefix}Times"] = list(times)
  obj_target[f"{prefix}Values"] = list(values)


def process_tween_number(collection, prefix, obj_target):
  times = []
  values = []
  for item in collection:
    times.append(item.time)
    values.append(item.value)
  
  obj_target[f"{prefix}Times"] = list(times)
  obj_target[f"{prefix}Values"] = list(values)


def write_string(f, s):
  """Utilitaire pour écrire une chaîne de caractères en binaire"""
  if s is None: s = ""
  # On encode en utf-8
  b_str = s.encode('utf-8')
  # On écrit la longueur (format 'i' pour int 4 octets) puis le contenu
  f.write(struct.pack('<i', len(b_str)))
  f.write(b_str)


def draw_grf_node_values(self, dummy_context):
  context = bpy.context
  obj = context.active_object
  
  if not obj or obj.type != 'MESH':
    return
  #if
  
  attr = obj.data.attributes.get("grf_node_type")
  if not attr or len(attr.data) == 0:
    return
  #if

  # Matrice et infos de région
  matrix = obj.matrix_world
  region = context.region
  rv3d = context.space_data.region_3d
  
  if not rv3d:
    return
  #if

  font_id = 0
  blf.size(font_id, 20)

  # Vérifier que l'index est valide
  num_verts = len(obj.data.vertices)
  if len(attr.data) != num_verts:
    return
  #if

  for i, v in enumerate(obj.data.vertices):
    if i >= len(attr.data):
      break
    #if
    
    val = attr.data[i].value.decode('utf-8')
    if val != 0:
      pos_3d = matrix @ v.co
      pos_2d = location_3d_to_region_2d(region, rv3d, pos_3d)
      
      if pos_2d:
        blf.color(font_id, 1.0, 1.0, 0.0, 1.0)
        blf.position(font_id, pos_2d.x + 10, pos_2d.y + 10, 0)
        blf.draw(font_id, str(val))
      #if
    #if
  #for