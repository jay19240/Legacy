import bpy
from . import utils
# ----------------------------------------------------------------------------------


def register():
  bpy.utils.register_class(TweenColor)
  bpy.utils.register_class(TweenNumber)
  bpy.utils.register_class(TweenVector3)

  bpy.utils.register_class(JamAnimation)
  bpy.types.Object.jam_animations = bpy.props.CollectionProperty(type=JamAnimation)
  
  bpy.utils.register_class(MaterialAnimation)
  bpy.types.Object.material_animations = bpy.props.CollectionProperty(type=MaterialAnimation)
  
  bpy.utils.register_class(WARME_PG_MatProperties)
  bpy.types.Object.mat_properties = bpy.props.PointerProperty(type=WARME_PG_MatProperties)
  
  bpy.utils.register_class(WARME_PG_LightProperties)
  bpy.types.Object.light_properties = bpy.props.PointerProperty(type=WARME_PG_LightProperties)

  bpy.utils.register_class(WARME_PG_SunProperties)
  bpy.types.Object.sun_properties = bpy.props.PointerProperty(type=WARME_PG_SunProperties)

  bpy.utils.register_class(WARME_PG_WorldProperties)
  bpy.types.Scene.world_properties = bpy.props.PointerProperty(type=WARME_PG_WorldProperties)

  bpy.utils.register_class(WARME_PG_DecalProperties)
  bpy.types.Object.decal_properties = bpy.props.PointerProperty(type=WARME_PG_DecalProperties)

  bpy.utils.register_class(WARME_PG_ShadowProperties)
  bpy.types.Object.shadow_properties = bpy.props.PointerProperty(type=WARME_PG_ShadowProperties)

  bpy.utils.register_class(WARME_PG_SkyboxProperties)
  bpy.types.Object.skybox_properties = bpy.props.PointerProperty(type=WARME_PG_SkyboxProperties)

  bpy.utils.register_class(WARME_PG_ParticlesProperties)
  bpy.types.Object.particles_properties = bpy.props.PointerProperty(type=WARME_PG_ParticlesProperties)

  bpy.utils.register_class(WARME_PG_EntityProperties)
  bpy.types.Object.entity_properties = bpy.props.PointerProperty(type=WARME_PG_EntityProperties)

  bpy.utils.register_class(WARME_PG_WaterProperties)
  bpy.types.Object.water_properties = bpy.props.PointerProperty(type=WARME_PG_WaterProperties)

  bpy.types.Scene.export_assets_path = bpy.props.StringProperty(name="Assets Path", default="", subtype='FILE_PATH')
  bpy.types.Scene.export_engine_path = bpy.props.StringProperty(name="Engine Path", default="", subtype='FILE_PATH')
  bpy.types.Scene.auggie_prompt = bpy.props.StringProperty(name="Prompt", default="Write your prompt here...")
  bpy.types.Scene.auggie_status = bpy.props.StringProperty(name="Status", default="Ready")
  bpy.types.Scene.auggie_output = bpy.props.StringProperty(name="Output", default="")
  bpy.types.Scene.grf_node_type = bpy.props.StringProperty(name="Node Type", default="")

def unregister():
  bpy.utils.unregister_class(TweenColor)
  bpy.utils.unregister_class(TweenNumber)
  bpy.utils.unregister_class(TweenVector3)
  bpy.utils.unregister_class(JamAnimation)
  bpy.utils.unregister_class(MaterialAnimation)
  bpy.utils.unregister_class(WARME_PG_MatProperties)
  bpy.utils.unregister_class(WARME_PG_LightProperties)
  bpy.utils.unregister_class(WARME_PG_SunProperties)
  bpy.utils.unregister_class(WARME_PG_WorldProperties)
  bpy.utils.unregister_class(WARME_PG_DecalProperties)
  bpy.utils.unregister_class(WARME_PG_ShadowProperties)
  bpy.utils.unregister_class(WARME_PG_SkyboxProperties)
  bpy.utils.unregister_class(WARME_PG_ParticlesProperties)
  bpy.utils.unregister_class(WARME_PG_EntityProperties)
  bpy.utils.unregister_class(WARME_PG_WaterProperties)
  del bpy.types.Scene.export_assets_path
  del bpy.types.Scene.export_engine_path
  del bpy.types.Scene.auggie_prompt
  del bpy.types.Scene.auggie_status
  del bpy.types.Scene.auggie_output
  del bpy.types.Scene.grf_node_type


# -------------------------------------------------------------------------------
# UTILS
# -------------------------------------------------------------------------------
def deferred_export():
  bpy.ops.object.export_pack()
  return None

def update_trigger_export(self, context):
  auto_export_enabled = context.scene.world_properties.enable_auto_export

  if bpy.app.timers.is_registered(deferred_export):
    bpy.app.timers.unregister(deferred_export)
  #endif
  
  if auto_export_enabled:
    bpy.app.timers.register(deferred_export, first_interval=1)
  #endif

def update_camera_projection_type_bind(self, context):
  camera = bpy.data.objects["Camera"]
  if self.camera_projection_type_bind == 'PERSPECTIVE':
    camera.data.type = 'PERSP'
    update_trigger_export(self, context)
  elif self.camera_projection_type_bind == 'ORTHOGRAPHIC':
    camera.data.type = 'ORTHO'
    update_trigger_export(self, context)

def update_camera_fovy_bind(self, context):
  camera = bpy.data.objects["Camera"]
  camera.data.angle_y = self.camera_fovy_bind
  update_trigger_export(self, context)

def update_camera_near_bind(self, context):
  camera = bpy.data.objects["Camera"]
  camera.data.clip_start = self.camera_near_bind
  update_trigger_export(self, context)

def update_camera_far_bind(self, context):
  camera = bpy.data.objects["Camera"]
  camera.data.clip_end = self.camera_far_bind
  update_trigger_export(self, context)

def update_ortho_size_bind(self, context):
  camera = bpy.data.objects["Camera"]
  camera.data.ortho_scale = self.camera_ortho_size_bind
  update_trigger_export(self, context)

def update_texture_path_bind(self, context):
  image_path = self.texture
  obj = context.active_object

  if obj and image_path:
    if not obj.data.materials:
      mat = bpy.data.materials.new(name="Material_Auto")
      mat.use_nodes = True
      obj.data.materials.append(mat)
    #endif
      
    mat = obj.active_material
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    tex_node = nodes.get("AutoTexture") or nodes.new('ShaderNodeTexImage')
    tex_node.name = "AutoTexture"

    update_trigger_export(self, context)
    
    try:
      img = bpy.data.images.load(image_path)
      tex_node.image = img
      bsdf = nodes.get("Principled BSDF")
      if bsdf:
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    except:
      print("Erreur lors du chargement de l'image")
    #except
  else:
    if obj.data.materials:
      mat = obj.active_material
      obj.data.materials.pop(index=obj.active_material_index)
      if mat and mat.users == 0:
        bpy.data.materials.remove(mat)
      #endif
    #endif
  #endif

def update_shadow_size(self, context):
  shadow = bpy.data.objects["ShadowProjector"]
  shadow.scale[0] = self.size
  shadow.scale[1] = self.size
  update_trigger_export(self, context)

def update_shadow_depth(self, context):
  shadow = bpy.data.objects["ShadowProjector"]
  shadow.scale[2] = self.depth
  update_trigger_export(self, context)


# -------------------------------------------------------------------------------
# PROPERTIES
# -------------------------------------------------------------------------------
class TweenColor(bpy.types.PropertyGroup):
  time: bpy.props.FloatProperty(name="Time")
  value: bpy.props.FloatVectorProperty(name="Value", subtype='COLOR', default=(1.0, 1.0, 1.0), min=0.0, max=1.0)


class TweenVector3(bpy.types.PropertyGroup):
  time: bpy.props.FloatProperty(name="Time")
  value: bpy.props.FloatVectorProperty(name="Value", subtype='NONE', default=(0.0, 0.0, 0.0))


class TweenNumber(bpy.types.PropertyGroup):
  time: bpy.props.FloatProperty(name="Time")
  value: bpy.props.FloatProperty(name="Value")


class JamAnimation(bpy.types.PropertyGroup):
  name: bpy.props.StringProperty(name="Name")
  start_frame: bpy.props.IntProperty(name="Start frame")
  end_frame: bpy.props.IntProperty(name="End frame")
  frame_duration: bpy.props.IntProperty(name="Frame Duration")


