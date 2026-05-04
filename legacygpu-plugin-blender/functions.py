import bpy
import mathutils
import bmesh
import shutil
import json
import struct
import os
import sys
from . import utils
from pathlib import Path
from math import pi, atan, degrees
# ----------------------------------------------------------------------------------
INFINITY = sys.float_info.max

# ----------------------------------------------------------------------------------
# JAM
# ----------------------------------------------------------------------------------
def jam_export(selected_obj):
  obj = {
    "Ident": "JAM",
    "NumVertices": -1,
    "NumFrames": -1,
    "NumAnimations": -1,
    "Frames": [],
    "TextureCoords": [],
    "Animations": []
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch selected object
  dg = bpy.context.evaluated_depsgraph_get()

  # Go to start frame
  bpy.context.scene.frame_current = bpy.context.scene.frame_start

  # For each frame
  while bpy.context.scene.frame_current <= bpy.context.scene.frame_end:
    # Get current mesh data
    dg.update()
    obj_eval = selected_obj.evaluated_get(dg)
    mesh = obj_eval.to_mesh()
    mesh.transform(bpy.context.object.matrix_world)

    vertices = []
    normals = [] 

    # Vertices, Normals
    for tri in mesh.polygons:
      if len(tri.loop_indices) != 3: raise NameError('Object not triangulate !')
      for li in tri.loop_indices:
        vert = mesh.vertices[mesh.loops[li].vertex_index]
        vertices.append(utils.get_xyz_transformed(vert.co, 0))
        vertices.append(utils.get_xyz_transformed(vert.co, 1))
        vertices.append(utils.get_xyz_transformed(vert.co, 2))
        normals.append(utils.get_xyz_transformed(vert.normal, 0))
        normals.append(utils.get_xyz_transformed(vert.normal, 1))
        normals.append(utils.get_xyz_transformed(vert.normal, 2))
      #endfor
    #endfor

    # Append to obj
    obj["Frames"].append({"Vertices": vertices, "Normals": normals})
    bpy.context.scene.frame_current += 1
  #endwhile

  depsgraph = bpy.context.evaluated_depsgraph_get()
  depsgraph.update()
  obj_eval = selected_obj.evaluated_get(depsgraph)
  mesh = obj_eval.data

  # TextureCoords
  for tri in mesh.polygons:
    for li in tri.loop_indices:
      obj["TextureCoords"].append(round(mesh.uv_layers.active.data[li].uv[0], 4))
      obj["TextureCoords"].append(1 - round(mesh.uv_layers.active.data[li].uv[1], 4))
    #endfor
  #endfor

  # Animations
  for anim in selected_obj.jam_animations:
    obj["Animations"].append({ "Name": anim.name, "StartFrame": anim.start_frame, "EndFrame": anim.end_frame, "FrameDuration": anim.frame_duration })
  #endfor

  obj["NumVertices"] = int(len(obj["Frames"][0]["Vertices"]) / 3)
  obj["NumFrames"] = len(obj["Frames"])
  obj["NumAnimations"] = len(obj["Animations"])

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)
  return obj


def jam_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jam')
  data = jam_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


def jam_export_binary(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'bam')
  data = jam_export(selected_obj)

  with open(file, "wb") as f:
    header = struct.pack('<3i', data["NumVertices"], data["NumFrames"], data["NumAnimations"])
    f.write(header)

    for uv in data["TextureCoords"]:
      buf = struct.pack('<f', uv)
      f.write(buf)
    #endfor

    for frame in data["Frames"]:
      for vert in frame["Vertices"]:
        buf = struct.pack('<f', vert)
        f.write(buf)
      #endfor

      for norm in frame["Normals"]:
        buf = struct.pack('<f', norm)
        f.write(buf)
      #endfor
    #endfor

    for animation in data["Animations"]:
      namelen = struct.pack('<i', len(animation["Name"]))
      f.write(namelen)

      for char in animation["Name"]:
        c = struct.pack('<i', ord(char))
        f.write(c)
      #endfor

      buf = struct.pack('<3i', animation["StartFrame"], animation["EndFrame"], animation["FrameDuration"])
      f.write(buf)
    #endfor
  #endwith


# ----------------------------------------------------------------------------------
# JWM
# ----------------------------------------------------------------------------------
def jwm_export(selected_obj):
  obj = {
    "Ident": "JWM",
    "NumSectors": -1,
    "NumSectorColors": -1,
    "Min": [],
    "Max": [],
    "Sectors": [],
    "SectorColors": [],
    "NeighborPool": [],
    "SharedPool": []
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch selected object
  dg = bpy.context.evaluated_depsgraph_get()

  # Get current mesh data
  dg.update()
  obj_eval = selected_obj.evaluated_get(dg)
  mesh = obj_eval.to_mesh()
  mesh.transform(bpy.context.object.matrix_world)

  # Minimum and maximum base
  minimum = [INFINITY, INFINITY, INFINITY]
  maximum = [-INFINITY, -INFINITY, -INFINITY]

  # Sectors, SectorColors
  for tri in mesh.polygons:
    if len(tri.loop_indices) != 3: raise NameError('Object not triangulate !')
    sec = []
    col = []

    for li in tri.loop_indices:
      secVertex = []
      secVertexColor = []

      if (len(mesh.vertex_colors) > 0):
        secVertexColor.append(mesh.vertex_colors[0].data[li].color[0]) #r
        secVertexColor.append(mesh.vertex_colors[0].data[li].color[1]) #g
        secVertexColor.append(mesh.vertex_colors[0].data[li].color[2]) #b
      #endif

      vert = mesh.vertices[mesh.loops[li].vertex_index]

      for i in range(0, 3):
        v = utils.get_xyz_transformed(vert.co, i)
        minimum[i] = min(v, minimum[i])
        maximum[i] = max(v, maximum[i])
        secVertex.append(v)
      #endfor

      if (len(secVertex) > 0): sec.append(secVertex)
      if (len(secVertexColor) > 0): col.append(secVertexColor)
    #endfor

    if (len(sec) > 0): obj["Sectors"].append(sec)
    if (len(col) > 0): obj["SectorColors"].append(col[0] if (col[0] == col[1] and col[0] == col[2]) else [0.0, 0.0, 0.0])
  #endfor

  # NeighborPool, SharedPool
  for i in range(len(obj["Sectors"])):
    neighbors = [-1, -1, -1]
    shared = [i]

    for j in range(3):
      p1 = obj["Sectors"][i][j]
      p2 = obj["Sectors"][i][(j + 1) % 3]

      for k in range(len(obj["Sectors"])):
        if obj["Sectors"][k] == obj["Sectors"][i]: continue
        for l in range(3):
          p1prime = obj["Sectors"][k][l]
          p2prime = obj["Sectors"][k][(l + 1) % 3]
          neighbor_test1 = p1 == p1prime and p2 == p2prime
          neighbor_test2 = p1 == p2prime and p2 == p1prime
          if neighbor_test1 or neighbor_test2: neighbors[j] = k
          if p1 == p1prime and not k in shared: shared.append(k)
        #endfor
      #endfor
    #endfor

    obj["NeighborPool"].append(neighbors)
    obj["SharedPool"].append(shared)
  #endfor

  # NumSectors, NumSectorColors, Min, Max
  obj["NumSectors"] = len(obj["Sectors"]);
  obj["NumSectorColors"] = len(obj["SectorColors"])
  obj["Min"] = [minimum[0], minimum[2]]
  obj["Max"] = [maximum[0], maximum[2]]

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)

  return obj


def jwm_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jwm')
  data = jwm_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


def jwm_export_binary(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'bwm')
  data = jwm_export(selected_obj)

  with open(file, "wb") as f:
    header = struct.pack('<2f', data["NumSectors"], data["NumSectorColors"])
    f.write(header)

    min = struct.pack('<2f', data["Min"][0], data["Min"][1])
    f.write(min)

    max = struct.pack('<2f', data["Max"][0], data["Max"][1])
    f.write(max)

    for sec in data["Sectors"]:
      for i in range(0, 3):
        buf = struct.pack('<3f', sec[i][0], sec[i][1], sec[i][2])
        f.write(buf)
      #endfor
    #endfor

    for col in data["SectorColors"]:
      buf = struct.pack('<3f', col[0], col[1], col[2])
      f.write(buf)
    #endfor

    for neighbor in data["NeighborPool"]:
      buf = struct.pack('<3f', neighbor[0], neighbor[1], neighbor[2])
      f.write(buf)
    #endfor

    for shared in data["SharedPool"]:
      buf = struct.pack('<f', len(shared))
      f.write(buf);
      for index in shared:
        buf = struct.pack('<f', index)
        f.write(buf)
      #endfor
    #endfor
  #endwith


