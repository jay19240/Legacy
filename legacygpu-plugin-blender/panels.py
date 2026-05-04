import bpy
import bpy.utils.previews
import os
import bmesh
from . import utils
# ----------------------------------------------------------------------------------

preview_collections = {}

def register():
  pcoll = bpy.utils.previews.new()
  img_engine_path = os.path.join(os.path.dirname(__file__), "images/engine.png")
  pcoll.load("engine", img_engine_path, 'IMAGE')
  preview_collections["main"] = pcoll

  bpy.utils.register_class(WARME_PT_options)
  bpy.utils.register_class(WARME_PT_object)
  bpy.utils.register_class(WARME_PT_grf_node_editor)


def unregister():
  for pcoll in preview_collections.values():
    bpy.utils.previews.remove(pcoll)
  preview_collections.clear()

  bpy.utils.unregister_class(WARME_PT_options)
  bpy.utils.unregister_class(WARME_PT_object)
  bpy.utils.unregister_class(WARME_PT_grf_node_editor)


class WARME_PT_options(bpy.types.Panel):
  bl_idname = "WARME_PT_options"
  bl_label = "Legacy"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "Legacy"
  bl_context = "objectmode"

  def draw(self, context):
    pcoll = preview_collections["main"]
    engine_image = pcoll["engine"]
    layout = self.layout.column()

    box = layout.box()
    row = box.row()
    row.alignment = 'CENTER'
    row.template_icon(icon_value=engine_image.icon_id, scale=10)

    utils.draw_input_row(layout, context.scene, "export_assets_path", "Assets Path")
    layout.separator()
    layout.operator("object.export_pack")
    layout.separator()

    # START GAME
    box, opened = utils.draw_foldout(layout, context.scene.world_properties, "show_game", "Game", 'ALIASED')
    if opened:
      utils.draw_input_row(layout, context.scene, "export_engine_path", "Engine Path")
      layout.separator()
      layout.prop(context.scene, "auggie_prompt", text="")
      layout.separator()
      layout.operator("object.run_auggie", icon='PLAY')
      layout.separator()
      row = layout.row()
      row.alignment = 'CENTER'
      row.label(text=f"Generation status: {context.scene.auggie_status}")
      layout.separator()
      layout.operator("object.run_server")
      layout.operator("object.kill_server")
      layout.separator()
      layout.operator("object.run_game")
    # END GAME

    # START EXPORT
    box, opened = utils.draw_foldout(layout, context.scene.world_properties, "show_export", "Export", 'EXPORT')
    if opened:
      layout.operator("object.export_objects")
      layout.operator("object.export_objects_as_wavefront")
      layout.separator()
      layout.operator("object.export_world_json")
      layout.operator("object.export_camera_json")
      layout.separator()
      layout.prop(context.scene.world_properties, "enable_auto_export")
      layout.prop(context.scene.world_properties, "enable_export_has_binary")
    # END EXPORT

    # START CREATE
    box, opened = utils.draw_foldout(layout, context.scene.world_properties, "show_create", "Create", 'ADD')
    if opened:
      utils.draw_title_row(layout, "--- Meshes ---")
      layout.operator("object.create_jsm")
      layout.operator("object.create_obj")
      layout.operator("object.create_jam")
      layout.operator("object.create_jwm")
      layout.operator("object.create_jnm")
      layout.operator("object.create_jwa")
      layout.operator("object.create_jsv")
      layout.operator("object.create_grf")

      utils.draw_title_row(layout, "--- Lines & Curves ---")
      layout.operator("object.create_jlm_points")
      layout.operator("object.create_jlm_curve")

      utils.draw_title_row(layout, "--- Lights ---")
      layout.operator("object.create_jlt_point")
      layout.operator("object.create_jlt_spot")

      utils.draw_title_row(layout, "--- Specials ---")
      layout.operator("object.create_special_dcl")
      layout.operator("object.create_special_sun")
      layout.operator("object.create_special_shadow_projector")
      layout.operator("object.create_special_shadow_projector_target")
      layout.operator("object.create_special_skybox")
      layout.operator("object.create_special_particles")

      utils.draw_title_row(layout, "--- Entities ---")
      layout.operator("object.create_entity_aabb")
      layout.operator("object.create_entity_cylinder")
      layout.operator("object.create_entity_sphere")
      layout.operator("object.create_entity_circle")
      layout.operator("object.create_entity_plane")
    #END CREATE

    # START CAST
    box, opened = utils.draw_foldout(layout, context.scene.world_properties, "show_cast_to", "Cast To", 'ARROW_LEFTRIGHT')
    if opened:
      utils.draw_title_row(layout, "--- Meshes ---")
      layout.operator("object.cast_to_jsm")
      layout.operator("object.cast_to_jam")
      layout.operator("object.cast_to_jwm")
      layout.operator("object.cast_to_jnm")
      layout.operator("object.cast_to_jwa")
      layout.operator("object.cast_to_jsv")
    # END CAST

    # START CAMERA
    box, opened = utils.draw_foldout(layout, context.scene.world_properties, "show_camera", "Camera", 'CAMERA_DATA')
    if opened:
      layout.prop(context.scene.world_properties, "camera_projection_type_bind")
      layout.prop(context.scene.world_properties, "camera_fovy_bind")
      layout.prop(context.scene.world_properties, "camera_near_bind")
      layout.prop(context.scene.world_properties, "camera_far_bind")
      layout.prop(context.scene.world_properties, "camera_ortho_size_bind")
      layout.prop(context.scene.world_properties, "camera_clip_offset")
      layout.prop(context.scene.world_properties, "camera_min_clip_offset")
      layout.prop(context.scene.world_properties, "camera_max_clip_offset")
      layout.prop(context.scene.world_properties, "camera_matrix_export_enabled")
    # END CAMERA

    # START WORLD
    box, opened = utils.draw_foldout(layout, context.scene.world_properties, "show_world", "World", 'WORLD')
    if opened:
      utils.draw_title_row(layout, "--- Fog ---")
      layout.prop(context.scene.world_properties, "fog_enabled")
      layout.prop(context.scene.world_properties, "fog_near")
      layout.prop(context.scene.world_properties, "fog_far")
      utils.draw_input_row(layout, context.scene.world_properties, "fog_color", "Fog Color")
      utils.draw_title_row(layout, "--- Others ---")
      utils.draw_input_row(layout, context.scene.world_properties, "ambient", "Ambient Color")
      utils.draw_input_row(layout, context.scene.world_properties, "decal_atlas", "Decal Atlas")
      utils.draw_title_row(layout, "--- Custom Params ---")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s00_name", text="")
      row.prop(context.scene.world_properties, "world_s00_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s01_name", text="")
      row.prop(context.scene.world_properties, "world_s01_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s02_name", text="")
      row.prop(context.scene.world_properties, "world_s02_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s03_name", text="")
      row.prop(context.scene.world_properties, "world_s03_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s04_name", text="")
      row.prop(context.scene.world_properties, "world_s04_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s05_name", text="")
      row.prop(context.scene.world_properties, "world_s05_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s06_name", text="")
      row.prop(context.scene.world_properties, "world_s06_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s07_name", text="")
      row.prop(context.scene.world_properties, "world_s07_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s08_name", text="")
      row.prop(context.scene.world_properties, "world_s08_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s09_name", text="")
      row.prop(context.scene.world_properties, "world_s09_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s10_name", text="")
      row.prop(context.scene.world_properties, "world_s10_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s11_name", text="")
      row.prop(context.scene.world_properties, "world_s11_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s12_name", text="")
      row.prop(context.scene.world_properties, "world_s12_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s13_name", text="")
      row.prop(context.scene.world_properties, "world_s13_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s14_name", text="")
      row.prop(context.scene.world_properties, "world_s14_value", text="")
      row = layout.row()
      row.prop(context.scene.world_properties, "world_s15_name", text="")
      row.prop(context.scene.world_properties, "world_s15_value", text="")
    # END WORLD


