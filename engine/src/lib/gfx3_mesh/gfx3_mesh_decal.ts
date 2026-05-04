import { gfx3MeshRenderer } from './gfx3_mesh_renderer';
import { gfx3DebugRenderer } from '../gfx3/gfx3_debug_renderer';
import { Gfx3Transformable } from '../gfx3/gfx3_transformable';
import { UT } from '../core/utils';

/**
 * A 3D mesh decal.
 */
export class Gfx3MeshDecal extends Gfx3Transformable {
  groupId: number;
  sx: number;
  sy: number;
  sw: number;
  sh: number;
  opacity: number;
  debugEnabled: boolean;

  constructor() {
    super();
    this.groupId = 0;
    this.sx = 0.0;
    this.sy = 0.0;
    this.sw = 1.0;
    this.sh = 1.0;
    this.opacity = 1.0;
    this.debugEnabled = true;
  }

  /**
   * Load asynchronously a decal data from a json file (dcl).
   * 
   * @param {string} path - The file path.
   */
  async loadFromFile(path: string): Promise<void> {
    const response = await fetch(path);
    const json = await response.json();

    if (!json.hasOwnProperty('Ident') || json['Ident'] != 'DCL') {
      throw new Error('Gfx3MeshDecal::loadFromFile(): File not valid !');
    }

    this.position[0] = json['PositionX'];
    this.position[1] = json['PositionY'];
    this.position[2] = json['PositionZ'];
    this.rotation[0] = json['RotationX'];
    this.rotation[1] = json['RotationY'];
    this.rotation[2] = json['RotationZ'];
    this.scale[0] = json['SizeX'];
    this.scale[1] = json['SizeY'];
    this.scale[2] = json['SizeZ'];
    this.groupId = json['GroupId'];
    this.sx = json['SourceX'];
    this.sy = json['SourceY'];
    this.sw = json['SourceWidth'];
    this.sh = json['SourceHeight'];
    this.opacity = json['Opacity'];
  }

  /**
   * The draw function.
   */
  draw(): void {
    const axis = this.getNormalizedAxies();
    gfx3MeshRenderer.drawDecal(
      this.groupId,
      this.sx,
      this.sy,
      this.sw,
      this.sh,
      this.position,
      axis[0],
      axis[1],
      axis[2],
      this.scale,
      this.opacity
    );

    if (this.debugEnabled) {
      const matrix = this.getTransformMatrix();
      const color = [1, 1, 0];
      const c = [
        [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5], // Near (0-3)
        [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5] // Far (4-7)
      ];

      for (let i = 0; i < 4; i++) {
        // Face Near
        gfx3DebugRenderer.drawLine(matrix, c[i][0], c[i][1], c[i][2], c[(i + 1) % 4][0], c[(i + 1) % 4][1], c[(i + 1) % 4][2], color[0], color[1], color[2]);
        // Face Far
        gfx3DebugRenderer.drawLine(matrix, c[i + 4][0], c[i + 4][1], c[i + 4][2], c[((i + 1) % 4) + 4][0], c[((i + 1) % 4) + 4][1], c[((i + 1) % 4) + 4][2], color[0], color[1], color[2]);
        // Join Near-Far
        gfx3DebugRenderer.drawLine(matrix, c[i][0], c[i][1], c[i][2], c[i + 4][0], c[i + 4][1], c[i + 4][2], color[0], color[1], color[2]);
      }

      const x = UT.VEC3_SCALE(axis[0], this.scale[0] / 2.0);
      gfx3DebugRenderer.drawLine(UT.MAT4_IDENTITY(), this.position[0], this.position[1], this.position[2], this.position[0] + x[0], this.position[1] + x[1], this.position[2] + x[2], 1, 0, 0);
      gfx3DebugRenderer.drawLine(UT.MAT4_IDENTITY(), this.position[0], this.position[1], this.position[2], this.position[0] - x[0], this.position[1] - x[1], this.position[2] - x[2], 1, 0, 0);

      const y = UT.VEC3_SCALE(axis[1], this.scale[1] / 2.0);
      gfx3DebugRenderer.drawLine(UT.MAT4_IDENTITY(), this.position[0], this.position[1], this.position[2], this.position[0] + y[0], this.position[1] + y[1], this.position[2] + y[2], 0, 1, 0);
      gfx3DebugRenderer.drawLine(UT.MAT4_IDENTITY(), this.position[0], this.position[1], this.position[2], this.position[0] - y[0], this.position[1] - y[1], this.position[2] - y[2], 0, 1, 0);

      const z = UT.VEC3_SCALE(axis[2], this.scale[2] / 2.0);
      gfx3DebugRenderer.drawLine(UT.MAT4_IDENTITY(), this.position[0], this.position[1], this.position[2], this.position[0] + z[0], this.position[1] + z[1], this.position[2] + z[2], 0, 0, 1);
      gfx3DebugRenderer.drawLine(UT.MAT4_IDENTITY(), this.position[0], this.position[1], this.position[2], this.position[0] - z[0], this.position[1] - z[1], this.position[2] - z[2], 0, 0, 1);
    }
  }

  /**
   * Set group.
   * 
   * @param {number} groupId - The group id.
   */
  setGroup(groupId: number): void {
    this.groupId = groupId;
  }

  /**
   * Set the source coordinate of sprite in the decal atlas.
   * 
   * @param {number} sx - The source x coordinate of the sprite top-left corner.
   * @param {number} sy - The source y coordinate of the sprite top-left corner.
   * @param {number} sw - The source width of the sprite.
   * @param {number} sh - The source height of the sprite.
   */
  setSource(sx: number, sy: number, sw: number, sh: number): void {
    this.sx = sx;
    this.sy = sy;
    this.sw = sw;
    this.sh = sh;
  }

  /**
   * Set the opacity of the decal.
   * 
   * @param {number} opacity - The opacity value.
   */
  setOpacity(opacity: number): void {
    this.opacity = opacity;
  }

  /**
   * Returns the group identifier.
   */
  getGroup(): number {
    return this.groupId;
  }

  /**
   * Returns the top-left coordinate of source sprite.
   */
  getSourceTopLeft(): vec2 {
    return [this.sx, this.sy];
  }

  /**
   * Returns the size of source sprite.
   */
  getSourceSize(): vec2 {
    return [this.sw, this.sh];
  }

  /**
   * Returns the opacity value.
   */
  getOpacity(): number {
    return this.opacity;
  }

  /**
   * Enable the debug mesh display.
   * 
   * @param {boolean} enabled - The enabled flag.
   */
  enableDebug(enabled: boolean): void {
    this.debugEnabled = enabled;
  }

  /**
   * Set the projector size.
   * 
   * @param {number} width - The width.
   * @param {number} height - The height.
   * @param {number} depth - The depth.
   */
  setSize(width: number, height: number, depth: number) {
    this.scale[0] = width;
    this.scale[1] = height;
    this.scale[2] = depth;
  }
}