# ----------------------------------------------------------------------------------
# JNM
# ----------------------------------------------------------------------------------
def jnm_export(selected_obj):
  obj = {
    "Ident": "JNM",
    "NumFrags": -1,
    "NumFragColors": -1,
    "Min": [],
    "Max": [],
    "Frags": [],
    "FragColors": []
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch selected object
  dg = bpy.context.evaluated_depsgraph_get()

  # Get current mesh data
  dg.update()
  obj_eval = selected_obj.evaluated_get(dg)
  mesh = obj_eval.to_mesh()
  mesh.transform(bpy.context.object.matrix_world)

  # Minimum and maximum base
  minimum = [INFINITY, INFINITY, INFINITY]
  maximum = [-INFINITY, -INFINITY, -INFINITY]

  # Frags, FragColors
  for tri in mesh.polygons:
    if len(tri.loop_indices) != 3: raise NameError('Object not triangulate !')
    frag = []
    fcol = []

    for li in tri.loop_indices:
      fragVertex = []
      fragVertexColor = []

      if (len(mesh.vertex_colors) > 0):
        fragVertexColor.append(mesh.vertex_colors[0].data[li].color[0])
        fragVertexColor.append(mesh.vertex_colors[0].data[li].color[1])
        fragVertexColor.append(mesh.vertex_colors[0].data[li].color[2])
      #endif

      vert = mesh.vertices[mesh.loops[li].vertex_index]
      for i in range(0, 3):
        v = utils.get_xyz_transformed(vert.co, i)
        minimum[i] = min(v, minimum[i])
        maximum[i] = max(v, maximum[i])
        fragVertex.append(v)
      #endfor

      if (len(fragVertex) > 0): frag.append(fragVertex)
      if (len(fragVertexColor) > 0): fcol.append(fragVertexColor)
    #endfor

    if (len(frag) > 0): obj["Frags"].append(frag)
    if (len(fcol) > 0): obj["FragColors"].append(fcol[0] if (fcol[0] == fcol[1] and fcol[0] == fcol[2]) else [0.0, 0.0, 0.0])
  #endfor

  # NumFrags, NumFragColors, Min, Max
  obj["NumFrags"] = len(obj["Frags"])
  obj["NumFragColors"] = len(obj["FragColors"])
  obj["Min"] = minimum
  obj["Max"] = maximum

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)

  return obj


def jnm_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jnm')
  data = jnm_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


def jnm_export_binary(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'bnm')
  data = jnm_export(selected_obj)

  with open(file, "wb") as f:
    header = struct.pack('<2f', data["NumFrags"], data["NumFragColors"])
    f.write(header)

    min = struct.pack('<3f', data["Min"][0], data["Min"][1], data["Min"][2])
    f.write(min)

    max = struct.pack('<3f', data["Max"][0], data["Max"][1], data["Max"][2])
    f.write(max)

    for frag in data["Frags"]:
      for i in range(0, 3):
        buf = struct.pack('<3f', frag[i][0], frag[i][1], frag[i][2])
        f.write(buf)
      #endfor
    #endfor

    for col in data["FragColors"]:
      buf = struct.pack('<3f', col[0], col[1], col[2])
      f.write(buf)
    #endfor
  #endwith


# ----------------------------------------------------------------------------------
# JSM
# ----------------------------------------------------------------------------------
def jsm_export(selected_obj):
  obj = {
    "Ident": "JSM",
    "NumVertices": -1,
    "Vertices": [],
    "Colors": [],
    "Normals": [],
    "TextureCoords": []
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch selected object
  dg = bpy.context.evaluated_depsgraph_get()

  # Get current mesh data
  dg.update()
  obj_eval = selected_obj.evaluated_get(dg)
  mesh = obj_eval.to_mesh()
  mesh.transform(bpy.context.object.matrix_world)

  # Vertices, Normals, Colors
  for tri in mesh.polygons:
    if len(tri.loop_indices) != 3: raise NameError('Object not triangulate !')
    for li in tri.loop_indices:
      if (len(mesh.vertex_colors) > 0):
        obj["Colors"].append(mesh.vertex_colors[0].data[li].color[0])
        obj["Colors"].append(mesh.vertex_colors[0].data[li].color[1])
        obj["Colors"].append(mesh.vertex_colors[0].data[li].color[2])
      #endif

      vert = mesh.vertices[mesh.loops[li].vertex_index]
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 0))
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 1))
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 2))
      obj["Normals"].append(utils.get_xyz_transformed(vert.normal, 0))
      obj["Normals"].append(utils.get_xyz_transformed(vert.normal, 1))
      obj["Normals"].append(utils.get_xyz_transformed(vert.normal, 2))
    #endfor
  #endfor

  # TextureCoords
  for tri in mesh.polygons:
    for li in tri.loop_indices:
      obj["TextureCoords"].append(round(mesh.uv_layers.active.data[li].uv[0], 4))
      obj["TextureCoords"].append(1 - round(mesh.uv_layers.active.data[li].uv[1], 4))
    #endfor
  #endfor

  # NumVertices, NumTextureCoords, NumNormals, NumColors
  obj["NumVertices"] = int(len(obj["Vertices"]) / 3)
  obj["NumTextureCoords"] = int(len(obj["TextureCoords"]) / 2)
  obj["NumNormals"] = int(len(obj["Normals"]) / 3)
  obj["NumColors"] = int(len(obj["Colors"]) / 3)

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)

  return obj


def jsm_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jsm')
  data = jsm_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


def jsm_export_binary(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'bsm')
  data = jsm_export(selected_obj)

  with open(file, "wb") as f:
    header = struct.pack('<4i', data["NumVertices"], data["NumTextureCoords"], data["NumNormals"], data["NumColors"])
    f.write(header)

    for vert in data["Vertices"]:
      buf = struct.pack('<f', vert)
      f.write(buf)
    #endfor

    for uv in data["TextureCoords"]:
      buf = struct.pack('<f', uv)
      f.write(buf)
    #endfor

    for normal in data["Normals"]:
      buf = struct.pack('<f', normal)
      f.write(buf)
    #endfor

    for color in data["Colors"]:
      buf = struct.pack('<f', color)
      f.write(buf)
    #endfor
  #endwith


# ----------------------------------------------------------------------------------
# JLM
# ----------------------------------------------------------------------------------
def jlm_export(selected_obj):
  obj = {
    "Ident": "JLM",
    "NumPoints": -1,
    "Points": []
  }

  if selected_obj.type == 'CURVE':
    mw = selected_obj.matrix_world.copy()
    for spline in selected_obj.data.splines:
      for p in spline.points:
        co_world = mw @ mathutils.Vector([p.co.x, p.co.y, p.co.z])
        obj["Points"].append([
          utils.get_xyz_transformed(co_world, 0),
          utils.get_xyz_transformed(co_world, 1),
          utils.get_xyz_transformed(co_world, 2)
        ])
      #endfor
    #endfor
  elif selected_obj.type == 'MESH':
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    obj_eval = selected_obj.evaluated_get(dg)
    mesh = obj_eval.to_mesh()
    mesh.transform(bpy.context.object.matrix_world)

    for vertex in mesh.vertices:
      obj["Points"].append([
        utils.get_xyz_transformed(vertex.co, 0),
        utils.get_xyz_transformed(vertex.co, 1),
        utils.get_xyz_transformed(vertex.co, 2)
      ])
    #endfor
  # endif

  obj["NumPoints"] = len(obj["Points"])
  return obj


def jlm_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jlm')
  data = jlm_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


def jlm_export_binary(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'blm')
  data = jlm_export(selected_obj)

  with open(file, "wb") as f:
    for vert in data["Points"]:
      buf = struct.pack('<3f', vert[0], vert[1], vert[2])
      f.write(buf)
    #endfor
  #endwith