class MaterialAnimation(bpy.types.PropertyGroup):
  texture_target: bpy.props.EnumProperty(name="Texture Target", items=[
    ('Texture', "Texture", "The albedo texture"),
    ('SecondaryTexture', "SecondaryTexture", "The second texture"),
    ('DisplacementTexture', "DisplacementTexture", "The displacement texture"),
    ('DissolveTexture', "DissolveTexture", "The dissolve texture")
  ])

  frame_width: bpy.props.IntProperty(name="Frame Width")
  frame_height: bpy.props.IntProperty(name="Frame Height")
  num_col: bpy.props.IntProperty(name="Num Col")
  num_row: bpy.props.IntProperty(name="Num Row")
  num_frames: bpy.props.IntProperty(name="Num Frames")
  frame_duration: bpy.props.IntProperty(name="Frame Duration")


class WARME_PG_MatProperties(bpy.types.PropertyGroup):
  show_transform_infos: bpy.props.BoolProperty(
    name="Transform Infos",
    default=False
  )
  show_animation: bpy.props.BoolProperty(
    name="Animation",
    default=False
  )
  show_general: bpy.props.BoolProperty(
    name="General",
    default=False
  )
  show_shadow: bpy.props.BoolProperty(
    name="Shadow",
    default=False
  )
  show_decals: bpy.props.BoolProperty(
    name="Decals",
    default=False
  )
  show_light: bpy.props.BoolProperty(
    name="Light",
    default=False
  )
  show_sampler: bpy.props.BoolProperty(
    name="Sampler",
    default=False
  )
  show_texture: bpy.props.BoolProperty(
    name="Texture",
    default=False
  )
  show_secondary_texture: bpy.props.BoolProperty(
    name="Secondary Texture",
    default=False
  )
  show_env_map: bpy.props.BoolProperty(
    name="Env Map",
    default=False
  )
  show_normal_map: bpy.props.BoolProperty(
    name="Normal Map",
    default=False
  )
  show_displacement_map: bpy.props.BoolProperty(
    name="Displacement Map",
    default=False
  )
  show_dissolve_map: bpy.props.BoolProperty(
    name="Dissolve Map",
    default=False
  )
  show_toon_map: bpy.props.BoolProperty(
    name="Toon Map",
    default=False
  )
  show_emissive_map: bpy.props.BoolProperty(
    name="Emissive Map",
    default=False
  )
  show_diffuse_map: bpy.props.BoolProperty(
    name="Diffuse Map",
    default=False
  )
  show_specular_map: bpy.props.BoolProperty(
    name="Specular Map",
    default=False
  )
  show_thune_map: bpy.props.BoolProperty(
    name="Thune Map",
    default=False
  )
  show_alpha_blend: bpy.props.BoolProperty(
    name="Alpha Blend",
    default=False
  )
  show_jitter_vertex: bpy.props.BoolProperty(
    name="Jitter Vertex",
    default=False
  )
  show_arcade: bpy.props.BoolProperty(
    name="Arcade",
    default=False
  )
  show_flipbook: bpy.props.BoolProperty(
    name="Flipbook",
    default=False
  )
  show_custom_params: bpy.props.BoolProperty(
    name="Custom Params",
    default=False
  )
  # ----------------------------------------------------------------------------------
  id: bpy.props.IntProperty(
    name="Id",
    description="Set the material identifier",
    default=0,
    update=update_trigger_export
  )
  opacity: bpy.props.FloatProperty(
    name="Opacity",
    description="Set the global opacity",
    default=1.0,
    min=0.0, max=1,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  shadow_enabled: bpy.props.BoolProperty(
    name="Shadow Enabled",
    description="Enable shadow or not",
    default=False,
    update=update_trigger_export
  )
  shadow_casting: bpy.props.BoolProperty(
    name="Shadow Casting",
    description="Enable the object to cast shadow on others",
    default=False,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  decal_enabled: bpy.props.BoolProperty(
    name="Decal Enabled",
    description="Enable the capacity of the material to receive a decal or not",
    default=False,
    update=update_trigger_export
  )
  decal_group: bpy.props.IntProperty(
    name="Decal Group Identifier",
    description="Set the decal group that affect this object",
    default=0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  light_enabled: bpy.props.BoolProperty(
    name="Light Enabled",
    description="Enable the light reactivity or not",
    default=False,
    update=update_trigger_export
  )
  light_group: bpy.props.IntProperty(
    name="Light Group Identifier",
    description="Set the light group that affect this object",
    default=0,
    update=update_trigger_export
  )
  light_gouraud_shading_enabled: bpy.props.BoolProperty(
    name="Light Gouraud Shading Enabled",
    description="Enable the light gouraud shading or not",
    default=False,
    update=update_trigger_export
  )
  light_emissive_factor: bpy.props.FloatProperty(
    name="Emissive Factor",
    description="Set the strength of the emissive color",
    default=0.0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  light_emissive_color: bpy.props.FloatVectorProperty(
    name="Emissive Color",
    description="Set the emissive color. Not used if emissive map is set.",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  light_ambient_color: bpy.props.FloatVectorProperty(
    name="Ambient Color",
    description="Set the ambiant color. If zero the scene ambient color is used.",
    subtype='COLOR',
    default=(0.5, 0.5, 0.5),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  light_diffuse_color: bpy.props.FloatVectorProperty(
    name="Diffuse Color",
    description="Set the diffuse color. Not used if diffuse map is set.",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  light_specular_factor: bpy.props.FloatProperty(
    name="Specular Factor",
    description="Set the strength of the specular effect",
    default=0.0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  light_specular_color: bpy.props.FloatVectorProperty(
    name="Specular Color",
    description="Set the specular color. Not used if specular map is set.",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  sampler_enabled: bpy.props.BoolProperty(
    name="Sampler Enabled",
    description="Enable the texture sampler settings",
    default=False,
    update=update_trigger_export
  )
  sampler_address_mode_u: bpy.props.EnumProperty(
    name="Address Mode U",
    description="Set texture apply mode (U axis)",
    items=[
        ('clamp-to-edge', "Clamp To Edge", "Repeat the last pixel of the border"),
        ('repeat', "Repeat", "Repeat the texture"),
        ('mirror-repeat', "Mirror Repeat", "Repeat the mirrored texture"),
    ],
    default='clamp-to-edge',
    update=update_trigger_export
  )
  sampler_address_mode_v: bpy.props.EnumProperty(
    name="Address Mode V",
    description="Set texture apply mode (V axis)",
    items=[
        ('clamp-to-edge', "Clamp To Edge", "Repeat the last pixel of the border"),
        ('repeat', "Repeat", "Repeat the texture"),
        ('mirror-repeat', "Mirror Repeat", "Repeat the mirrored texture"),
    ],
    default='clamp-to-edge',
    update=update_trigger_export
  )
  sampler_address_mode_w: bpy.props.EnumProperty(
    name="Address Mode W",
    description="Set texture apply mode (W axis)",
    items=[
        ('clamp-to-edge', "Clamp To Edge", "Repeat the last pixel of the border"),
        ('repeat', "Repeat", "Repeat the texture"),
        ('mirror-repeat', "Mirror Repeat", "Repeat the mirrored texture"),
    ],
    default='clamp-to-edge',
    update=update_trigger_export
  )
  sampler_mag_filter: bpy.props.EnumProperty(
    name="Mag Filter",
    description="Set the filter strategy used on texture scale up",
    items=[
        ('nearest', "Nearest", "The nearest strategy on texture scale up"),
        ('linear', "Linear", "The linear strategy on texture scale up"),
    ],
    default='nearest',
    update=update_trigger_export
  )
  sampler_min_filter: bpy.props.EnumProperty(
    name="Min Filter",
    description="Set the filter strategy used on texture scale down",
    items=[
        ('nearest', "Nearest", "The nearest strategy on texture scale down"),
        ('linear', "Linear", "The linear strategy on texture scale down"),
    ],
    default='nearest',
    update=update_trigger_export
  )
  sampler_mipmap_filter: bpy.props.EnumProperty(
    name="MipMap Filter",
    description="Set the filter strategy used on transition between mip levels",
    items=[
        ('nearest', "Nearest", "The nearest strategy"),
        ('linear', "Linear", "The linear strategy"),
    ],
    default='nearest',
    update=update_trigger_export
  )
  sampler_lod_min_clamp: bpy.props.FloatProperty(
    name="LOD Min Clamp",
    description="Set the minimum level of detail allowed for this texture (0, 1, 2, 3, 4...) from more to less quality",
    default=0.0,
    update=update_trigger_export
  )
  sampler_lod_max_clamp: bpy.props.FloatProperty(
    name="LOD Max Clamp",
    description="Set the maximum level of detail allowed for this texture (0, 1, 2, 3, 4...) from more to less quality",
    default=0.0,
    update=update_trigger_export
  )
  sampler_max_anisotropy: bpy.props.FloatProperty(
    name="Max Anisotropy",
    description="Set Anisotropy filter. MaxAnisotropy sharpens textures viewed at steep angles by sampling along the direction of perspective distortion",
    default=1.0,
    update=update_trigger_export
  )
  sampler_type: bpy.props.EnumProperty(
    name="Type",
    description="Set the type of the texture",
    items=[
        ('Mips', "Mips", "Mipmaps Texture"),
        ('None', "None", "Classic Texture"),
    ],
    default='None',
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  texture: bpy.props.StringProperty(
    name="Texture",
    description="Set the albedo texture",
    default="",
    subtype='FILE_PATH',
    update=update_texture_path_bind
  )
  texture_scroll_angle: bpy.props.FloatProperty(
    name="Texture Scroll Angle",
    description="Set the scroll angle of the texture",
    default=0,
    update=update_trigger_export
  )
  texture_scroll_rate: bpy.props.FloatProperty(
    name="Texture Scroll Rate",
    description="Set the scroll rate of the texture",
    default=0,
    update=update_trigger_export
  )
  texture_offset: bpy.props.FloatVectorProperty(
    name="Texture Offset",
    description="Set the uv offset of the texture",
    default=(0.0, 0.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  texture_scale: bpy.props.FloatVectorProperty(
    name="Texture Scale",
    description="Set the uv scale of the texture",
    default=(1.0, 1.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  texture_rotation_angle: bpy.props.FloatProperty(
    name="Texture Rotation Angle",
    description="Set the rotation angle of the texture",
    default=0,
    update=update_trigger_export
  )
  texture_opacity: bpy.props.FloatProperty(
    name="Texture Opacity",
    description="Set the opacity of the texture",
    default=1.0,
    min=0.0, max=1,
    update=update_trigger_export
  )
  texture_blend_color: bpy.props.FloatVectorProperty(
    name="Texture Blend Color",
    description="Set the texture blend color",
    default=(1.0, 1.0, 1.0),
    subtype='COLOR',
    update=update_trigger_export
  )
  texture_blend_color_mode: bpy.props.EnumProperty(
    name="Texture Blend Color Mode",
    items=[
      ('NONE', "NONE", "None"),
      ('MUL', "MUL", "Multiply"),
      ('ADD', "ADD", "Add"),
      ('MIX', "MIX", "Mix")
    ],
    description="Set the texture blend color mode",
    default='NONE',
    update=update_trigger_export
  )
  texture_blend_color_mix: bpy.props.FloatProperty(
    name="Texture Blend Color Mix",
    description="Set the texture blend color mix",
    default=1.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  secondary_texture: bpy.props.StringProperty(
    name="Secondary Texture",
    description="Set the secondary texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  secondary_texture_scroll_angle: bpy.props.FloatProperty(
    name="Secondary Texture Scroll Angle",
    description="Set the scroll angle of the secondary texture",
    default=0,
    update=update_trigger_export
  )
  secondary_texture_scroll_rate: bpy.props.FloatProperty(
    name="Secondary Texture Scroll Rate",
    description="Set the scroll rate of the secondary texture",
    default=0,
    update=update_trigger_export
  )
  secondary_texture_offset: bpy.props.FloatVectorProperty(
    name="Secondary Texture Offset",
    description="Set the uv offset of the secondary texture",
    default=(0.0, 0.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  secondary_texture_scale: bpy.props.FloatVectorProperty(
    name="Secondary Texture Scale",
    description="Set the uv scale of the secondary texture",
    default=(1.0, 1.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  secondary_texture_rotation_angle: bpy.props.FloatProperty(
    name="Secondary Texture Rotation Angle",
    description="Set the rotation angle of the secondary texture",
    default=0,
    update=update_trigger_export
  )
  secondary_texture_opacity: bpy.props.FloatProperty(
    name="Secondary Texture Opacity",
    description="Set the opacity of the secondary texture",
    default=1.0,
    min=0.0, max=1,
    update=update_trigger_export
  )
  secondary_texture_blend_mode: bpy.props.EnumProperty(
    name="Secondary Texture Blend Mode",
    items=[
      ('NONE', "NONE", "None"),
      ('MUL', "MUL", "Multiply"),
      ('ADD', "ADD", "Add"),
      ('MIX', "MIX", "Mix")
    ],
    description="Set the secondary texture blend mode",
    default='NONE',
    update=update_trigger_export
  )
  secondary_texture_blend_color: bpy.props.FloatVectorProperty(
    name="Secondary Texture Blend Color",
    description="Set the secondary texture blend color",
    default=(1.0, 1.0, 1.0),
    subtype='COLOR',
    update=update_trigger_export
  )
  secondary_texture_blend_color_mode: bpy.props.EnumProperty(
    name="Secondary Texture Blend Color Mode",
    items=[
      ('NONE', "NONE", "None"),
      ('MUL', "MUL", "Multiply"),
      ('ADD', "ADD", "Add"),
      ('MIX', "MIX", "Mix")
    ],
    description="Set the secondary texture blend color mode",
    default='NONE',
    update=update_trigger_export
  )
  secondary_texture_blend_color_mix: bpy.props.FloatProperty(
    name="Secondary Texture Blend Color Mix",
    description="Set the secondary texture blend color mix",
    default=0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  env_map_name: bpy.props.StringProperty(
    name="Env Map Name",
    description="Set the env map name",
    default="",
    update=update_trigger_export
  )
  env_map_right: bpy.props.StringProperty(
    name="Env Map Right",
    description="Set the env map right texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  env_map_left: bpy.props.StringProperty(
    name="Env Map Left",
    description="Set the env map left texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  env_map_top: bpy.props.StringProperty(
    name="Env Map Top",
    description="Set the env map top texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  env_map_bottom: bpy.props.StringProperty(
    name="Env Map Bottom",
    description="Set the env map bottom texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  env_map_front: bpy.props.StringProperty(
    name="Env Map Front",
    description="Set the env map front texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  env_map_back: bpy.props.StringProperty(
    name="Env Map Back",
    description="Set the env map back texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  env_map_opacity: bpy.props.FloatProperty(
    name="Env Map Opacity",
    description="Set the env map reflexion opacity",
    default=1.0,
    min=0.0, max=1,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  normal_map: bpy.props.StringProperty(
    name="Normal Map",
    description="Set the normal map texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  normal_map_scroll_angle: bpy.props.FloatProperty(
    name="Normal Map Scroll Angle",
    description="Set the normal map scroll angle",
    default=0,
    update=update_trigger_export
  )
  normal_map_scroll_rate: bpy.props.FloatProperty(
    name="Normal Map Scroll Rate",
    description="Set the normal map scroll rate",
    default=0,
    update=update_trigger_export
  )
  normal_map_offset: bpy.props.FloatVectorProperty(
    name="Normal Map Offset",
    description="Set the normal map offset",
    default=(0.0, 0.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  normal_map_scale: bpy.props.FloatVectorProperty(
    name="Normal Map Scale",
    description="Set the normal map scale",
    default=(1.0, 1.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  normal_map_rotation_angle: bpy.props.FloatProperty(
    name="Normal Map Rotation Angle",
    description="Set the normal map rotation angle",
    default=0,
    update=update_trigger_export
  )
  normal_map_intensity: bpy.props.FloatProperty(
    name="Normal Map Intensity",
    description="Set the normal map intensity",
    default=1,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  displacement_map: bpy.props.StringProperty(
    name="Displacement Map",
    description="Set the displacement map texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  displacement_map_scroll_angle: bpy.props.FloatProperty(
    name="Displacement Map Scroll Angle",
    description="Set the scroll angle of the displacement map",
    default=0,
    update=update_trigger_export
  )
  displacement_map_scroll_rate: bpy.props.FloatProperty(
    name="Displacement Map Scroll Rate",
    description="Set the scroll rate of the displacement map",
    default=0,
    update=update_trigger_export
  )
  displacement_map_offset: bpy.props.FloatVectorProperty(
    name="Displacement Map Offset",
    description="Set the uv offset of the displacement map",
    default=(0.0, 0.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  displacement_map_scale: bpy.props.FloatVectorProperty(
    name="Displacement Map Scale",
    description="Set the uv scale of the displacement map",
    default=(1.0, 1.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  displacement_map_rotation_angle: bpy.props.FloatProperty(
    name="Displacement Map Rotation Angle",
    description="Set the rotation angle of the displacement map",
    default=0,
    update=update_trigger_export
  )
  displacement_map_factor: bpy.props.FloatProperty(
    name="Displacement Map Factor",
    description="Set the displacement map factor",
    default=0,
    update=update_trigger_export
  )
  displace_texture: bpy.props.BoolProperty(
    name="Albedo Texture",
    description="Enable displacement for the albedo texture",
    default=False,
    update=update_trigger_export
  )
  displace_secondary_texture: bpy.props.BoolProperty(
    name="Secondary Texture",
    description="Enable displacement for the secondary texture",
    default=False,
    update=update_trigger_export
  )
  displace_normal_map: bpy.props.BoolProperty(
    name="Normal Map",
    description="Enable displacement for the normal map",
    default=False,
    update=update_trigger_export
  )
  displace_dissolve_map: bpy.props.BoolProperty(
    name="Dissolve Map",
    description="Enable displacement for the dissolve map",
    default=False,
    update=update_trigger_export
  )
  displace_env_map: bpy.props.BoolProperty(
    name="Env Map",
    description="Enable displacement for the env map",
    default=False,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  dissolve_map: bpy.props.StringProperty(
    name="Dissolve Map",
    description="Set the dissolve map texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  dissolve_map_scroll_angle: bpy.props.FloatProperty(
    name="Dissolve Map Scroll Angle",
    description="Set the scroll angle of the dissolve map",
    default=0,
    update=update_trigger_export
  )
  dissolve_map_scroll_rate: bpy.props.FloatProperty(
    name="Dissolve Map Scroll Rate",
    description="Set the scroll rate of the dissolve map",
    default=0,
    update=update_trigger_export
  )
  dissolve_map_offset: bpy.props.FloatVectorProperty(
    name="Dissolve Map Offset",
    description="Set the uv offset of the dissolve map",
    default=(0.0, 0.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  dissolve_map_scale: bpy.props.FloatVectorProperty(
    name="Dissolve Map Scale",
    description="Set the uv scale of the dissolve map",
    default=(1.0, 1.0),
    subtype='NONE',
    size=2,
    update=update_trigger_export
  )
  dissolve_map_rotation_angle: bpy.props.FloatProperty(
    name="Dissolve Map Rotation Angle",
    description="Set the rotation angle of the dissolve map",
    default=0,
    update=update_trigger_export
  )
  dissolve_glow: bpy.props.FloatVectorProperty(
    name="Dissolve Glow Color",
    description="Set the glow color of the dissolve",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  dissolve_glow_range: bpy.props.FloatProperty(
    name="Dissolve Glow Range",
    description="Set the glow range of the dissolve",
    default=0,
    min=0.0, max=0.5,
    update=update_trigger_export
  )
  dissolve_glow_falloff: bpy.props.FloatProperty(
    name="Dissolve Glow Falloff",
    description="Set the glow falloff of the dissolve",
    default=0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  dissolve_amount: bpy.props.FloatProperty(
    name="Dissolve Amount",
    description="Set the dissolve amount",
    default=0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  toon_map: bpy.props.StringProperty(
    name="Toon texture",
    description="Set the toon map texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  toon_map_opacity: bpy.props.FloatProperty(
    name="Toon Map Opacity",
    description="Set the opacity of the toon map effect",
    default=1.0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  toon_light_dir: bpy.props.FloatVectorProperty(
    name="Toon Light Direction",
    description="Set the light direction",
    default=(0.0, 0.0, 0.0),
    subtype='XYZ',
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  emissive_map: bpy.props.StringProperty(
    name="Emissive Map",
    description="Set the emissive color map texture. Override emissive color.",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  diffuse_map: bpy.props.StringProperty(
    name="Diffuse Map",
    description="Set the diffuse map texture. Override diffuse color.",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  specular_map: bpy.props.StringProperty(
    name="Specular Map",
    description="Set the specular map texture. Override specular color.",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  thune_map: bpy.props.StringProperty(
    name="Thune Map",
    description="Set the thune map texture. Thune map is used to map shininess (R), arcade (G) and reflective environment (B) in one texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  thune_map_shininess_enabled: bpy.props.BoolProperty(
    name="Shininess Enabled (R)",
    description="Enable shininess from thune map (R)",
    default=False,
    update=update_trigger_export
  )
  thune_map_arcade_enabled: bpy.props.BoolProperty(
    name="Arcade Enabled (G)",
    description="Enable arcade from thune map (G)",
    default=False,
    update=update_trigger_export
  )
  thune_map_reflective_enabled: bpy.props.BoolProperty(
    name="Reflective Enabled (G)",
    description="Enable reflective from thune map (G)",
    default=False,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  alpha_blend_enabled: bpy.props.BoolProperty(
    name="Alpha Blend Enabled",
    description="Enable alpha blending effect",
    default=False,
    update=update_trigger_export
  )
  alpha_blend_facing: bpy.props.FloatProperty(
    name="Alpha Blend Facing",
    description="Set the facing transparency based on view angle",
    default=1.0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  alpha_blend_distance: bpy.props.FloatProperty(
    name="Alpha Blend Distance",
    description="Set the transparency based on view distance",
    default=0.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  jitter_vertex_enabled: bpy.props.BoolProperty(
    name="Vertex Jittering Enabled",
    description="Enable vertex jittering or not",
    default=False,
    update=update_trigger_export
  )
  jitter_vertex_level: bpy.props.FloatProperty(
    name="Vertex Jittering Level",
    description="Set the strength of the vertex jittering",
    default=120.0,
    min=0.0, max=1000.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  arcade_enabled: bpy.props.BoolProperty(
    name="Arcade Shading Enabled",
    description="Arcade shading handle the reflection color based on view angle",
    default=False,
    update=update_trigger_export
  )
  arcade_start_color: bpy.props.FloatVectorProperty(
    name="Arcade Start Color",
    description="Set the start color applied to pixel when facing the camera (interpolate with view direction)",
    subtype='COLOR',
    default=(1.0, 0.0, 0.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  arcade_end_color: bpy.props.FloatVectorProperty(
    name="Arcade End Color",
    description="Set the end color applied to pixel when facing the camera (interpolate with view direction)",
    subtype='COLOR',
    default=(1.0, 0.0, 0.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  arcade_sharp_color: bpy.props.FloatVectorProperty(
    name="Arcade Sharp Color",
    description="Set the color with an angle greater than 90 degrees with the camera",
    subtype='COLOR',
    default=(0.1, 0.1, 0.1),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  s00_name: bpy.props.StringProperty(
    name="S00",
    description="Custom slot name 00",
    default="S00",
    update=update_trigger_export
  )
  s00_value: bpy.props.FloatProperty(
    name="S00",
    description="Custom slot value 00",
    update=update_trigger_export
  )
  s01_name: bpy.props.StringProperty(
    name="S01",
    description="Custom slot name 01",
    default="S01",
    update=update_trigger_export
  )
  s01_value: bpy.props.FloatProperty(
    name="S01",
    description="Custom slot value 01",
    update=update_trigger_export
  )
  s02_name: bpy.props.StringProperty(
    name="S02",
    description="Custom slot name 02",
    default="S02",
    update=update_trigger_export
  )
  s02_value: bpy.props.FloatProperty(
    name="S02",
    description="Custom slot value 02",
    update=update_trigger_export
  )
  s03_name: bpy.props.StringProperty(
    name="S03",
    description="Custom slot name 03",
    default="S03",
    update=update_trigger_export
  )
  s03_value: bpy.props.FloatProperty(
    name="S03",
    description="Custom slot value 03",
    update=update_trigger_export
  )
  s04_name: bpy.props.StringProperty(
    name="S04",
    description="Custom slot name 04",
    default="S04",
    update=update_trigger_export
  )
  s04_value: bpy.props.FloatProperty(
    name="S04",
    description="Custom slot value 04",
    update=update_trigger_export
  )
  s05_name: bpy.props.StringProperty(
    name="S05",
    description="Custom slot name 05",
    default="S05",
    update=update_trigger_export
  )
  s05_value: bpy.props.FloatProperty(
    name="S05",
    description="Custom slot value 05",
    update=update_trigger_export
  )
  s06_name: bpy.props.StringProperty(
    name="S06",
    description="Custom slot name 06",
    default="S06",
    update=update_trigger_export
  )
  s06_value: bpy.props.FloatProperty(
    name="S06",
    description="Custom slot value 06",
    update=update_trigger_export
  )
  s07_name: bpy.props.StringProperty(
    name="S07",
    description="Custom slot name 07",
    default="S07",
    update=update_trigger_export
  )
  s07_value: bpy.props.FloatProperty(
    name="S07",
    description="Custom slot value 07",
    update=update_trigger_export
  )
  s08_name: bpy.props.StringProperty(
    name="S08",
    description="Custom slot name 08",
    default="S08",
    update=update_trigger_export
  )
  s08_value: bpy.props.FloatProperty(
    name="S08",
    description="Custom slot value 08",
    update=update_trigger_export
  )
  s09_name: bpy.props.StringProperty(
    name="S09",
    description="Custom slot name 09",
    default="S09",
    update=update_trigger_export
  )
  s09_value: bpy.props.FloatProperty(
    name="S09",
    description="Custom slot value 09",
    update=update_trigger_export
  )
  s10_name: bpy.props.StringProperty(
    name="S10",
    description="Custom slot name 10",
    default="S10",
    update=update_trigger_export
  )
  s10_value: bpy.props.FloatProperty(
    name="S10",
    description="Custom slot value 10",
    update=update_trigger_export
  )
  s11_name: bpy.props.StringProperty(
    name="S11",
    description="Custom slot name 11",
    default="S11",
    update=update_trigger_export
  )
  s11_value: bpy.props.FloatProperty(
    name="S11",
    description="Custom slot value 11",
    update=update_trigger_export
  )
  s12_name: bpy.props.StringProperty(
    name="S12",
    description="Custom slot name 12",
    default="S12",
    update=update_trigger_export
  )
  s12_value: bpy.props.FloatProperty(
    name="S12",
    description="Custom slot value 12",
    update=update_trigger_export
  )
  s13_name: bpy.props.StringProperty(
    name="S13",
    description="Custom slot name 13",
    default="S13",
    update=update_trigger_export
  )
  s13_value: bpy.props.FloatProperty(
    name="S13",
    description="Custom slot value 13",
    update=update_trigger_export
  )
  s14_name: bpy.props.StringProperty(
    name="S14",
    description="Custom slot name 14",
    default="S14",
    update=update_trigger_export
  )
  s14_value: bpy.props.FloatProperty(
    name="S14",
    description="Custom slot value 14",
    update=update_trigger_export
  )
  s15_name: bpy.props.StringProperty(
    name="S15",
    description="Custom slot name 15",
    default="S15",
    update=update_trigger_export
  )
  s15_value: bpy.props.FloatProperty(
    name="S15",
    description="Custom slot value 15",
    update=update_trigger_export
  )
  s0_texture: bpy.props.StringProperty(
    name="S0 Texture",
    description="Custom texture slot 0",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  s1_texture: bpy.props.StringProperty(
    name="S1 Texture",
    description="Custom texture slot 1",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )


class WARME_PG_WorldProperties(bpy.types.PropertyGroup):
  show_game: bpy.props.BoolProperty(
    name="Game",
    default=False
  )
  show_export: bpy.props.BoolProperty(
    name="Export",
    default=False
  )
  show_create: bpy.props.BoolProperty(
    name="Create",
    default=False
  )
  show_cast_to: bpy.props.BoolProperty(
    name="Cast To",
    default=False
  )
  show_camera: bpy.props.BoolProperty(
    name="Camera",
    default=False
  )
  show_world: bpy.props.BoolProperty(
    name="World",
    default=False
  )
  enable_auto_export: bpy.props.BoolProperty(
    name="Auto Export On Save",
    description="Export on save and property changes",
    default=False
  )
  enable_export_has_binary: bpy.props.BoolProperty(
    name="Export Has Binary",
    description="Export has binary or not",
    default=False
  )
  # camera ----------------------------------------------------------------------------------
  camera_projection_type_bind: bpy.props.EnumProperty(
    name="Projection",
    description="Set the projection type of the camera",
    items=[
        ('PERSPECTIVE', "Perspective", "Vue en perspective", 'VIEW_PERSPECTIVE', 0),
        ('ORTHOGRAPHIC', "Orthographique", "Vue orthographique", 'VIEW_ORTHO', 1),
    ],
    default='PERSPECTIVE',
    update=update_camera_projection_type_bind
  )
  camera_fovy_bind: bpy.props.FloatProperty(
    name="Fovy Angle (Degrees)",
    description="Set the field of view of the camera",
    default=45.0,
    update=update_camera_fovy_bind
  )
  camera_near_bind: bpy.props.FloatProperty(
    name="Near",
    description="Set the near clipping plane of the camera",
    default=1,
    update=update_camera_near_bind
  )
  camera_far_bind: bpy.props.FloatProperty(
    name="Far",
    description="Set the far clipping plane of the camera",
    default=2000.0,
    update=update_camera_far_bind
  )
  camera_ortho_size_bind: bpy.props.FloatProperty(
    name="Ortho Size",
    description="Set the orthographic scale of the camera",
    default=1.0,
    update=update_ortho_size_bind
  )
  camera_clip_offset: bpy.props.FloatVectorProperty(
    name="Engine Clip Offset",
    subtype='NONE',
    size=2,
    default=(0.0, 0.0),
    update=update_trigger_export
  )
  camera_min_clip_offset: bpy.props.FloatVectorProperty(
    name="Engine Min Clip Offset",
    subtype='NONE',
    size=2,
    default=(-1.0, -1.0),
    update=update_trigger_export
  )
  camera_max_clip_offset: bpy.props.FloatVectorProperty(
    name="Engine Max Clip Offset",
    subtype='NONE',
    size=2,
    default=(1.0, 1.0),
    update=update_trigger_export
  )
  camera_matrix_export_enabled: bpy.props.BoolProperty(
    name="Matrix Export Enabled",
    description="Enable camera matrix export or not",
    default=False,
    update=update_trigger_export
  )
  # world ----------------------------------------------------------------------------------
  fog_enabled: bpy.props.BoolProperty(
    name="Fog Enabled",
    description="Enable fog or not",
    default=False,
    update=update_trigger_export
  )
  fog_near: bpy.props.FloatProperty(
    name="Fog Near",
    description="Fog near distance",
    default=3.0,
    update=update_trigger_export
  )
  fog_far: bpy.props.FloatProperty(
    name="Fog Far",
    description="Fog far distance",
    default=15.0,
    update=update_trigger_export
  )
  fog_color: bpy.props.FloatVectorProperty(
    name="Fog Color",
    description="Fog color",
    subtype='COLOR',
    default=(0.5, 0.5, 0.5),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  ambient: bpy.props.FloatVectorProperty(
    name="Ambient Scene Color",
    description="The ambient color of the scene",
    subtype='COLOR',
    default=(0.5, 0.5, 0.5),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  decal_atlas: bpy.props.StringProperty(
    name="Decal Atlas",
    description="Decal atlas texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  world_s00_name: bpy.props.StringProperty(
    name="S00",
    description="Scene custom slot name 00",
    default="S00",
    update=update_trigger_export
  )
  world_s00_value: bpy.props.FloatProperty(
    name="S00",
    description="Scene custom slot value 00",
    update=update_trigger_export
  )
  world_s01_name: bpy.props.StringProperty(
    name="S01",
    description="Scene custom slot name 01",
    default="S01",
    update=update_trigger_export
  )
  world_s01_value: bpy.props.FloatProperty(
    name="S01",
    description="Scene custom slot value 01",
    update=update_trigger_export
  )
  world_s02_name: bpy.props.StringProperty(
    name="S02",
    description="Scene custom slot name 02",
    default="S02",
    update=update_trigger_export
  )
  world_s02_value: bpy.props.FloatProperty(
    name="S02",
    description="Scene custom slot value 02",
    update=update_trigger_export
  )
  world_s03_name: bpy.props.StringProperty(
    name="S03",
    description="Scene custom slot name 03",
    default="S03",
    update=update_trigger_export
  )
  world_s03_value: bpy.props.FloatProperty(
    name="S03",
    description="Scene custom slot value 03",
    update=update_trigger_export
  )
  world_s04_name: bpy.props.StringProperty(
    name="S04",
    description="Scene custom slot name 04",
    default="S04",
    update=update_trigger_export
  )
  world_s04_value: bpy.props.FloatProperty(
    name="S04",
    description="Scene custom slot value 04",
    update=update_trigger_export
  )
  world_s05_name: bpy.props.StringProperty(
    name="S05",
    description="Scene custom slot name 05",
    default="S05",
    update=update_trigger_export
  )
  world_s05_value: bpy.props.FloatProperty(
    name="S05",
    description="Scene custom slot value 05",
    update=update_trigger_export
  )
  world_s06_name: bpy.props.StringProperty(
    name="S06",
    description="Scene custom slot name 06",
    default="S06",
    update=update_trigger_export
  )
  world_s06_value: bpy.props.FloatProperty(
    name="S06",
    description="Scene custom slot value 06",
    update=update_trigger_export
  )
  world_s07_name: bpy.props.StringProperty(
    name="S07",
    description="Scene custom slot name 07",
    default="S07",
    update=update_trigger_export
  )
  world_s07_value: bpy.props.FloatProperty(
    name="S07",
    description="Scene custom slot value 07",
    update=update_trigger_export
  )
  world_s08_name: bpy.props.StringProperty(
    name="S08",
    description="Scene custom slot name 08",
    default="S08",
    update=update_trigger_export
  )
  world_s08_value: bpy.props.FloatProperty(
    name="S08",
    description="Scene custom slot value 08",
    update=update_trigger_export
  )
  world_s09_name: bpy.props.StringProperty(
    name="S09",
    description="Scene custom slot name 09",
    default="S09",
    update=update_trigger_export
  )
  world_s09_value: bpy.props.FloatProperty(
    name="S09",
    description="Scene custom slot value 09",
    update=update_trigger_export
  )
  world_s10_name: bpy.props.StringProperty(
    name="S10",
    description="Scene custom slot name 10",
    default="S10",
    update=update_trigger_export
  )
  world_s10_value: bpy.props.FloatProperty(
    name="S10",
    description="Scene custom slot value 10",
    update=update_trigger_export
  )
  world_s11_name: bpy.props.StringProperty(
    name="S11",
    description="Scene custom slot name 11",
    default="S11",
    update=update_trigger_export
  )
  world_s11_value: bpy.props.FloatProperty(
    name="S11",
    description="Scene custom slot value 11",
    update=update_trigger_export
  )
  world_s12_name: bpy.props.StringProperty(
    name="S12",
    description="Scene custom slot name 12",
    default="S12",
    update=update_trigger_export
  )
  world_s12_value: bpy.props.FloatProperty(
    name="S12",
    description="Scene custom slot value 12",
    update=update_trigger_export
  )
  world_s13_name: bpy.props.StringProperty(
    name="S13",
    description="Scene custom slot name 13",
    default="S13",
    update=update_trigger_export
  )
  world_s13_value: bpy.props.FloatProperty(
    name="S13",
    description="Scene custom slot value 13",
    update=update_trigger_export
  )
  world_s14_name: bpy.props.StringProperty(
    name="S14",
    description="Scene custom slot name 14",
    default="S14",
    update=update_trigger_export
  )
  world_s14_value: bpy.props.FloatProperty(
    name="S14",
    description="Scene custom slot value 14",
    update=update_trigger_export
  )
  world_s15_name: bpy.props.StringProperty(
    name="S15",
    description="Scene custom slot name 15",
    default="S15",
    update=update_trigger_export
  )
  world_s15_value: bpy.props.FloatProperty(
    name="S15",
    description="Scene custom slot value 15",
    update=update_trigger_export
  )


class WARME_PG_LightProperties(bpy.types.PropertyGroup):
  diffuse: bpy.props.FloatVectorProperty(
    name="Diffuse color",
    description="Diffuse color of the light",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  specular: bpy.props.FloatVectorProperty(
    name="Specular color",
    description="Specular color of the light",
    subtype='COLOR',
    default=(0.0, 0.0, 0.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  intensity: bpy.props.FloatProperty(
    name="Intensity",
    description="Intensity of the light",
    default=1,
    min=0.0, max=10.0,
    update=update_trigger_export
  )
  constant: bpy.props.FloatProperty(
    name="Constant Attenuation",
    description="Factor of constant attenuation",
    default=1,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  linear: bpy.props.FloatProperty(
    name="Linear Attenuation",
    description="Factor of linear attenuation (distance dependant)",
    default=0.0,
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  exp: bpy.props.FloatProperty(
    name="Exponential Attenuation",
    description="Factor of exponential attenuation (distance squared dependant)",
    default=0.0,
    min=0.0, max=2.0,
    update=update_trigger_export
  )
  group: bpy.props.IntProperty(
    name="Group Id",
    description="The material light group to affect",
    default=0,
    update=update_trigger_export
  )
  spot_cutoff_angle: bpy.props.FloatProperty(
    name="Spot Cutoff Angle",
    description="Cutoff angle of spot light",
    default=12.5,
    update=update_trigger_export
  )


class WARME_PG_SunProperties(bpy.types.PropertyGroup):
  diffuse: bpy.props.FloatVectorProperty(
    name="Diffuse Color",
    description="Set the diffuse color",
    subtype='COLOR',
    default=(0.5, 0.5, 0.5),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  specular: bpy.props.FloatVectorProperty(
    name="Specular Color",
    description="Set the specular color",
    subtype='COLOR',
    default=(1.0, 1.0, 1.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  intensity: bpy.props.FloatProperty(
    name="Intensity",
    description="Set the intensity of the sun light",
    default=1.0,
    update=update_trigger_export
  )
  group: bpy.props.IntProperty(
    name="Group Identifier",
    description="Set the group identifier",
    default=0,
    update=update_trigger_export
  )


class WARME_PG_DecalProperties(bpy.types.PropertyGroup):
  size: bpy.props.FloatVectorProperty(
    name="Size",
    description="Set the size of the projector",
    subtype='NONE',
    size=3,
    default=(1.0, 1.0, 1.0),
    update=update_trigger_export
  )
  group: bpy.props.IntProperty(
    name="Group Id",
    description="Set the group identifier",
    default=0,
    update=update_trigger_export
  )
  source_position: bpy.props.IntVectorProperty(
    name="Texture Position",
    description="Set position of the sprite from the atlas texture",
    subtype='NONE',
    size=2,
    default=(0, 0),
    update=update_trigger_export
  )
  source_size: bpy.props.IntVectorProperty(
    name="Source Size",
    description="Set size of the sprite from the atlas texture",
    subtype='NONE',
    size=2,
    default=(0, 0),
    update=update_trigger_export
  )
  opacity: bpy.props.FloatProperty(
    name="Opacity",
    description="Set the opacity",
    default=1.0,
    update=update_trigger_export
  )


class WARME_PG_ShadowProperties(bpy.types.PropertyGroup):
  size: bpy.props.FloatProperty(
    name="Size",
    description="Set the size of the projector",
    default=(1.0),
    update=update_shadow_size
  )
  depth: bpy.props.FloatProperty(
    name="Depth",
    description="Set the depth of the projector",
    default=(1.0),
    update=update_shadow_depth
  )
  texture_size: bpy.props.IntProperty(
    name="Size",
    description="Set the depth texture size",
    default=(2048),
    update=update_shadow_size
  )


class WARME_PG_SkyboxProperties(bpy.types.PropertyGroup):
  name: bpy.props.StringProperty(
    name="Skybox Name",
    description="Set the skybox name",
    default="",
    update=update_trigger_export
  )
  right: bpy.props.StringProperty(
    name="Skybox Right",
    description="Set the skybox right texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  left: bpy.props.StringProperty(
    name="Skybox Left",
    description="Set the skybox left texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  top: bpy.props.StringProperty(
    name="Skybox Top",
    description="Set the skybox top texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  bottom: bpy.props.StringProperty(
    name="Skybox Bottom",
    description="Set the skybox bottom texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  front: bpy.props.StringProperty(
    name="Skybox Front",
    description="Set the skybox front texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  back: bpy.props.StringProperty(
    name="Skybox Back",
    description="Set the skybox back texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )


class WARME_PG_ParticlesProperties(bpy.types.PropertyGroup):
  texture: bpy.props.StringProperty(
    name="Texture",
    description="Set the particle texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  position_style: bpy.props.EnumProperty(
    name="Position Style",
    description="Set the spawn position style distribution",
    items=[
      ('CUBE', "CUBE", "Cube"),
      ('SPHERE', "SPHERE", "Sphere"),
    ],
    default='CUBE',
    update=update_trigger_export
  )
  position_base: bpy.props.FloatVectorProperty(
    name="Position Base",
    description="Set the position base",
    subtype='NONE',
    default=(0.0, 0.0, 0.0),
    update=update_trigger_export
  )
  position_spread: bpy.props.FloatVectorProperty(
    name="Position Spread",
    description="Set the position variation from base",
    subtype='NONE',
    default=(0.0, 0.0, 0.0),
    update=update_trigger_export
  )
  position_sphere_radius_base: bpy.props.FloatProperty(
    name="Position Sphere Radius Base",
    description="Set the position radius base",
    default=(0.0),
    update=update_trigger_export
  )
  position_radius_spread: bpy.props.FloatProperty(
    name="Position Sphere Radius Spread",
    description="Set the position variation from base",
    default=(0.0),
    update=update_trigger_export
  )
  velocity_style: bpy.props.EnumProperty(
    name="Velocity Style",
    description="Set the velocity style",
    items=[
      ('CLASSIC', "CLASSIC", "Classic"),
      ('EXPLODE', "EXPLODE", "Explode"),
    ],
    default='CLASSIC',
    update=update_trigger_export
  )
  velocity_base: bpy.props.FloatVectorProperty(
    name="Velocity Base",
    description="Set the velocity base",
    subtype='NONE',
    default=(0.0, 0.0, 0.0),
    update=update_trigger_export
  )
  velocity_spread: bpy.props.FloatVectorProperty(
    name="Velocity Spread",
    description="Set the velocity variation from base",
    subtype='NONE',
    default=(0.0, 0.0, 0.0),
    update=update_trigger_export
  )
  velocity_explode_speed_base: bpy.props.FloatProperty(
    name="Velocity Explode Speed Base",
    description="Set the velocity explode speed base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  velocity_explode_speed_spread: bpy.props.FloatProperty(
    name="Velocity Explode Speed Spread",
    description="Set the velocity explode speed variation from base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  color_base: bpy.props.FloatVectorProperty(
    name="Color Base",
    description="Set the color base",
    subtype='COLOR',
    default=(0.0, 1.0, 0.5),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  color_spread: bpy.props.FloatVectorProperty(
    name="Color Spread",
    description="Set the color variation from base",
    subtype='COLOR',
    default=(0.0, 0.0, 0.0),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  size_base: bpy.props.FloatProperty(
    name="Size Base",
    description="Set the size base",
    subtype='NONE',
    default=(1.0),
    update=update_trigger_export
  )
  size_spread: bpy.props.FloatProperty(
    name="Size Spread",
    description="Set the size variation from base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  opacity_base: bpy.props.FloatProperty(
    name="Opacity Base",
    description="Set the opacity base",
    subtype='NONE',
    default=(1.0),
    update=update_trigger_export
  )
  opacity_spread: bpy.props.FloatProperty(
    name="Opacity Spread",
    description="Set the opacity variation from base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  acceleration_base: bpy.props.FloatVectorProperty(
    name="Acceleration Base",
    description="Set the acceleration base",
    subtype='NONE',
    default=(0.0, 0.0, 0.0),
    update=update_trigger_export
  )
  acceleration_spread: bpy.props.FloatVectorProperty(
    name="Acceleration Spread",
    description="Set the acceleration variation from base",
    subtype='NONE',
    default=(0.0, 0.0, 0.0),
    update=update_trigger_export
  )
  angle_base: bpy.props.FloatProperty(
    name="Angle Base",
    description="Set the angle base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  angle_spread: bpy.props.FloatProperty(
    name="Angle Spread",
    description="Set the angle variation from base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  angle_velocity_base: bpy.props.FloatProperty(
    name="Angle Velocity Base",
    description="Set the angle velocity base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  angle_velocity_spread: bpy.props.FloatProperty(
    name="Angle Velocity Spread",
    description="Set the angle velocity variation from base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  angle_acceleration_base: bpy.props.FloatProperty(
    name="Angle Acceleration Base",
    description="Set the angle acceleration base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  angle_acceleration_spread: bpy.props.FloatProperty(
    name="Angle Acceleration Spread",
    description="Set the angle acceleration variation from base",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  particle_death_age: bpy.props.FloatProperty(
    name="Particle Death Age",
    description="Set the particle death age",
    subtype='NONE',
    default=(1.0),
    update=update_trigger_export
  )
  particles_per_second: bpy.props.FloatProperty(
    name="Particles Per Second",
    description="Set the number of particles generated per second",
    subtype='NONE',
    default=(30.0),
    update=update_trigger_export
  )
  particles_quantity: bpy.props.FloatProperty(
    name="Particles Quantity",
    description="Set the maximum number of particles",
    subtype='NONE',
    default=(100.0),
    update=update_trigger_export
  )
  emitter_death_age: bpy.props.FloatProperty(
    name="Emitter Death Age",
    description="Set emitter death age",
    subtype='NONE',
    default=(60.0),
    update=update_trigger_export
  )
  tweens_color: bpy.props.CollectionProperty(type=TweenColor)
  tweens_size: bpy.props.CollectionProperty(type=TweenNumber)
  tweens_opacity: bpy.props.CollectionProperty(type=TweenNumber)
  tweens_acceleration: bpy.props.CollectionProperty(type=TweenVector3)
  tweens_color_index: bpy.props.IntProperty()
  tweens_size_index: bpy.props.IntProperty()
  tweens_opacity_index: bpy.props.IntProperty()
  tweens_acceleration_index: bpy.props.IntProperty()


class WARME_PG_EntityProperties(bpy.types.PropertyGroup):
  type: bpy.props.StringProperty(
    name="Type",
    description="Set the type of entity",
    default="",
    update=update_trigger_export
  )
  s00_name: bpy.props.StringProperty(
    name="S00",
    description="Custom slot name 00",
    default="S00",
    update=update_trigger_export
  )
  s00_value: bpy.props.StringProperty(
    name="S00",
    description="Custom slot value 00",
    update=update_trigger_export
  )
  s01_name: bpy.props.StringProperty(
    name="S01",
    description="Custom slot name 01",
    default="S01",
    update=update_trigger_export
  )
  s01_value: bpy.props.StringProperty(
    name="S01",
    description="Custom slot value 01",
    update=update_trigger_export
  )
  s02_name: bpy.props.StringProperty(
    name="S02",
    description="Custom slot name 02",
    default="S02",
    update=update_trigger_export
  )
  s02_value: bpy.props.StringProperty(
    name="S02",
    description="Custom slot value 02",
    update=update_trigger_export
  )
  s03_name: bpy.props.StringProperty(
    name="S03",
    description="Custom slot name 03",
    default="S03",
    update=update_trigger_export
  )
  s03_value: bpy.props.StringProperty(
    name="S03",
    description="Custom slot value 03",
    update=update_trigger_export
  )
  s04_name: bpy.props.StringProperty(
    name="S04",
    description="Custom slot name 04",
    default="S04",
    update=update_trigger_export
  )
  s04_value: bpy.props.StringProperty(
    name="S04",
    description="Custom slot value 04",
    update=update_trigger_export
  )
  s05_name: bpy.props.StringProperty(
    name="S05",
    description="Custom slot name 05",
    default="S05",
    update=update_trigger_export
  )
  s05_value: bpy.props.StringProperty(
    name="S05",
    description="Custom slot value 05",
    update=update_trigger_export
  )
  s06_name: bpy.props.StringProperty(
    name="S06",
    description="Custom slot name 06",
    default="S06",
    update=update_trigger_export
  )
  s06_value: bpy.props.StringProperty(
    name="S06",
    description="Custom slot value 06",
    update=update_trigger_export
  )
  s07_name: bpy.props.StringProperty(
    name="S07",
    description="Custom slot name 07",
    default="S07",
    update=update_trigger_export
  )
  s07_value: bpy.props.StringProperty(
    name="S07",
    description="Custom slot value 07",
    update=update_trigger_export
  )
  s08_name: bpy.props.StringProperty(
    name="S08",
    description="Custom slot name 08",
    default="S08",
    update=update_trigger_export
  )
  s08_value: bpy.props.StringProperty(
    name="S08",
    description="Custom slot value 08",
    update=update_trigger_export
  )
  s09_name: bpy.props.StringProperty(
    name="S09",
    description="Custom slot name 09",
    default="S09",
    update=update_trigger_export
  )
  s09_value: bpy.props.StringProperty(
    name="S09",
    description="Custom slot value 09",
    update=update_trigger_export
  )
  s10_name: bpy.props.StringProperty(
    name="S10",
    description="Custom slot name 10",
    default="S10",
    update=update_trigger_export
  )
  s10_value: bpy.props.StringProperty(
    name="S10",
    description="Custom slot value 10",
    update=update_trigger_export
  )
  s11_name: bpy.props.StringProperty(
    name="S11",
    description="Custom slot name 11",
    default="S11",
    update=update_trigger_export
  )
  s11_value: bpy.props.StringProperty(
    name="S11",
    description="Custom slot value 11",
    update=update_trigger_export
  )
  s12_name: bpy.props.StringProperty(
    name="S12",
    description="Custom slot name 12",
    default="S12",
    update=update_trigger_export
  )
  s12_value: bpy.props.StringProperty(
    name="S12",
    description="Custom slot value 12",
    update=update_trigger_export
  )
  s13_name: bpy.props.StringProperty(
    name="S13",
    description="Custom slot name 13",
    default="S13",
    update=update_trigger_export
  )
  s13_value: bpy.props.StringProperty(
    name="S13",
    description="Custom slot value 13",
    update=update_trigger_export
  )
  s14_name: bpy.props.StringProperty(
    name="S14",
    description="Custom slot name 14",
    default="S14",
    update=update_trigger_export
  )
  s14_value: bpy.props.StringProperty(
    name="S14",
    description="Custom slot value 14",
    update=update_trigger_export
  )
  s15_name: bpy.props.StringProperty(
    name="S15",
    description="Custom slot name 15",
    default="S15",
    update=update_trigger_export
  )
  s15_value: bpy.props.StringProperty(
    name="S15",
    description="Custom slot value 15",
    update=update_trigger_export
  )


class WARME_PG_WaterProperties(bpy.types.PropertyGroup):
  show_wave: bpy.props.BoolProperty(
    name="Waves",
    default=False
  )
  show_normal_map: bpy.props.BoolProperty(
    name="Normal Map",
    default=False
  )
  show_surface_color: bpy.props.BoolProperty(
    name="Surface Color",
    default=False
  )
  show_optics: bpy.props.BoolProperty(
    name="Optics Settings",
    default=False
  )
  show_sun: bpy.props.BoolProperty(
    name="Sun Settings",
    default=False
  )
  show_custom_params: bpy.props.BoolProperty(
    name="Custom Params",
    default=False
  )
  # ----------------------------------------------------------------------------------
  wave_amplitude: bpy.props.FloatProperty(
    name="Wave Amplitude",
    description="Set the wave amplitude factor",
    subtype='NONE',
    default=(0.5),
    update=update_trigger_export
  )
  wave_scale: bpy.props.FloatProperty(
    name="Wave Scale",
    description="Set the perlin noise scale",
    subtype='NONE',
    default=(0.18),
    update=update_trigger_export
  )
  wave_speed: bpy.props.FloatProperty(
    name="Wave Speed",
    description="Set the perlin scroll speed",
    subtype='NONE',
    default=(0.35),
    update=update_trigger_export
  )
  wave_choppiness: bpy.props.FloatProperty(
    name="Wave Choppiness",
    description="Set how waves are sharp",
    subtype='NONE',
    default=(1.0),
    update=update_trigger_export
  )
  wave_step_x: bpy.props.FloatProperty(
    name="Wave Step X",
    description="Set the horizontal surface step (0.5 = high level of details)",
    subtype='NONE',
    default=(0.5),
    update=update_trigger_export
  )
  wave_step_z: bpy.props.FloatProperty(
    name="Wave Step Z",
    description="Set the depth surface step (0.5 = high level of details)",
    subtype='NONE',
    default=(0.5),
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  normal_map: bpy.props.StringProperty(
    name="Normal Map",
    description="Normal Map texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  normal_map_scroll_x: bpy.props.FloatProperty(
    name="Normal Map Scroll X",
    description="Set the normal map horizontal scroll",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  normal_map_scroll_y: bpy.props.FloatProperty(
    name="Normal Map Scroll Y",
    description="Set the normal map vertical scroll",
    subtype='NONE',
    default=(0.0),
    update=update_trigger_export
  )
  normal_map_intensity: bpy.props.FloatProperty(
    name="Normal Map Intensity",
    description="Set the normal map intensity",
    subtype='NONE',
    default=(0.1),
    update=update_trigger_export
  )
  normal_map_scale: bpy.props.FloatProperty(
    name="Normal Map Scale",
    description="Set the normal map scale",
    subtype='NONE',
    default=(0.2),
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  surface_color_enabled: bpy.props.BoolProperty(
    name="Surface Color Enabled",
    description="Enable or not the water surface color tint",
    default=False,
    update=update_trigger_export
  )
  surface_color: bpy.props.FloatVectorProperty(
    name="Surface Color",
    description="Set the surface color tint",
    subtype='COLOR',
    default=(0.04, 0.18, 0.28),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  surface_color_factor: bpy.props.FloatProperty(
    name="Surface Color Factor",
    description="Set the surface color factor",
    subtype='NONE',
    default=(0.9),
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  optics_env_map_right: bpy.props.StringProperty(
    name="Cubemap Right",
    description="Set the cubemap right texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  optics_env_map_left: bpy.props.StringProperty(
    name="Cubemap Left",
    description="Set the cubemap left texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  optics_env_map_top: bpy.props.StringProperty(
    name="Cubemap Top",
    description="Set the cubemap top texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  optics_env_map_bottom: bpy.props.StringProperty(
    name="Cubemap Bottom",
    description="Set the cubemap bottom texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  optics_env_map_front: bpy.props.StringProperty(
    name="Cubemap Front",
    description="Set the cubemap front texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  optics_env_map_back: bpy.props.StringProperty(
    name="Cubemap Back",
    description="Set the cubemap back texture",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  optics_env_intensity: bpy.props.FloatProperty(
    name="Optics Env Map Intensity",
    description="Set the reflectivity factor",
    subtype='NONE',
    default=(1.0),
    update=update_trigger_export
  )
  optics_fresnel_power: bpy.props.FloatProperty(
    name="Optics Fresnel Power",
    description="Set the reflectivity distortion power",
    subtype='NONE',
    default=(4.0),
    update=update_trigger_export
  )
  optics_fresnel_biais: bpy.props.FloatProperty(
    name="Optics Fresnel Biais",
    description="Set the reflectivity factor",
    subtype='NONE',
    default=(0.4),
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  sun_enabled: bpy.props.BoolProperty(
    name="Sun Enabled",
    description="Enable or not the sun",
    default=False,
    update=update_trigger_export
  )
  sun_direction_x: bpy.props.FloatProperty(
    name="Sun Direction X",
    description="Set the sun direction",
    subtype='NONE',
    default=(-0.4),
    update=update_trigger_export
  )
  sun_direction_y: bpy.props.FloatProperty(
    name="Sun Direction Y",
    description="Set the sun direction",
    subtype='NONE',
    default=(-1.0),
    update=update_trigger_export
  )
  sun_direction_z: bpy.props.FloatProperty(
    name="Sun Direction Z",
    description="Set the sun direction",
    subtype='NONE',
    default=(-0.3),
    update=update_trigger_export
  )
  sun_color: bpy.props.FloatVectorProperty(
    name="Sun Color",
    description="Set the sun color",
    subtype='COLOR',
    default=(1.0, 0.9, 0.8),
    min=0.0, max=1.0,
    update=update_trigger_export
  )
  sun_color_factor: bpy.props.FloatProperty(
    name="Sun Intensity",
    description="Set the sun intensity",
    subtype='NONE',
    default=(0.8),
    update=update_trigger_export
  )
  # ----------------------------------------------------------------------------------
  s00_name: bpy.props.StringProperty(
    name="S00",
    description="Custom slot name 00",
    default="S00",
    update=update_trigger_export
  )
  s00_value: bpy.props.StringProperty(
    name="S00",
    description="Custom slot value 00",
    update=update_trigger_export
  )
  s01_name: bpy.props.StringProperty(
    name="S01",
    description="Custom slot name 01",
    default="S01",
    update=update_trigger_export
  )
  s01_value: bpy.props.StringProperty(
    name="S01",
    description="Custom slot value 01",
    update=update_trigger_export
  )
  s02_name: bpy.props.StringProperty(
    name="S02",
    description="Custom slot name 02",
    default="S02",
    update=update_trigger_export
  )
  s02_value: bpy.props.StringProperty(
    name="S02",
    description="Custom slot value 02",
    update=update_trigger_export
  )
  s03_name: bpy.props.StringProperty(
    name="S03",
    description="Custom slot name 03",
    default="S03",
    update=update_trigger_export
  )
  s03_value: bpy.props.StringProperty(
    name="S03",
    description="Custom slot value 03",
    update=update_trigger_export
  )
  s04_name: bpy.props.StringProperty(
    name="S04",
    description="Custom slot name 04",
    default="S04",
    update=update_trigger_export
  )
  s04_value: bpy.props.StringProperty(
    name="S04",
    description="Custom slot value 04",
    update=update_trigger_export
  )
  s05_name: bpy.props.StringProperty(
    name="S05",
    description="Custom slot name 05",
    default="S05",
    update=update_trigger_export
  )
  s05_value: bpy.props.StringProperty(
    name="S05",
    description="Custom slot value 05",
    update=update_trigger_export
  )
  s06_name: bpy.props.StringProperty(
    name="S06",
    description="Custom slot name 06",
    default="S06",
    update=update_trigger_export
  )
  s06_value: bpy.props.StringProperty(
    name="S06",
    description="Custom slot value 06",
    update=update_trigger_export
  )
  s07_name: bpy.props.StringProperty(
    name="S07",
    description="Custom slot name 07",
    default="S07",
    update=update_trigger_export
  )
  s07_value: bpy.props.StringProperty(
    name="S07",
    description="Custom slot value 07",
    update=update_trigger_export
  )
  s0_texture: bpy.props.StringProperty(
    name="S0 Texture",
    description="Custom texture slot 0",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )
  s1_texture: bpy.props.StringProperty(
    name="S1 Texture",
    description="Custom texture slot 1",
    default="",
    subtype='FILE_PATH',
    update=update_trigger_export
  )