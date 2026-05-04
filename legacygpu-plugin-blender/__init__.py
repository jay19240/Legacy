bl_info = {
  "name": "Legacy Exporter",
  "author": "panzer-banana",
  "version": (1, 0, 0),
  "blender": (4, 2, 0),
  "location": "View3D > Properties > Legacy Export",
  "description": "Export to a custom Legacy format",
  "category": "Import-Export"
}

# Imports --------------------------------------------------------------------------
from . import operators
from . import operators_world
from . import panels
from . import functions
from . import props
from . import utils
import bpy
import os
from bpy.app.handlers import persistent
# ----------------------------------------------------------------------------------

_handle = None

@persistent
def on_save(dummy):
  if (bpy.context.scene.world_properties.enable_auto_export):
    bpy.ops.object.export_pack()


def register():
  global _handle

  props.register()
  operators.register()
  operators_world.register()
  panels.register()

  if on_save not in bpy.app.handlers.save_post:
    bpy.app.handlers.save_post.append(on_save)

  _handle = bpy.types.SpaceView3D.draw_handler_add(
    utils.draw_grf_node_values, (None, bpy.context), 'WINDOW', 'POST_PIXEL'
  )

def unregister():
  props.unregister()
  operators.unregister()
  operators_world.unregister()
  panels.unregister()

  if on_save in bpy.app.handlers.save_post:
    bpy.app.handlers.save_post.remove(on_save)


if __name__ == "__main__":
  register()