# ----------------------------------------------------------------------------------
# JSV
# ----------------------------------------------------------------------------------
def jsv_export(selected_obj):
  obj = {
    "Ident": "JSV",
    "NumVertices": -1,
    "Vertices": [],
    "Colors": []
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch selected object
  dg = bpy.context.evaluated_depsgraph_get()

  # Get current mesh data
  dg.update()
  obj_eval = selected_obj.evaluated_get(dg)
  mesh = obj_eval.to_mesh()
  mesh.transform(bpy.context.object.matrix_world)

  # Vertices, Colors
  for tri in mesh.polygons:
    if len(tri.loop_indices) != 3: raise NameError('Object not triangulate !')
    for li in tri.loop_indices:
      if (len(mesh.vertex_colors) == 0): raise NameError('Object is not colored !')
      color = mesh.vertex_colors[0].data[li].color
      vert = mesh.vertices[mesh.loops[li].vertex_index]
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 0))
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 1))
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 2))
      obj["Colors"].append(round(color[0], 4))
      obj["Colors"].append(round(color[1], 4))
      obj["Colors"].append(round(color[2], 4))
    #endfor
  #endfor

  # NumVertices
  obj["NumVertices"] = int(len(obj["Vertices"]) / 3)

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)

  return obj


def jsv_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jsv')
  data = jsv_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


def jsv_export_binary(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'bsv')
  data = jsv_export(selected_obj)

  with open(file, "wb") as f:
    header = struct.pack('<i', data["NumVertices"])
    f.write(header)

    for vert in data["Vertices"]:
      buf = struct.pack('<f', vert)
      f.write(buf)
    #endfor

    for color in data["Colors"]:
      buf = struct.pack('<f', color)
      f.write(buf)
    #endfor
  #endwith


# ----------------------------------------------------------------------------------
# JWA
# ----------------------------------------------------------------------------------
def jwa_export(selected_obj):
  obj = {
    "Ident": "JWA",
    "NumVertices": -1,
    "CustomParams": [],
    "Vertices": [],
    "TextureCoords": [],
    "Normals": [],
    "Colors": []    
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch selected object
  dg = bpy.context.evaluated_depsgraph_get()

  # Get current mesh data
  dg.update()
  obj_eval = selected_obj.evaluated_get(dg)
  mesh = obj_eval.to_mesh()
  mesh.transform(selected_obj.matrix_world)

  obj['WaveAmplitude'] = selected_obj.water_properties.wave_amplitude
  obj['WaveScale'] = selected_obj.water_properties.wave_scale
  obj['WaveSpeed'] = selected_obj.water_properties.wave_speed
  obj['WaveChoppiness'] = selected_obj.water_properties.wave_choppiness
  obj['WaveStepX'] = selected_obj.water_properties.wave_step_x
  obj['WaveStepZ'] = selected_obj.water_properties.wave_step_z
  obj['NormalMap'] = bpy.path.basename(selected_obj.water_properties.normal_map)
  obj['NormalMapScrollX'] = selected_obj.water_properties.normal_map_scroll_x
  obj['NormalMapScrollY'] = selected_obj.water_properties.normal_map_scroll_y
  obj['NormalMapIntensity'] = selected_obj.water_properties.normal_map_intensity
  obj['NormalMapScale'] = selected_obj.water_properties.normal_map_scale
  obj['SurfaceColorEnabled'] = selected_obj.water_properties.surface_color_enabled
  obj['SurfaceColorR'] = selected_obj.water_properties.surface_color[0]
  obj['SurfaceColorG'] = selected_obj.water_properties.surface_color[1]
  obj['SurfaceColorB'] = selected_obj.water_properties.surface_color[2]
  obj['SurfaceColorFactor'] = selected_obj.water_properties.surface_color_factor
  obj['EnvMapRight'] = bpy.path.basename(selected_obj.water_properties.optics_env_map_right)
  obj['EnvMapLeft'] = bpy.path.basename(selected_obj.water_properties.optics_env_map_left)
  obj['EnvMapTop'] = bpy.path.basename(selected_obj.water_properties.optics_env_map_top)
  obj['EnvMapBottom'] = bpy.path.basename(selected_obj.water_properties.optics_env_map_bottom)
  obj['EnvMapFront'] = bpy.path.basename(selected_obj.water_properties.optics_env_map_front)
  obj['EnvMapBack'] = bpy.path.basename(selected_obj.water_properties.optics_env_map_back)
  obj['EnvMapIntensity'] = selected_obj.water_properties.optics_env_intensity
  obj['FresnelPower'] = selected_obj.water_properties.optics_fresnel_power
  obj['FresnelBiais'] = selected_obj.water_properties.optics_fresnel_biais
  obj['SunEnabled'] = selected_obj.water_properties.sun_enabled
  obj['SunDirectionX'] = selected_obj.water_properties.sun_direction_x
  obj['SunDirectionY'] = selected_obj.water_properties.sun_direction_y
  obj['SunDirectionZ'] = selected_obj.water_properties.sun_direction_z
  obj['SunColorR'] = selected_obj.water_properties.sun_color[0]
  obj['SunColorG'] = selected_obj.water_properties.sun_color[1]
  obj['SunColorB'] = selected_obj.water_properties.sun_color[2]
  obj['SunColorFactor'] = selected_obj.water_properties.sun_color_factor

  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s00_name, "Value": selected_obj.water_properties.s00_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s01_name, "Value": selected_obj.water_properties.s01_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s02_name, "Value": selected_obj.water_properties.s02_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s03_name, "Value": selected_obj.water_properties.s03_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s04_name, "Value": selected_obj.water_properties.s04_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s05_name, "Value": selected_obj.water_properties.s05_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s06_name, "Value": selected_obj.water_properties.s06_value })
  obj["CustomParams"].append({ "Name": selected_obj.water_properties.s07_name, "Value": selected_obj.water_properties.s07_value })

  obj["S0Texture"] = bpy.path.basename(selected_obj.water_properties.s0_texture)
  obj["S1Texture"] = bpy.path.basename(selected_obj.water_properties.s1_texture)

  # Vertices, Colors
  for tri in mesh.polygons:
    if len(tri.loop_indices) != 3: raise NameError('Object not triangulate !')
    for li in tri.loop_indices:
      if (len(mesh.vertex_colors) == 0): raise NameError('Object is not colored !')
      color = mesh.vertex_colors[0].data[li].color
      vert = mesh.vertices[mesh.loops[li].vertex_index]
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 0))
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 1))
      obj["Vertices"].append(utils.get_xyz_transformed(vert.co, 2))
      obj["TextureCoords"].append(round(mesh.uv_layers.active.data[li].uv[0], 4))
      obj["TextureCoords"].append(1 - round(mesh.uv_layers.active.data[li].uv[1], 4))
      obj["Colors"].append(round(color[0], 4))
      obj["Colors"].append(round(color[1], 4))
      obj["Colors"].append(round(color[2], 4))
    #endfor
  #endfor

  # NumVertices
  obj["NumVertices"] = int(len(obj["Vertices"]) / 3)

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)

  return obj


def jwa_export_json(selected_obj, path, filename):
  resources_files = []
  file = utils.get_available_filename(path, filename, 'jwa')
  data = jwa_export(selected_obj)
  utils.copy_texture_file(path, resources_files, selected_obj.water_properties)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith
  return resources_files