class WARME_PT_object(bpy.types.Panel):
  bl_idname = "WARME_PT_object"
  bl_label = "Legacy Object"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "Legacy Object"
  bl_context = "objectmode"

  def draw(self, context):
    selected = bpy.context.selected_objects
    layout = self.layout.column()    
    layout.separator()

    # START TRANSFORM
    if bpy.context.selected_objects and bpy.context.selected_objects[0]:
      selected_object = bpy.context.selected_objects[0]
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_transform_infos", "Transform Informations", 'PREFERENCES')
      if opened:
        pos = utils.get_position_of_object(bpy.context.selected_objects[0])
        layout.operator("object.copy_object_position")
        layout.label(text=f"X: {pos[0]:.3f}")
        layout.label(text=f"Y: {pos[1]:.3f}")
        layout.label(text=f"Z: {pos[2]:.3f}")
        layout.separator()

        rot = utils.get_rotation_of_object(bpy.context.selected_objects[0])
        layout.operator("object.copy_object_rotation")
        layout.label(text=f"X: {rot[0]:.3f}")
        layout.label(text=f"Y: {rot[1]:.3f}")
        layout.label(text=f"Z: {rot[2]:.3f}")
        layout.separator()
        
        mat = utils.get_object_matrix_converted_for_engine(bpy.context.selected_objects[0])
        layout.operator("object.copy_object_matrix")
        layout.label(text=f"{mat[0][0]:.3f}, {mat[0][1]:.3f}, {mat[0][2]:.3f}, {mat[0][3]:.3f}")
        layout.label(text=f"{mat[1][0]:.3f}, {mat[1][1]:.3f}, {mat[1][2]:.3f}, {mat[1][3]:.3f}")
        layout.label(text=f"{mat[2][0]:.3f}, {mat[2][1]:.3f}, {mat[2][2]:.3f}, {mat[2][3]:.3f}")
        layout.label(text=f"{mat[3][0]:.3f}, {mat[3][1]:.3f}, {mat[3][2]:.3f}, {mat[3][3]:.3f}")
      #endif
    # END TRANSFORM

    # START SUN
    if selected and len(selected) == 1 and selected[0].name == 'Sun':
      selected_object = bpy.context.selected_objects[0]
      utils.draw_input_row(layout, selected_object.sun_properties, "diffuse", "Diffuse")
      utils.draw_input_row(layout, selected_object.sun_properties, "specular", "Specular")
      layout.prop(selected_object.sun_properties, "intensity")
      layout.prop(selected_object.sun_properties, "group")
    # END SUN

    # START SHADOW
    if selected and len(selected) == 1 and selected[0].name == 'ShadowProjector':
      selected_object = bpy.context.selected_objects[0]
      utils.draw_input_row(layout, selected_object.shadow_properties, "size", "Size")
      utils.draw_input_row(layout, selected_object.shadow_properties, "depth", "Depth")
      utils.draw_input_row(layout, selected_object.shadow_properties, "texture_size", "Texture Depth Size")
    # END SHADOW

    # START SKYBOX
    if selected and len(selected) == 1 and utils.belong_to_collection(bpy.context.selected_objects[0], "SKY"):
      selected_object = bpy.context.selected_objects[0]
      utils.draw_input_row(layout, selected_object.skybox_properties, "name", "Name")
      utils.draw_input_row(layout, selected_object.skybox_properties, "right", "Right")
      utils.draw_input_row(layout, selected_object.skybox_properties, "left", "Left")
      utils.draw_input_row(layout, selected_object.skybox_properties, "top", "Top")
      utils.draw_input_row(layout, selected_object.skybox_properties, "bottom", "Bottom")
      utils.draw_input_row(layout, selected_object.skybox_properties, "front", "Front")
      utils.draw_input_row(layout, selected_object.skybox_properties, "back", "Back")
    # END SKYBOX

    # START PARTICLES
    if selected and len(selected) == 1 and utils.belong_to_collection(bpy.context.selected_objects[0], "PRT"):
      selected_object = bpy.context.selected_objects[0]
      utils.draw_input_row(layout, selected_object.particles_properties, "texture", "Texture")
      utils.draw_input_row(layout, selected_object.particles_properties, "position_style", "Position Style")
      utils.draw_input_row(layout, selected_object.particles_properties, "position_base", "Position Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "position_spread", "Position Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "position_sphere_radius_base", "Position Sphere Radius Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "position_radius_spread", "Position Radius Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "velocity_style", "Velocity Style")
      utils.draw_input_row(layout, selected_object.particles_properties, "velocity_base", "Velocity Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "velocity_spread", "Velocity Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "velocity_explode_speed_base", "Velocity Explode Speed Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "velocity_explode_speed_spread", "Velocity Explode Speed Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "color_base", "Color Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "color_spread", "Color Spread")

      layout = self.layout.column()
      layout.operator("object.add_particles_tweens_color")
      layout.operator("object.remove_particles_tweens_color")
      layout.separator(type="LINE")
      # Row for each items
      for i, anim in enumerate(context.object.particles_properties.tweens_color):
        utils.draw_input_row(layout, context.object.particles_properties.tweens_color[i], "time", "Time")
        utils.draw_input_row(layout, context.object.particles_properties.tweens_color[i], "value", "Value")
        layout.separator(type="LINE")
      #endfor

      utils.draw_input_row(layout, selected_object.particles_properties, "size_base", "Size Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "size_spread", "Size Spread")

      layout = self.layout.column()
      layout.operator("object.add_particles_tweens_size")
      layout.operator("object.remove_particles_tweens_size")
      layout.separator(type="LINE")
      # Row for each items
      for i, anim in enumerate(context.object.particles_properties.tweens_size):
        utils.draw_input_row(layout, context.object.particles_properties.tweens_size[i], "time", "Time")
        utils.draw_input_row(layout, context.object.particles_properties.tweens_size[i], "value", "Value")
        layout.separator(type="LINE")
      #endfor

      utils.draw_input_row(layout, selected_object.particles_properties, "opacity_base", "Opacity Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "opacity_spread", "Opacity Spread")

      layout = self.layout.column()
      layout.operator("object.add_particles_tweens_opacity")
      layout.operator("object.remove_particles_tweens_opacity")
      layout.separator(type="LINE")
      # Row for each items
      for i, anim in enumerate(context.object.particles_properties.tweens_opacity):
        utils.draw_input_row(layout, context.object.particles_properties.tweens_opacity[i], "time", "Time")
        utils.draw_input_row(layout, context.object.particles_properties.tweens_opacity[i], "value", "Value")
        layout.separator(type="LINE")
      #endfor

      utils.draw_input_row(layout, selected_object.particles_properties, "acceleration_base", "Acceleration Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "acceleration_spread", "Acceleration Spread")

      layout = self.layout.column()
      layout.operator("object.add_particles_tweens_acceleration")
      layout.operator("object.remove_particles_tweens_acceleration")
      layout.separator(type="LINE")
      # Row for each items
      for i, anim in enumerate(context.object.particles_properties.tweens_acceleration):
        utils.draw_input_row(layout, context.object.particles_properties.tweens_acceleration[i], "time", "Time")
        utils.draw_input_row(layout, context.object.particles_properties.tweens_acceleration[i], "value", "Value")
        layout.separator(type="LINE")
      #endfor

      utils.draw_input_row(layout, selected_object.particles_properties, "angle_base", "Angle Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "angle_spread", "Angle Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "angle_velocity_base", "Angle Velocity Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "angle_velocity_spread", "Angle Velocity Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "angle_acceleration_base", "Angle Acceleration Base")
      utils.draw_input_row(layout, selected_object.particles_properties, "angle_acceleration_spread", "Angle Acceleration Spread")
      utils.draw_input_row(layout, selected_object.particles_properties, "particle_death_age", "Particle Death Age")
      utils.draw_input_row(layout, selected_object.particles_properties, "particles_per_second", "Particles Per Second")
      utils.draw_input_row(layout, selected_object.particles_properties, "particles_quantity", "Particles Quantity")
      utils.draw_input_row(layout, selected_object.particles_properties, "emitter_death_age", "Emitter Death Age")
    # END PARTICLES

    # START LIGHT
    if selected and len(selected) == 1 and selected[0].type == 'LIGHT':
      selected_object = bpy.context.selected_objects[0]
      layout = self.layout.column()
      utils.draw_input_row(layout, selected_object.light_properties, "diffuse", "Diffuse")
      utils.draw_input_row(layout, selected_object.light_properties, "specular", "Specular")
      layout.prop(selected_object.light_properties, "intensity")
      layout.prop(selected_object.light_properties, "constant")
      layout.prop(selected_object.light_properties, "linear")
      layout.prop(selected_object.light_properties, "exp")
      layout.prop(selected_object.light_properties, "group")
      layout.prop(selected_object.light_properties, "spot_cutoff_angle")
    # END LIGHT

    # START DECAL
    if selected and len(selected) == 1 and utils.belong_to_collection(bpy.context.selected_objects[0], "DCL"):
      selected_object = bpy.context.selected_objects[0]
      layout = self.layout.column()
      utils.draw_input_row(layout, selected_object.decal_properties, "size", "Size")
      utils.draw_input_row(layout, selected_object.decal_properties, "group", "Group")
      utils.draw_input_row(layout, selected_object.decal_properties, "source_position", "Source Position")
      utils.draw_input_row(layout, selected_object.decal_properties, "source_size", "Source Size")
      utils.draw_input_row(layout, selected_object.decal_properties, "opacity", "Opacity")
    # END DECAL

    # START ENTITY
    if selected and len(selected) == 1 and utils.belong_to_collection(bpy.context.selected_objects[0], "ENT"):
      selected_object = bpy.context.selected_objects[0]
      layout = self.layout.column()
      utils.draw_input_row(layout, selected_object.entity_properties, "type", "Type")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s00_name", text="")
      row.prop(selected_object.entity_properties, "s00_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s01_name", text="")
      row.prop(selected_object.entity_properties, "s01_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s02_name", text="")
      row.prop(selected_object.entity_properties, "s02_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s03_name", text="")
      row.prop(selected_object.entity_properties, "s03_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s04_name", text="")
      row.prop(selected_object.entity_properties, "s04_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s05_name", text="")
      row.prop(selected_object.entity_properties, "s05_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s06_name", text="")
      row.prop(selected_object.entity_properties, "s06_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s07_name", text="")
      row.prop(selected_object.entity_properties, "s07_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s08_name", text="")
      row.prop(selected_object.entity_properties, "s08_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s09_name", text="")
      row.prop(selected_object.entity_properties, "s09_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s10_name", text="")
      row.prop(selected_object.entity_properties, "s10_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s11_name", text="")
      row.prop(selected_object.entity_properties, "s11_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s12_name", text="")
      row.prop(selected_object.entity_properties, "s12_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s13_name", text="")
      row.prop(selected_object.entity_properties, "s13_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s14_name", text="")
      row.prop(selected_object.entity_properties, "s14_value", text="")
      row = layout.row()
      row.prop(selected_object.entity_properties, "s15_name", text="")
      row.prop(selected_object.entity_properties, "s15_value", text="")
    # END ENTITY

    # START WATER
    if selected and len(selected) == 1 and utils.belong_to_collection(bpy.context.selected_objects[0], "JWA"):
      selected_object = bpy.context.selected_objects[0]
      layout = self.layout.column()

      box, opened = utils.draw_foldout(layout, selected_object.water_properties, "show_wave", "Wave", 'SMOOTHCURVE')
      if opened:
        utils.draw_input_row(layout, selected_object.water_properties, "wave_amplitude", "Amplitude")
        utils.draw_input_row(layout, selected_object.water_properties, "wave_scale", "Scale")
        utils.draw_input_row(layout, selected_object.water_properties, "wave_speed", "Speed")
        utils.draw_input_row(layout, selected_object.water_properties, "wave_choppiness", "Choppiness")
        utils.draw_input_row(layout, selected_object.water_properties, "wave_step_x", "Step X")
        utils.draw_input_row(layout, selected_object.water_properties, "wave_step_z", "Step Z")

      box, opened = utils.draw_foldout(layout, selected_object.water_properties, "show_normal_map", "Normal Map", 'NORMALS_FACE')
      if opened:
        utils.draw_input_row(layout, selected_object.water_properties, "normal_map", "Texture")
        utils.draw_input_row(layout, selected_object.water_properties, "normal_map_scroll_x", "Scroll X")
        utils.draw_input_row(layout, selected_object.water_properties, "normal_map_scroll_y", "Scroll Y")
        utils.draw_input_row(layout, selected_object.water_properties, "normal_map_intensity", "Intensity")
        utils.draw_input_row(layout, selected_object.water_properties, "normal_map_scale", "Scale")

      box, opened = utils.draw_foldout(layout, selected_object.water_properties, "show_surface_color", "Surface Color", 'COLOR')
      if opened:
        utils.draw_input_row(layout, selected_object.water_properties, "surface_color_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.water_properties, "surface_color", "Color")
        utils.draw_input_row(layout, selected_object.water_properties, "surface_color_factor", "Color Factor")

      box, opened = utils.draw_foldout(layout, selected_object.water_properties, "show_optics", "Optics Settings", 'SHADING_TEXTURE')
      if opened:
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_map_right", "Env Map Right")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_map_left", "Env Map Left")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_map_top", "Env Map Top")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_map_bottom", "Env Map Bottom")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_map_front", "Env Map Front")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_map_back", "Env Map Back")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_env_intensity", "Env Map Intensity")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_fresnel_power", "Fresnel Power")
        utils.draw_input_row(layout, selected_object.water_properties, "optics_fresnel_biais", "Fresnel Biais")

      box, opened = utils.draw_foldout(layout, selected_object.water_properties, "show_sun", "Sun", 'LIGHT')
      if opened:
        utils.draw_input_row(layout, selected_object.water_properties, "sun_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.water_properties, "sun_direction_x", "Direction X")
        utils.draw_input_row(layout, selected_object.water_properties, "sun_direction_y", "Direction Y")
        utils.draw_input_row(layout, selected_object.water_properties, "sun_direction_z", "Direction Z")
        utils.draw_input_row(layout, selected_object.water_properties, "sun_color", "Color")
        utils.draw_input_row(layout, selected_object.water_properties, "sun_color_factor", "Color Factor")

      box, opened = utils.draw_foldout(layout, selected_object.water_properties, "show_custom_params", "Custom Params", 'RNA')
      if opened:
        row = layout.row()
        row.prop(selected_object.water_properties, "s00_name", text="")
        row.prop(selected_object.water_properties, "s00_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s01_name", text="")
        row.prop(selected_object.water_properties, "s01_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s02_name", text="")
        row.prop(selected_object.water_properties, "s02_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s03_name", text="")
        row.prop(selected_object.water_properties, "s03_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s04_name", text="")
        row.prop(selected_object.water_properties, "s04_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s05_name", text="")
        row.prop(selected_object.water_properties, "s05_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s06_name", text="")
        row.prop(selected_object.water_properties, "s06_value", text="")
        row = layout.row()
        row.prop(selected_object.water_properties, "s07_name", text="")
        row.prop(selected_object.water_properties, "s07_value", text="")
        layout.separator(type="LINE")
        utils.draw_input_row(layout, selected_object.water_properties, "s0_texture", "Texture S0")
        utils.draw_input_row(layout, selected_object.water_properties, "s1_texture", "Texture S1")
    # END WATER

    # START JSM/JAM
    if selected and len(selected) == 1 and (utils.belong_to_collection(bpy.context.selected_objects[0], "JSM") or utils.belong_to_collection(bpy.context.selected_objects[0], "JAM")):
      selected_object = bpy.context.selected_objects[0]
      layout = self.layout.column()

      # START ANIMATIONS
      if bpy.context.selected_objects and bpy.context.selected_objects[0] and utils.belong_to_collection(bpy.context.selected_objects[0], "JAM"):
        box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_animation", "Animation Frames", 'PREFERENCES')
        if opened:
          layout = self.layout.column()
          layout.operator("object.add_animation")
          layout.operator("object.remove_animation")
          layout.separator(type="LINE")
          # Row for each animation
          for i, anim in enumerate(context.object.jam_animations):
            utils.draw_input_row(layout, context.object.jam_animations[i], "name", "Name")
            utils.draw_input_row(layout, context.object.jam_animations[i], "start_frame", "Start Frame")
            utils.draw_input_row(layout, context.object.jam_animations[i], "end_frame", "End Frame")
            utils.draw_input_row(layout, context.object.jam_animations[i], "frame_duration", "Frame Duration")
            layout.separator(type="LINE")
          #endfor
        #endif
      # END ANIMATIONS

      # GENERAL
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_general", "General", 'PREFERENCES')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "id", "Id")
        utils.draw_input_row(layout, selected_object.mat_properties, "opacity", "Opacity")

      # SHADOW
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_shadow", "Shadow", 'NORMALS_FACE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "shadow_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "shadow_casting", "Enable Shadow Casting")

      # DECALS
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_decals", "Decals", 'STICKY_UVS_DISABLE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "decal_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "decal_group", "Group Id")

      # LIGHT
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_light", "Light", 'LIGHT')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "light_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_group", "Group Id")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_gouraud_shading_enabled", "Enable Gouraud Shading")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_emissive_factor", "Emissive Strength Factor")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_emissive_color", "Emissive Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_ambient_color", "Ambient Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_diffuse_color", "Diffuse Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_specular_factor", "Specular Strength Factor")
        utils.draw_input_row(layout, selected_object.mat_properties, "light_specular_color", "Specular Color")

      # SAMPLER
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_sampler", "Sampler", 'IMAGE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_address_mode_u", "Address Mode U")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_address_mode_v", "Address Mode V")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_address_mode_w", "Address Mode W")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_mag_filter", "Mag Filter")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_min_filter", "Min Filter")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_mipmap_filter", "MipMap Filter")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_lod_min_clamp", "Lod Min Clamp")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_lod_max_clamp", "Lod Max Clamp")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_max_anisotropy", "Max Anisotropy")
        utils.draw_input_row(layout, selected_object.mat_properties, "sampler_type", "Type")

      # TEXTURE
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_texture", "Texture", 'PREFERENCES')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "texture", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_scroll_angle", "Scroll Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_scroll_rate", "Scroll Rate")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_offset", "Offset X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_offset", "Offset Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_scale", "Scale X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_scale", "Scale Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_rotation_angle", "Rotation Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_opacity", "Opacity")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_blend_color", "Blend Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_blend_color_mode", "Blend Color Mode")
        utils.draw_input_row(layout, selected_object.mat_properties, "texture_blend_color_mix", "Blend Color Mix")

      # SECONDARY TEXTURE
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_secondary_texture", "Secondary Texture", 'TEXTURE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_scroll_angle", "Scroll Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_scroll_rate", "Scroll Rate")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_offset", "Offset X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_offset", "Offset Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_scale", "Scale X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_scale", "Scale Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_rotation_angle", "Rotation Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_opacity", "Opacity")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_blend_mode", "Texture Blending Mode")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_blend_color", "Blend Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_blend_color_mode", "Blend Color Mode")
        utils.draw_input_row(layout, selected_object.mat_properties, "secondary_texture_blend_color_mix", "Blend Color Mix")

      # ENV MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_env_map", "Env Map", 'WORLD')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_name", "Name")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_right", "Right Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_left", "Left Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_top", "Top Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_bottom", "Bottom Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_front", "Front Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_back", "Back Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "env_map_opacity", "Opacity")

      # NORMAL MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_normal_map", "Normal Map", 'NORMALS_FACE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_scroll_angle", "Scroll Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_scroll_rate", "Scroll Rate")
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_offset", "Offset X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_offset", "Offset Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_scale", "Scale X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_scale", "Scale Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_rotation_angle", "Rotation Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "normal_map_intensity", "Intensity")

      # DISPLACEMENT MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_displacement_map", "Displacement Map", 'MOD_DISPLACE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_scroll_angle", "Scroll Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_scroll_rate", "Scroll Rate")
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_offset", "Offset X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_offset", "Offset Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_scale", "Scale X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_scale", "Scale Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_rotation_angle", "Rotation Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "displacement_map_factor", "Displacement Pixel Factor")
        utils.draw_input_row(layout, selected_object.mat_properties, "displace_texture", "Texture Albedo")
        utils.draw_input_row(layout, selected_object.mat_properties, "displace_secondary_texture", "Secondary Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "displace_normal_map", "Normal Map")
        utils.draw_input_row(layout, selected_object.mat_properties, "displace_dissolve_map", "Dissolve Map")
        utils.draw_input_row(layout, selected_object.mat_properties, "displace_env_map", "Env Map")

      # DISSOLVE MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_dissolve_map", "Dissolve Map", 'MOD_MASK')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_scroll_angle", "Scroll Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_scroll_rate", "Scroll Rate")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_offset", "Offset X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_offset", "Offset Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_scale", "Scale X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_scale", "Scale Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_map_rotation_angle", "Rotation Angle")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_glow", "Glow Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_glow_range", "Glow Range")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_glow_falloff", "Glow Fallof")
        utils.draw_input_row(layout, selected_object.mat_properties, "dissolve_amount", "Dissolve Amount")

      # TOON MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_toon_map", "Toon Map", 'OUTLINER_OB_LIGHT')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "toon_map", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "toon_map_opacity", "Opacity")
        utils.draw_input_row(layout, selected_object.mat_properties, "toon_light_dir", "Light Direction X", 0)
        utils.draw_input_row(layout, selected_object.mat_properties, "toon_light_dir", "Light Direction Y", 1)
        utils.draw_input_row(layout, selected_object.mat_properties, "toon_light_dir", "Light Direction Z", 2)

      # EMISSIVE MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_emissive_map", "Emissive Map", 'LIGHT_DATA')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "emissive_map", "Texture")

      # DIFFUSE MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_diffuse_map", "Diffuse Map", 'IMAGE')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "diffuse_map", "Texture")

      # SPECULAR MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_specular_map", "Specular Map", 'SHADING_RENDERED')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "specular_map", "Texture")

      # THUNE MAP
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_thune_map", "Thune Map", 'SHADING_RENDERED')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "thune_map", "Texture")
        utils.draw_input_row(layout, selected_object.mat_properties, "thune_map_shininess_enabled", "Shininess (R)")
        utils.draw_input_row(layout, selected_object.mat_properties, "thune_map_arcade_enabled", "Arcade (G)")
        utils.draw_input_row(layout, selected_object.mat_properties, "thune_map_reflective_enabled", "Reflective (B)")

      # ALPHA BLEND
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_alpha_blend", "Alpha Blend", 'MOD_UVPROJECT')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "alpha_blend_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "alpha_blend_facing", "Facing value")
        utils.draw_input_row(layout, selected_object.mat_properties, "alpha_blend_distance", "Distance start")

      # JITTER VERTEX
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_jitter_vertex", "Jitter Vertex", 'PLAY')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "jitter_vertex_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "jitter_vertex_level", "Strenght Level")

      # ARCADE
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_arcade", "Arcade Shading", 'MOD_UVPROJECT')
      if opened:
        utils.draw_input_row(layout, selected_object.mat_properties, "arcade_enabled", "Enable")
        utils.draw_input_row(layout, selected_object.mat_properties, "arcade_start_color", "Start Front Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "arcade_end_color", "End Front Color")
        utils.draw_input_row(layout, selected_object.mat_properties, "arcade_sharp_color", "Sharp Color")

      # FLIPBOOK
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_flipbook", "Flipbook", 'SEQ_SEQUENCER')
      if opened:
        layout.separator()
        layout.operator("object.material_add_animation")
        layout.operator("object.material_remove_animation")
        layout.separator(type="LINE")
        # Row for each animation
        for i, anim in enumerate(context.object.material_animations):
          col = layout.column()
          row1 = col.row()
          utils.draw_input_row(col, context.object.material_animations[i], "texture_target", "Texture Target")
          utils.draw_input_row(col, context.object.material_animations[i], "frame_width", "Frame Width")
          utils.draw_input_row(col, context.object.material_animations[i], "frame_height", "Frame Height")
          utils.draw_input_row(col, context.object.material_animations[i], "frame_duration", "Frame Duration")
          utils.draw_input_row(col, context.object.material_animations[i], "num_col", "Num Col")
          utils.draw_input_row(col, context.object.material_animations[i], "num_row", "Num Row")
          utils.draw_input_row(col, context.object.material_animations[i], "num_frames", "Num Frames")
          layout.separator(type="LINE")
        #endfor

      # CUSTOM PARAMS
      box, opened = utils.draw_foldout(layout, selected_object.mat_properties, "show_custom_params", "Custom Params", 'RNA')
      if opened:
        row = layout.row()
        row.prop(selected_object.mat_properties, "s00_name", text="")
        row.prop(selected_object.mat_properties, "s00_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s01_name", text="")
        row.prop(selected_object.mat_properties, "s01_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s02_name", text="")
        row.prop(selected_object.mat_properties, "s02_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s03_name", text="")
        row.prop(selected_object.mat_properties, "s03_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s04_name", text="")
        row.prop(selected_object.mat_properties, "s04_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s05_name", text="")
        row.prop(selected_object.mat_properties, "s05_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s06_name", text="")
        row.prop(selected_object.mat_properties, "s06_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s07_name", text="")
        row.prop(selected_object.mat_properties, "s07_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s08_name", text="")
        row.prop(selected_object.mat_properties, "s08_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s09_name", text="")
        row.prop(selected_object.mat_properties, "s09_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s10_name", text="")
        row.prop(selected_object.mat_properties, "s10_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s11_name", text="")
        row.prop(selected_object.mat_properties, "s11_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s12_name", text="")
        row.prop(selected_object.mat_properties, "s12_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s13_name", text="")
        row.prop(selected_object.mat_properties, "s13_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s14_name", text="")
        row.prop(selected_object.mat_properties, "s14_value", text="")
        row = layout.row()
        row.prop(selected_object.mat_properties, "s15_name", text="")
        row.prop(selected_object.mat_properties, "s15_value", text="")
        layout.separator()
        row = layout.row()
        utils.draw_input_row(row, selected_object.mat_properties, "s0_texture", "Texture S0")
        row = layout.row()
        utils.draw_input_row(row, selected_object.mat_properties, "s1_texture", "Texture S1")
      #endif
    # END JSM/JAM


class WARME_PT_grf_node_editor(bpy.types.Panel):
  bl_label = "Legacy GRF"
  bl_idname = "VIEW3D_PT_grf_node_editor"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = 'Legacy GRF'

  def draw(self, context):
    selected = bpy.context.selected_objects
    if selected and len(selected) == 1 and utils.belong_to_collection(bpy.context.selected_objects[0], "GRF"):
      layout = self.layout
      scene = context.scene
      obj = context.active_object

      if not obj or obj.type != 'MESH':
        layout.label(text="Sélectionnez un Mesh", icon='ERROR')
        return
      #if

      box = layout.box()
      box.label(text="Données du Nœud", icon='DOT')
      
      row = box.row(align=True)
      row.prop(scene, "grf_node_type", text="Type")
      row.operator("mesh.grf_apply_node_meta", text="Appliquer")

      # Infos en mode Edit
      if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        active = bm.select_history.active
        if active and isinstance(active, bmesh.types.BMVert):
          layer = bm.verts.layers.string.get("grf_node_type")
          val = active[layer] if layer else 0
          box.label(text=f"Sommet {active.index} | Type Actuel: {val.decode('utf-8')}", icon='INFO')
        #if
      #if
    #if