def jwa_export_binary(selected_obj, path, filename):
  resources_files = []
  file = utils.get_available_filename(path, filename, 'bwa')
  data = jwa_export(selected_obj)
  utils.copy_texture_file(path, resources_files, selected_obj.water_properties)

  with open(file, "wb") as f:
    f.write(struct.pack('<27f',
      data["NumVertices"],
      data['WaveAmplitude'],
      data['WaveScale'],
      data['WaveSpeed'],
      data['WaveChoppiness'],
      data['WaveStepX'],
      data['WaveStepZ'],
      data['NormalMapScrollX'],
      data['NormalMapScrollY'],
      data['NormalMapIntensity'],
      data['NormalMapScale'],
      data['SurfaceColorEnabled'],
      data['SurfaceColorR'],
      data['SurfaceColorG'],
      data['SurfaceColorB'],
      data['SurfaceColorFactor'],
      data['EnvMapIntensity'],
      data['FresnelPower'],
      data['FresnelBiais'],
      data['SunEnabled'],
      data['SunDirectionX'],
      data['SunDirectionY'],
      data['SunDirectionZ'],
      data['SunColorR'],
      data['SunColorG'],
      data['SunColorB'],
      data['SunColorFactor']
    ))

    utils.write_string(f, data['NormalMap'])
    utils.write_string(f, data['EnvMapRight'])
    utils.write_string(f, data['EnvMapLeft'])
    utils.write_string(f, data['EnvMapTop'])
    utils.write_string(f, data['EnvMapBottom'])
    utils.write_string(f, data['EnvMapFront'])
    utils.write_string(f, data['EnvMapBack'])

    for param in data["CustomParams"]:
      utils.write_string(f, param['Name'])
      utils.write_string(f, param['Value'])
    #endfor

    utils.write_string(f, data['S0Texture'])
    utils.write_string(f, data['S1Texture'])

    for vert in data["Vertices"]:
      buf = struct.pack('<f', vert)
      f.write(buf)
    #endfor

    for uv in data["TextureCoords"]:
      buf = struct.pack('<f', uv)
      f.write(buf)
    #endfor

    for color in data["Colors"]:
      buf = struct.pack('<f', color)
      f.write(buf)
    #endfor
  #endwith
  return resources_files


# ----------------------------------------------------------------------------------
# JLT
# ----------------------------------------------------------------------------------
def jlt_export(selected_obj):
  obj = {
    "Ident": "JLT",
    "Type": "POINT",
    "PositionX": 0,
    "PositionY": 0,
    "PositionZ": 0,
    "DiffuseColorR": 0,
    "DiffuseColorG": 0,
    "DiffuseColorB": 0,
    "SpecularColorR": 0,
    "SpecularColorG": 0,
    "SpecularColorB": 0,
    "Intensity": -1,
    "Constant": 1,
    "Linear": 0,
    "Exp": 0,
    "GroupId": 0,
    "SpotCutoff": 0,
    "SpotDirectionX": 0,    
    "SpotDirectionY": -1,    
    "SpotDirectionZ": 0
  }

  # Check for valid object
  if (selected_obj.type != 'LIGHT'): raise NameError('Object is not a light')

  # Check for valid light and fill the type
  if selected_obj.data.type == 'POINT': obj["Type"] = "POINT"
  elif selected_obj.data.type == 'SPOT': obj["Type"] = "SPOT"
  else: raise NameError('Object is not a valid light')

  local_dir = Vector((0, 0, -1))
  world_dir = selected_obj.matrix_world.to_3x3() @ local_dir
  world_dir.normalize()

  # Fill json object
  obj["PositionX"] = utils.get_xyz_transformed(selected_obj.location, 0)
  obj["PositionY"] = utils.get_xyz_transformed(selected_obj.location, 1)
  obj["PositionZ"] = utils.get_xyz_transformed(selected_obj.location, 2)
  obj["DiffuseColorR"] = selected_obj.light_properties.diffuse.r
  obj["DiffuseColorG"] = selected_obj.light_properties.diffuse.g
  obj["DiffuseColorB"] = selected_obj.light_properties.diffuse.b
  obj["SpecularColorR"] = selected_obj.light_properties.specular.r
  obj["SpecularColorG"] = selected_obj.light_properties.specular.g
  obj["SpecularColorB"] = selected_obj.light_properties.specular.b
  obj["Intensity"] = selected_obj.light_properties.intensity
  obj["Constant"] = selected_obj.light_properties.constant
  obj["Linear"] = selected_obj.light_properties.linear
  obj["Exp"] = selected_obj.light_properties.exp
  obj["GroupId"] = selected_obj.light_properties.group
  obj["SpotCutoff"] = selected_obj.light_properties.spot_cutoff_angle
  obj["SpotDirectionX"] = utils.get_xyz_transformed(world_dir, 0)
  obj["SpotDirectionY"] = utils.get_xyz_transformed(world_dir, 1)
  obj["SpotDirectionZ"] = utils.get_xyz_transformed(world_dir, 2)

  # Fill json custom props
  for k, v in selected_obj.items():
    obj[k] = v
  #endfor
  return obj


def jlt_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'jlt')
  data = jlt_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


# ----------------------------------------------------------------------------------
# GRF
# ----------------------------------------------------------------------------------
def grf_export(selected_obj):
  obj = {
    "Ident": "GRF",
    "Nodes": {},
    "Groups": {}
  }

  # Triangulate selected object
  utils.triangulate_mesh(selected_obj)

  # Fetch mesh data
  world_matrix = selected_obj.matrix_world
  bm = bmesh.new()
  bm.from_mesh(selected_obj.data)

  # create vertex group lookup dictionary for names
  vgroup_names = {vgroup.index: vgroup.name for vgroup in selected_obj.vertex_groups}

  # create dictionary of vertex group assignments per vertex
  vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in selected_obj.data.vertices}

  node_type_layer = bm.verts.layers.string.get("grf_node_type")

  # build the graph
  for vert in bm.verts:
    world_coords = world_matrix @ vert.co
    x = utils.get_xyz_transformed(world_coords, 0)
    y = utils.get_xyz_transformed(world_coords, 1)
    z = utils.get_xyz_transformed(world_coords, 2)
    obj["Nodes"][vert.index] = {}
    obj["Nodes"][vert.index]["Pos"] = [x, y, z]
    obj["Nodes"][vert.index]["G"] = 0
    obj["Nodes"][vert.index]["H"] = 0
    obj["Nodes"][vert.index]["F"] = 0
    obj["Nodes"][vert.index]["Children"] = []

    if node_type_layer:
      obj["Nodes"][vert.index]["Type"] = vert[node_type_layer].decode('utf-8')
    else:
      obj["Nodes"][vert.index]["Type"] = 0
    #if

    for e in vert.link_edges:
      v_other = e.other_vert(vert)
      if (v_other.index in obj["Nodes"] and 'NOBACK' in vgroups[vert.index]): continue
      obj['Nodes'][vert.index]['Children'].append(v_other.index)
    #endfor
  #endfor

  # fill groups
  obj["Groups"] = vgroups

  # Destriangulate selected object
  utils.destriangulate_mesh(selected_obj)

  return obj


def grf_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'grf')
  data = grf_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


# ----------------------------------------------------------------------------------
# MAT
# ----------------------------------------------------------------------------------
def mat_export(selected_obj):
  obj = {
    "Ident": "MAT",
    "Flipbooks": [],
    "CustomParams": []
  }

  # Fill json object
  obj["Id"] = selected_obj.mat_properties.id
  obj["Opacity"] = selected_obj.mat_properties.opacity
  # ----------------------------------------------------------------------------------
  obj["ShadowEnabled"] = selected_obj.mat_properties.shadow_enabled
  obj["ShadowCasting"] = selected_obj.mat_properties.shadow_casting
  # ----------------------------------------------------------------------------------
  obj["DecalEnabled"] = selected_obj.mat_properties.decal_enabled
  obj["DecalGroup"] = selected_obj.mat_properties.decal_group
  # ----------------------------------------------------------------------------------
  obj["LightEnabled"] = selected_obj.mat_properties.light_enabled
  obj["LightGroup"] = selected_obj.mat_properties.light_group
  obj["LightGouraudShadingEnabled"] = selected_obj.mat_properties.light_gouraud_shading_enabled
  obj["LightEmissiveFactor"] = selected_obj.mat_properties.light_emissive_factor
  obj["LightEmissiveR"] = selected_obj.mat_properties.light_emissive_color[0]
  obj["LightEmissiveG"] = selected_obj.mat_properties.light_emissive_color[1]
  obj["LightEmissiveB"] = selected_obj.mat_properties.light_emissive_color[2]
  obj["LightAmbientR"] = selected_obj.mat_properties.light_ambient_color[0]
  obj["LightAmbientG"] = selected_obj.mat_properties.light_ambient_color[1]
  obj["LightAmbientB"] = selected_obj.mat_properties.light_ambient_color[2]
  obj["LightDiffuseR"] = selected_obj.mat_properties.light_diffuse_color[0]
  obj["LightDiffuseG"] = selected_obj.mat_properties.light_diffuse_color[1]
  obj["LightDiffuseB"] = selected_obj.mat_properties.light_diffuse_color[2]
  obj["LightSpecularFactor"] = selected_obj.mat_properties.light_specular_factor
  obj["LightSpecularR"] = selected_obj.mat_properties.light_specular_color[0]
  obj["LightSpecularG"] = selected_obj.mat_properties.light_specular_color[1]
  obj["LightSpecularB"] = selected_obj.mat_properties.light_specular_color[2]
  # ----------------------------------------------------------------------------------
  obj["Texture"] = bpy.path.basename(selected_obj.mat_properties.texture)
  obj["TextureScrollAngle"] = selected_obj.mat_properties.texture_scroll_angle
  obj["TextureScrollRate"] = selected_obj.mat_properties.texture_scroll_rate
  obj["TextureOffsetX"] = selected_obj.mat_properties.texture_offset[0]
  obj["TextureOffsetY"] = selected_obj.mat_properties.texture_offset[1]
  obj["TextureScaleX"] = selected_obj.mat_properties.texture_scale[0]
  obj["TextureScaleY"] = selected_obj.mat_properties.texture_scale[1]
  obj["TextureRotationAngle"] = selected_obj.mat_properties.texture_rotation_angle
  obj["TextureOpacity"] = selected_obj.mat_properties.texture_opacity
  obj["TextureBlendColorR"] = selected_obj.mat_properties.texture_blend_color[0]
  obj["TextureBlendColorG"] = selected_obj.mat_properties.texture_blend_color[1]
  obj["TextureBlendColorB"] = selected_obj.mat_properties.texture_blend_color[2]
  obj["TextureBlendColorMode"] = selected_obj.mat_properties.texture_blend_color_mode
  obj["TextureBlendColorMix"] = selected_obj.mat_properties.texture_blend_color_mix
  # ----------------------------------------------------------------------------------
  obj["SecondaryTexture"] = bpy.path.basename(selected_obj.mat_properties.secondary_texture)
  obj["SecondaryTextureScrollAngle"] = selected_obj.mat_properties.secondary_texture_scroll_angle
  obj["SecondaryTextureScrollRate"] = selected_obj.mat_properties.secondary_texture_scroll_rate
  obj["SecondaryTextureOffsetX"] = selected_obj.mat_properties.secondary_texture_offset[0]
  obj["SecondaryTextureOffsetY"] = selected_obj.mat_properties.secondary_texture_offset[1]
  obj["SecondaryTextureScaleX"] = selected_obj.mat_properties.secondary_texture_scale[0]
  obj["SecondaryTextureScaleY"] = selected_obj.mat_properties.secondary_texture_scale[1]
  obj["SecondaryTextureRotationAngle"] = selected_obj.mat_properties.secondary_texture_rotation_angle
  obj["SecondaryTextureOpacity"] = selected_obj.mat_properties.secondary_texture_opacity
  obj["SecondaryTextureBlendMode"] = selected_obj.mat_properties.secondary_texture_blend_mode
  obj["SecondaryTextureBlendColorR"] = selected_obj.mat_properties.secondary_texture_blend_color[0]
  obj["SecondaryTextureBlendColorG"] = selected_obj.mat_properties.secondary_texture_blend_color[1]
  obj["SecondaryTextureBlendColorB"] = selected_obj.mat_properties.secondary_texture_blend_color[2]
  obj["SecondaryTextureBlendColorMode"] = selected_obj.mat_properties.secondary_texture_blend_color_mode
  obj["SecondaryTextureBlendColorMix"] = selected_obj.mat_properties.secondary_texture_blend_color_mix
  # ----------------------------------------------------------------------------------
  obj["EnvMapName"] = bpy.path.basename(selected_obj.mat_properties.env_map_name)
  obj["EnvMapRight"] = bpy.path.basename(selected_obj.mat_properties.env_map_right)
  obj["EnvMapLeft"] = bpy.path.basename(selected_obj.mat_properties.env_map_left)
  obj["EnvMapTop"] = bpy.path.basename(selected_obj.mat_properties.env_map_top)
  obj["EnvMapBottom"] = bpy.path.basename(selected_obj.mat_properties.env_map_bottom)
  obj["EnvMapFront"] = bpy.path.basename(selected_obj.mat_properties.env_map_front)
  obj["EnvMapBack"] = bpy.path.basename(selected_obj.mat_properties.env_map_back)
  obj["EnvMapOpacity"] = selected_obj.mat_properties.env_map_opacity
  # ----------------------------------------------------------------------------------
  obj["NormalMap"] = bpy.path.basename(selected_obj.mat_properties.normal_map)
  obj["NormalMapScrollAngle"] = selected_obj.mat_properties.normal_map_scroll_angle
  obj["NormalMapScrollRate"] = selected_obj.mat_properties.normal_map_scroll_rate
  obj["NormalMapOffsetX"] = selected_obj.mat_properties.normal_map_offset[0]
  obj["NormalMapOffsetY"] = selected_obj.mat_properties.normal_map_offset[1]
  obj["NormalMapScaleX"] = selected_obj.mat_properties.normal_map_scale[0]
  obj["NormalMapScaleY"] = selected_obj.mat_properties.normal_map_scale[1]
  obj["NormalMapRotationAngle"] = selected_obj.mat_properties.normal_map_rotation_angle
  obj["NormalMapIntensity"] = selected_obj.mat_properties.normal_map_intensity
  # ----------------------------------------------------------------------------------
  obj["DisplacementMap"] = bpy.path.basename(selected_obj.mat_properties.displacement_map)
  obj["DisplacementMapScrollAngle"] = selected_obj.mat_properties.displacement_map_scroll_angle
  obj["DisplacementMapScrollRate"] = selected_obj.mat_properties.displacement_map_scroll_rate
  obj["DisplacementMapOffsetX"] = selected_obj.mat_properties.displacement_map_offset[0]
  obj["DisplacementMapOffsetY"] = selected_obj.mat_properties.displacement_map_offset[1]
  obj["DisplacementMapScaleX"] = selected_obj.mat_properties.displacement_map_scale[0]
  obj["DisplacementMapScaleY"] = selected_obj.mat_properties.displacement_map_scale[1]
  obj["DisplacementMapRotationAngle"] = selected_obj.mat_properties.displacement_map_rotation_angle
  obj["DisplacementMapFactor"] = selected_obj.mat_properties.displacement_map_factor
  obj["DisplaceTextureEnabled"] = selected_obj.mat_properties.displace_texture
  obj["DisplaceSecondaryTextureEnabled"] = selected_obj.mat_properties.displace_secondary_texture
  obj["DisplaceNormalMapEnabled"] = selected_obj.mat_properties.displace_normal_map
  obj["DisplaceDissolveMapEnabled"] = selected_obj.mat_properties.displace_dissolve_map
  obj["DisplaceEnvMapEnabled"] = selected_obj.mat_properties.displace_env_map
  # ----------------------------------------------------------------------------------
  obj["DissolveMap"] = bpy.path.basename(selected_obj.mat_properties.dissolve_map)
  obj["DissolveMapScrollAngle"] = selected_obj.mat_properties.dissolve_map_scroll_angle
  obj["DissolveMapScrollRate"] = selected_obj.mat_properties.dissolve_map_scroll_rate
  obj["DissolveMapOffsetX"] = selected_obj.mat_properties.dissolve_map_offset[0]
  obj["DissolveMapOffsetY"] = selected_obj.mat_properties.dissolve_map_offset[1]
  obj["DissolveMapScaleX"] = selected_obj.mat_properties.dissolve_map_scale[0]
  obj["DissolveMapScaleY"] = selected_obj.mat_properties.dissolve_map_scale[1]
  obj["DissolveMapRotationAngle"] = selected_obj.mat_properties.dissolve_map_rotation_angle
  obj["DissolveGlowR"] = selected_obj.mat_properties.dissolve_glow[0]
  obj["DissolveGlowG"] = selected_obj.mat_properties.dissolve_glow[1]
  obj["DissolveGlowB"] = selected_obj.mat_properties.dissolve_glow[2]
  obj["DissolveGlowRange"] = selected_obj.mat_properties.dissolve_glow_range
  obj["DissolveGlowFalloff"] = selected_obj.mat_properties.dissolve_glow_falloff
  obj["DissolveAmount"] = selected_obj.mat_properties.dissolve_amount
  # ----------------------------------------------------------------------------------
  obj["JitterVertexEnabled"] = selected_obj.mat_properties.jitter_vertex_enabled
  obj["JitterVertexLevel"] = selected_obj.mat_properties.jitter_vertex_level
  # ----------------------------------------------------------------------------------
  obj["ToonMap"] = bpy.path.basename(selected_obj.mat_properties.toon_map)
  obj["ToonMapOpacity"] = selected_obj.mat_properties.toon_map_opacity
  obj["ToonLightDirX"] = selected_obj.mat_properties.toon_light_dir[0]
  obj["ToonLightDirY"] = selected_obj.mat_properties.toon_light_dir[1]
  obj["ToonLightDirZ"] = selected_obj.mat_properties.toon_light_dir[2]
  # ----------------------------------------------------------------------------------
  obj["AlphaBlendEnabled"] = selected_obj.mat_properties.alpha_blend_enabled
  obj["AlphaBlendFacing"] = selected_obj.mat_properties.alpha_blend_facing
  obj["AlphaBlendDistance"] = selected_obj.mat_properties.alpha_blend_distance
  # ----------------------------------------------------------------------------------
  obj["ArcadeEnabled"] = selected_obj.mat_properties.arcade_enabled
  obj["ArcadeStartColorR"] = selected_obj.mat_properties.arcade_start_color[0]
  obj["ArcadeStartColorG"] = selected_obj.mat_properties.arcade_start_color[1]
  obj["ArcadeStartColorB"] = selected_obj.mat_properties.arcade_start_color[2]
  obj["ArcadeEndColorR"] = selected_obj.mat_properties.arcade_end_color[0]
  obj["ArcadeEndColorG"] = selected_obj.mat_properties.arcade_end_color[1]
  obj["ArcadeEndColorB"] = selected_obj.mat_properties.arcade_end_color[2]
  obj["ArcadeSharpColorR"] = selected_obj.mat_properties.arcade_sharp_color[0]
  obj["ArcadeSharpColorG"] = selected_obj.mat_properties.arcade_sharp_color[1]
  obj["ArcadeSharpColorB"] = selected_obj.mat_properties.arcade_sharp_color[2]
  # ----------------------------------------------------------------------------------
  obj["EmissiveMap"] = bpy.path.basename(selected_obj.mat_properties.emissive_map)
  # ----------------------------------------------------------------------------------
  obj["DiffuseMap"] = bpy.path.basename(selected_obj.mat_properties.diffuse_map)
  # ----------------------------------------------------------------------------------
  obj["SpecularMap"] = bpy.path.basename(selected_obj.mat_properties.specular_map)
  # ----------------------------------------------------------------------------------
  obj["ThuneMap"] = bpy.path.basename(selected_obj.mat_properties.thune_map)
  obj["ThuneMapShininessEnabled"] = selected_obj.mat_properties.thune_map_shininess_enabled
  obj["ThuneMapArcadeEnabled"] = selected_obj.mat_properties.thune_map_arcade_enabled
  obj["ThuneMapReflectiveEnabled"] = selected_obj.mat_properties.thune_map_reflective_enabled

  # Flipbooks
  for anim in selected_obj.material_animations:
    obj["Flipbooks"].append({
      "TextureTarget": anim.texture_target,
      "FrameWidth": anim.frame_width,
      "FrameHeight": anim.frame_height,
      "NumCol": anim.num_col,
      "NumRow": anim.num_row,
      "NumFrames": anim.num_frames,
      "FrameDuration": anim.frame_duration
    })
  #endfor

  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s00_name, "Value": selected_obj.mat_properties.s00_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s01_name, "Value": selected_obj.mat_properties.s01_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s02_name, "Value": selected_obj.mat_properties.s02_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s03_name, "Value": selected_obj.mat_properties.s03_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s04_name, "Value": selected_obj.mat_properties.s04_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s05_name, "Value": selected_obj.mat_properties.s05_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s06_name, "Value": selected_obj.mat_properties.s06_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s07_name, "Value": selected_obj.mat_properties.s07_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s08_name, "Value": selected_obj.mat_properties.s08_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s09_name, "Value": selected_obj.mat_properties.s09_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s10_name, "Value": selected_obj.mat_properties.s10_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s11_name, "Value": selected_obj.mat_properties.s11_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s12_name, "Value": selected_obj.mat_properties.s12_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s13_name, "Value": selected_obj.mat_properties.s13_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s14_name, "Value": selected_obj.mat_properties.s14_value })
  obj["CustomParams"].append({ "Name": selected_obj.mat_properties.s15_name, "Value": selected_obj.mat_properties.s15_value })

  obj["S0Texture"] = bpy.path.basename(selected_obj.mat_properties.s0_texture)
  obj["S1Texture"] = bpy.path.basename(selected_obj.mat_properties.s1_texture)
  return obj


def mat_export_json(selected_obj, path, filename):
  resources_files = []
  file = utils.get_available_filename(path, filename, 'mat')
  data = mat_export(selected_obj)
  utils.copy_texture_file(path, resources_files, selected_obj.mat_properties)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith
  return resources_files


# ----------------------------------------------------------------------------------
# OBJ
# ----------------------------------------------------------------------------------
def obj_export(path, name):
  FORWARD_AXIS = '-Z'
  UP_AXIS = 'Y'

  filepath = os.path.join(path, name + ".obj")
  bpy.ops.wm.obj_export(
    filepath=filepath,
    export_selected_objects=True,
    forward_axis=FORWARD_AXIS,
    up_axis=UP_AXIS,
    export_uv=True,
    export_normals=True,
    export_smooth_groups=True,
    export_materials=True,
    export_triangulated_mesh=True,
    global_scale=1.0
  )


# ----------------------------------------------------------------------------------
# CAMERA
# ----------------------------------------------------------------------------------
def camera_export_json(path, filename):
  obj = {
    "Ident": "CAM"
  }

  camera = bpy.data.objects["Camera"]
  pos = utils.get_position_of_object(camera)
  rot = utils.get_rotation_of_camera(camera)
  matrix = utils.get_object_matrix_converted_for_engine(camera)  
  fovy = camera.data.angle_y

  if camera.data.sensor_fit == 'VERTICAL':
    # FOV vertical affiché
    fovy = 2 * atan((camera.data.sensor_height * 0.5) / camera.data.lens)
  else:
    # FOV horizontal affiché (cas par défaut)
    fovy = 2 * atan((camera.data.sensor_width * 0.5) / camera.data.lens)

  # Fill json object
  obj["ProjectionMode"] = "PERSPECTIVE" if camera.data.type == 'PERSP' else "ORTHOGRAPHIC"
  obj["PositionX"] = pos[0]
  obj["PositionY"] = pos[1]
  obj["PositionZ"] = pos[2]
  obj["RotationX"] = rot[0]
  obj["RotationY"] = rot[1]
  obj["RotationZ"] = rot[2]
  obj["PerspectiveFovy"] = fovy
  obj["PerspectiveNear"] = camera.data.clip_start
  obj["PerspectiveFar"] = camera.data.clip_end
  obj["OrthographicSize"] = camera.data.ortho_scale
  obj["ClipOffsetX"] = bpy.context.scene.world_properties.camera_clip_offset[0]
  obj["ClipOffsetY"] = bpy.context.scene.world_properties.camera_clip_offset[1]
  obj["MinClipOffsetX"] = bpy.context.scene.world_properties.camera_min_clip_offset[0]
  obj["MinClipOffsetY"] = bpy.context.scene.world_properties.camera_min_clip_offset[1]
  obj["MaxClipOffsetX"] = bpy.context.scene.world_properties.camera_max_clip_offset[0]
  obj["MaxClipOffsetY"] = bpy.context.scene.world_properties.camera_max_clip_offset[1]

  if bpy.context.scene.world_properties.camera_matrix_export_enabled:
    obj["CameraMatrix"] = [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3], matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3], matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3], matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]

  file = utils.get_available_filename(path, filename, 'cam')
  with open(file, 'w', encoding='utf-8') as f:
    json.dump(obj, f, ensure_ascii=False)
  #endwith


# ----------------------------------------------------------------------------------
# WORLD
# ----------------------------------------------------------------------------------
def world_export_json(path, filename):
  obj = {
    "Ident": "WRD"
  }

  # Fill json object
  # ----------------------------------------------------------------------------------
  if "Sun" in bpy.data.objects:
    sun = bpy.data.objects["Sun"]
    rot_matrix = sun.matrix_world.to_3x3().normalized()
    obj["SunEnabled"] = True
    obj["SunDirectionX"] = utils.get_xyz_transformed(rot_matrix.col[2], 0)
    obj["SunDirectionY"] = utils.get_xyz_transformed(rot_matrix.col[2], 1)
    obj["SunDirectionZ"] = utils.get_xyz_transformed(rot_matrix.col[2], 2)
    obj["SunDiffuseColorR"] = sun.sun_properties.diffuse[0]
    obj["SunDiffuseColorG"] = sun.sun_properties.diffuse[1]
    obj["SunDiffuseColorB"] = sun.sun_properties.diffuse[2]
    obj["SunSpecularColorR"] = sun.sun_properties.specular[0]
    obj["SunSpecularColorG"] = sun.sun_properties.specular[1]
    obj["SunSpecularColorB"] = sun.sun_properties.specular[2]
    obj["SunIntensity"] = sun.sun_properties.intensity
    obj["SunGroupId"] = sun.sun_properties.group
  #endif
  # ----------------------------------------------------------------------------------
  if "ShadowProjector" in bpy.data.objects and "ShadowProjectorTarget" in bpy.data.objects:
    shadow = bpy.data.objects["ShadowProjector"]
    target = bpy.data.objects["ShadowProjectorTarget"]
    shadow_pos = utils.get_position_of_object(shadow)
    target_pos = utils.get_position_of_object(target)
    obj["ShadowEnabled"] = True
    obj["ShadowPositionX"] = shadow_pos[0]
    obj["ShadowPositionY"] = shadow_pos[1]
    obj["ShadowPositionZ"] = shadow_pos[2]
    obj["ShadowTargetX"] = target_pos[0]
    obj["ShadowTargetY"] = target_pos[1]
    obj["ShadowTargetZ"] = target_pos[2]
    obj["ShadowSize"] = shadow.shadow_properties.size
    obj["ShadowDepth"] = shadow.shadow_properties.depth
    obj["ShadowTextureSize"] = shadow.shadow_properties.texture_size
  #endif
  # ----------------------------------------------------------------------------------
  obj["FogEnabled"] = bpy.context.scene.world_properties.fog_enabled
  obj["FogNear"] = bpy.context.scene.world_properties.fog_near
  obj["FogFar"] = bpy.context.scene.world_properties.fog_far
  obj["FogColorR"] = bpy.context.scene.world_properties.fog_color[0]
  obj["FogColorG"] = bpy.context.scene.world_properties.fog_color[1]
  obj["FogColorB"] = bpy.context.scene.world_properties.fog_color[2]
  # ----------------------------------------------------------------------------------
  obj["AmbientR"] = bpy.context.scene.world_properties.ambient[0]
  obj["AmbientG"] = bpy.context.scene.world_properties.ambient[1]
  obj["AmbientB"] = bpy.context.scene.world_properties.ambient[2]
  # ----------------------------------------------------------------------------------
  obj["DecalAtlas"] = bpy.path.basename(bpy.context.scene.world_properties.decal_atlas)
  # ----------------------------------------------------------------------------------
  obj["CustomParams"] = []
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s00_name, "Value": bpy.context.scene.world_properties.world_s00_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s01_name, "Value": bpy.context.scene.world_properties.world_s01_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s02_name, "Value": bpy.context.scene.world_properties.world_s02_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s03_name, "Value": bpy.context.scene.world_properties.world_s03_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s04_name, "Value": bpy.context.scene.world_properties.world_s04_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s05_name, "Value": bpy.context.scene.world_properties.world_s05_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s06_name, "Value": bpy.context.scene.world_properties.world_s06_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s07_name, "Value": bpy.context.scene.world_properties.world_s07_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s08_name, "Value": bpy.context.scene.world_properties.world_s08_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s09_name, "Value": bpy.context.scene.world_properties.world_s09_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s10_name, "Value": bpy.context.scene.world_properties.world_s10_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s11_name, "Value": bpy.context.scene.world_properties.world_s11_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s12_name, "Value": bpy.context.scene.world_properties.world_s12_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s13_name, "Value": bpy.context.scene.world_properties.world_s13_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s14_name, "Value": bpy.context.scene.world_properties.world_s14_value })
  obj["CustomParams"].append({ "Name": bpy.context.scene.world_properties.world_s15_name, "Value": bpy.context.scene.world_properties.world_s15_value })

  resources_files = []
  utils.copy_texture_file(path, resources_files, bpy.context.scene.world_properties)

  file = utils.get_available_filename(path, filename, 'wrd')
  with open(file, 'w', encoding='utf-8') as f:
    json.dump(obj, f, ensure_ascii=False)
  #endwith
  return resources_files


# ----------------------------------------------------------------------------------
# SPECIAL
# ----------------------------------------------------------------------------------
def special_export_dcl_json(selected_obj, path, filename):
  obj = {
    "Ident": "DCL"
  }

  pos = utils.get_position_of_object(selected_obj)
  rot = utils.get_rotation_of_object(selected_obj)

  obj["PositionX"] = pos[0]
  obj["PositionY"] = pos[1]
  obj["PositionZ"] = pos[2]
  obj["RotationX"] = rot[0]
  obj["RotationY"] = rot[1]
  obj["RotationZ"] = rot[2]
  obj["SizeX"] = selected_obj.decal_properties.size[0]
  obj["SizeY"] = selected_obj.decal_properties.size[1]
  obj["SizeZ"] = selected_obj.decal_properties.size[2]
  obj["GroupId"] = selected_obj.decal_properties.group
  obj["SourceX"] = selected_obj.decal_properties.source_position[0]
  obj["SourceY"] = selected_obj.decal_properties.source_position[1]
  obj["SourceWidth"] = selected_obj.decal_properties.source_size[0]
  obj["SourceHeight"] = selected_obj.decal_properties.source_size[1]
  obj["Opacity"] = selected_obj.decal_properties.opacity

  file = utils.get_available_filename(path, filename, 'dcl')
  with open(file, 'w', encoding='utf-8') as f:
    json.dump(obj, f, ensure_ascii=False)
  #endwith


def special_export_sky_json(selected_obj, path, filename):
  obj = {
    "Ident": "SKY"
  }

  obj["Name"] = selected_obj.skybox_properties.name
  obj["Right"] = bpy.path.basename(selected_obj.skybox_properties.right)
  obj["Left"] = bpy.path.basename(selected_obj.skybox_properties.left)
  obj["Top"] = bpy.path.basename(selected_obj.skybox_properties.top)
  obj["Bottom"] = bpy.path.basename(selected_obj.skybox_properties.bottom)
  obj["Front"] = bpy.path.basename(selected_obj.skybox_properties.front)
  obj["Back"] = bpy.path.basename(selected_obj.skybox_properties.back)

  resources_files = []
  utils.copy_texture_file(path, resources_files, selected_obj.skybox_properties)

  file = utils.get_available_filename(path, filename, 'sky')
  with open(file, 'w', encoding='utf-8') as f:
    json.dump(obj, f, ensure_ascii=False)
  #endwith
  return resources_files


def special_export_prt_json(selected_obj, path, filename):
  obj = {
    "Ident": "PRT"
  }

  obj["Position"] = list(utils.get_position_of_object(selected_obj))
  obj["Rotation"] = list(utils.get_rotation_of_object(selected_obj))
  obj["Texture"] = bpy.path.basename(selected_obj.particles_properties.texture)
  obj["PositionStyle"] = selected_obj.particles_properties.position_style
  obj["PositionBase"] = list(selected_obj.particles_properties.position_base)
  obj["PositionSpread"] = list(selected_obj.particles_properties.position_spread)
  obj["PositionSphereRadiusBase"] = selected_obj.particles_properties.position_sphere_radius_base
  obj["PositionRadiusSpread"] = selected_obj.particles_properties.position_radius_spread
  obj["VelocityStyle"] = selected_obj.particles_properties.velocity_style
  obj["VelocityBase"] = list(selected_obj.particles_properties.velocity_base)
  obj["VelocitySpread"] = list(selected_obj.particles_properties.velocity_spread)
  obj["VelocityExplodeSpeedBase"] = selected_obj.particles_properties.velocity_explode_speed_base
  obj["VelocityExplodeSpeedSpread"] = selected_obj.particles_properties.velocity_explode_speed_spread
  obj["ColorBase"] = list(selected_obj.particles_properties.color_base)
  obj["ColorSpread"] = list(selected_obj.particles_properties.color_spread)
  obj["SizeBase"] = selected_obj.particles_properties.size_base
  obj["SizeSpread"] = selected_obj.particles_properties.size_spread
  obj["OpacityBase"] = selected_obj.particles_properties.opacity_base
  obj["OpacitySpread"] = selected_obj.particles_properties.opacity_spread
  obj["AccelerationBase"] = list(selected_obj.particles_properties.acceleration_base)
  obj["AccelerationSpread"] = list(selected_obj.particles_properties.acceleration_spread)
  obj["AngleBase"] = selected_obj.particles_properties.angle_base
  obj["AngleSpread"] = selected_obj.particles_properties.angle_spread
  obj["AngleVelocityBase"] = selected_obj.particles_properties.angle_velocity_base
  obj["AngleVelocitySpread"] = selected_obj.particles_properties.angle_velocity_spread
  obj["AngleAccelerationBase"] = selected_obj.particles_properties.angle_acceleration_base
  obj["AngleAccelerationSpread"] = selected_obj.particles_properties.angle_acceleration_spread
  obj["ParticleDeathAge"] = selected_obj.particles_properties.particle_death_age
  obj["ParticlesPerSecond"] = selected_obj.particles_properties.particles_per_second
  obj["ParticlesQuantity"] = selected_obj.particles_properties.particles_quantity
  obj["EmitterDeathAge"] = selected_obj.particles_properties.emitter_death_age

  utils.process_tween_vector(selected_obj.particles_properties.tweens_color, "ColorTween", obj)
  utils.process_tween_number(selected_obj.particles_properties.tweens_size, "SizeTween", obj)
  utils.process_tween_number(selected_obj.particles_properties.tweens_opacity, "OpacityTween", obj)
  utils.process_tween_vector(selected_obj.particles_properties.tweens_acceleration, "AccelerationTween", obj)

  resources_files = []
  utils.copy_texture_file(path, resources_files, selected_obj.particles_properties)

  file = utils.get_available_filename(path, filename, 'prt')
  with open(file, 'w', encoding='utf-8') as f:
    json.dump(obj, f, ensure_ascii=False)
  #endwith
  return resources_files


# ----------------------------------------------------------------------------------
# ENT
# ----------------------------------------------------------------------------------
def ent_export(selected_obj):
  obj = {
    "Ident": "ENT"
  }

  pos = utils.get_position_of_object(selected_obj)
  rot = utils.get_rotation_of_object(selected_obj)
  sca = utils.get_scale_of_object(selected_obj)

  obj["Name"] = selected_obj.name
  obj["Type"] = selected_obj.entity_properties.type
  obj["Shape"] = selected_obj.get("entity_shape", "UNKNOWN")
  obj["PositionX"] = pos[0]
  obj["PositionY"] = pos[1]
  obj["PositionZ"] = pos[2]
  obj["RotationX"] = rot[0]
  obj["RotationY"] = rot[1]
  obj["RotationZ"] = rot[2]
  obj["ScaleX"] = sca[0]
  obj["ScaleY"] = sca[1]
  obj["ScaleZ"] = sca[2]
  obj["Width"] = selected_obj.dimensions.x
  obj["Height"] = selected_obj.dimensions.z
  obj["Depth"] = selected_obj.dimensions.y
  obj["CustomParams"] = []
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s00_name, "Value": selected_obj.entity_properties.s00_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s01_name, "Value": selected_obj.entity_properties.s01_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s02_name, "Value": selected_obj.entity_properties.s02_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s03_name, "Value": selected_obj.entity_properties.s03_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s04_name, "Value": selected_obj.entity_properties.s04_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s05_name, "Value": selected_obj.entity_properties.s05_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s06_name, "Value": selected_obj.entity_properties.s06_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s07_name, "Value": selected_obj.entity_properties.s07_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s08_name, "Value": selected_obj.entity_properties.s08_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s09_name, "Value": selected_obj.entity_properties.s09_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s10_name, "Value": selected_obj.entity_properties.s10_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s11_name, "Value": selected_obj.entity_properties.s11_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s12_name, "Value": selected_obj.entity_properties.s12_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s13_name, "Value": selected_obj.entity_properties.s13_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s14_name, "Value": selected_obj.entity_properties.s14_value })
  obj["CustomParams"].append({ "Name": selected_obj.entity_properties.s15_name, "Value": selected_obj.entity_properties.s15_value })

  if selected_obj.data.name in ["SPHERE", "CYLINDER", "CIRCLE"]:
    obj["Radius"] = selected_obj.dimensions.x / 2
  #endif
  return obj


def ent_export_json(selected_obj, path, filename):
  file = utils.get_available_filename(path, filename, 'ent')
  data = ent_export(selected_obj)

  with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
  #endwith


# ----------------------------------------------------------------------------------
# PACK
# ----------------------------------------------------------------------------------
def pack(path, context):
  path = os.path.join(path, "")
  path_list = []

  res = world_export_json(path, "scene")
  path_list.append(path + 'scene.wrd')
  path_list.extend(res)

  camera_export_json(path, "scene")
  path_list.append(path + 'scene.cam')

  for collection in bpy.data.collections:
    if (collection.name == "JAM"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          jam_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.bam')
        else:
          jam_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jam')
        #endif
        res = mat_export_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.mat')
        path_list.extend(res)
        utils.copy_sampler_file(path, path_list, obj, obj.mat_properties, obj.mat_properties.sampler_enabled)
      #endfor
    #endif

    if (collection.name == "JSM"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          jsm_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.bsm')
        else:
          jsm_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jsm')
        #endif
        res = mat_export_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.mat')
        path_list.extend(res)
        utils.copy_sampler_file(path, path_list, obj, obj.mat_properties, obj.mat_properties.sampler_enabled)
      #endfor
    #endif

    if (collection.name == "JWM"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          jwm_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.bwm')
        else:
          jwm_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jwm')
        #endif
      #endfor
    #endif

    if (collection.name == "JNM"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          jnm_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.bnm')
        else:
          jnm_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jnm')
        #endif
      #endfor
    #endif

    if (collection.name == "JLM"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          jlm_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.blm')
        else:
          jlm_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jlm')
        #endif
      #endfor
    #endif

    if (collection.name == "JSV"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          jsv_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.bsv')
        else:
          jsv_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jsv')
        #endif
      #endfor
    #endif

    if (collection.name == "JWA"):
      for obj in collection.objects:
        if context.scene.world_properties.enable_export_has_binary:
          res = jwa_export_binary(obj, path, obj.name)
          path_list.append(path + obj.name + '.bwa')
          path_list.extend(res)
        else:
          res = jwa_export_json(obj, path, obj.name)
          path_list.append(path + obj.name + '.jwa')
          path_list.extend(res)
        #endif
      #endfor
    #endif

    if (collection.name == "JLT"):
      for obj in collection.objects:
        jlt_export_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.jlt')
      #endfor
    #endif

    if (collection.name == "OBJ"):
      for obj in collection.objects:
        obj_exporter(obj, path, obj.name)
        path_list.append(path + obj.name + '.obj')
        path_list.append(path + obj.name + '.mtl')
      #endfor
    #endif

    if (collection.name == "GRF"):
      for obj in collection.objects:
        grf_export_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.grf')
      #endfor
    #endif

    # specials ----------------------------------------------------------------------------------

    if (collection.name == "DCL"):
      for obj in collection.objects:
        special_export_dcl_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.dcl')
      #endfor
    #endif

    if (collection.name == "SKY"):
      for obj in collection.objects:
        res = special_export_sky_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.sky')
        path_list.extend(res)
      #endfor
    #endif

    if (collection.name == "PRT"):
      for obj in collection.objects:
        res = special_export_prt_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.prt')
        path_list.extend(res)
      #endfor
    #endif

    if (collection.name == "ENT"):
      for obj in collection.objects:
        ent_export_json(obj, path, obj.name)
        path_list.append(path + obj.name + '.ent')
      #endfor
    #endif
  #endfor

  scene_name = os.path.basename(bpy.data.filepath)
  utils.zip_files(path_list, path + scene_name + '.pak')

  path_list = list(set(path_list))

  for file in path_list:
    os.remove(file)
  #endfor