import { UT } from '../core/utils';
import { Gfx2Drawable } from './gfx2_drawable';

export enum Gfx2RenderingMode {
  ISOMETRIC = 'ISOMETRIC',
  ORTHOGRAPHIC = 'ORTHOGRAPHIC'
};

export interface Gfx2DebugLine {
  from: vec2;
  to: vec2;
  color: string;
  width: number;
}

/**
 * Singleton 2D graphics manager.
 */
export class Gfx2Manager {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  drawables: Array<Gfx2Drawable>;
  drawCommands: Array<(ctx: CanvasRenderingContext2D) => void>;
  drawDebugLines: Array<Gfx2DebugLine>;
  mode: Gfx2RenderingMode;
  cameraTransform: mat3;
  cameraScale: vec2;
  cameraRotation: number;
  cameraPosition: vec2;
  bgColor: vec4;
  offCanvas: OffscreenCanvas;
  offCtx: OffscreenCanvasRenderingContext2D;

  constructor() {
    this.canvas = <HTMLCanvasElement>document.getElementById('CANVAS_2D')!;
    this.ctx = this.canvas.getContext('2d')!;
    this.drawables = [];
    this.drawCommands = [];
    this.drawDebugLines = [];
    this.mode = Gfx2RenderingMode.ORTHOGRAPHIC;
    this.cameraTransform = UT.MAT3_IDENTITY();
    this.cameraScale = [1, 1];
    this.cameraRotation = 0;
    this.cameraPosition = [0, 0];
    this.bgColor = [0, 0, 0, 1];
    this.offCanvas = new OffscreenCanvas(this.canvas.clientWidth, this.canvas.clientHeight);
    this.offCtx = this.offCanvas.getContext('2d', { willReadFrequently: true }) as OffscreenCanvasRenderingContext2D;

    if (!this.ctx) {
      UT.FAIL('This browser does not support canvas');
      throw new Error('Gfx2Manager::Gfx2Manager: Your browser not support 2D');
    }
  }

  /**
   * The update function.
   * 
   * @param {number} ts - The timestep.
   */
  update(ts: number): void { }

  /**
   * Begin the render phase. Prepares the canvas for rendering.
   * Warning: You need to call this method before any draw calls.
   */
  beginRender(): void {
    if (this.canvas.width != this.canvas.clientWidth || this.canvas.height != this.canvas.clientHeight) {
      this.canvas.width = this.canvas.clientWidth;
      this.canvas.height = this.canvas.clientHeight;
      this.offCanvas.width = this.canvas.clientWidth;
      this.offCanvas.height = this.canvas.clientHeight;
    }

    this.ctx.imageSmoothingEnabled = false;

    this.ctx.save();
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.fillStyle = `rgba(${this.bgColor[0]}, ${this.bgColor[1]}, ${this.bgColor[2]}, ${this.bgColor[3]})`;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.transform(this.cameraTransform[0], this.cameraTransform[1], this.cameraTransform[3], this.cameraTransform[4], this.cameraTransform[6], this.cameraTransform[7]);
    this.ctx.translate(this.canvas.width * 0.5, this.canvas.height * 0.5);
    this.ctx.scale(this.cameraScale[0], this.cameraScale[1]);
    this.ctx.rotate(this.cameraRotation);
    this.ctx.translate(-this.cameraPosition[0], -this.cameraPosition[1]);
  }

  /**
   * The render method.
   */
  render(): void {
    const sortFn = this.mode == Gfx2RenderingMode.ISOMETRIC ? ISOMETRIC_SORT : ORTHOGRAPHIC_SORT;
    this.drawables.sort(sortFn);

    for (const drawable of this.drawables) {
      drawable.render();
    }

    for (const drawCmd of this.drawCommands) {
      drawCmd(this.ctx);
    }

    for (const line of this.drawDebugLines) {
      this.ctx.beginPath();
      this.ctx.strokeStyle = line.color;
      this.ctx.lineWidth = line.width;
      this.ctx.moveTo(line.from[0], line.from[1]);
      this.ctx.lineTo(line.to[0], line.to[1]);
      this.ctx.stroke();
    }

    this.drawDebugLines = [];
  }

  /**
   * End the render phase.
   */
  endRender(): void {
    this.ctx.restore();
    this.drawables = [];
    this.drawCommands = [];
  }

  /**
   * Add drawable to the draw list.
   * 
   * @param {Gfx2Drawable} drawable - The drawable.
   */
  draw(drawable: Gfx2Drawable): void {
    this.drawables.push(drawable);
  }

  /**
   * Draw a debug line.
   * 
   * @param {number} x1 - The line x-begin.
   * @param {number} y1 - The line y-begin.
   * @param {number} x2 - The line x-end.
   * @param {number} y2 - The line y-end.
   * @param {number} color - The line color.
   * @param {number} width - The line width.
   */
  drawDebugLine(x1: number, y1: number, x2: number, y2: number, color: string = 'red', width: number = 0.05) {
    this.drawDebugLines.push({
      from: [x1, y1],
      to: [x2, y2],
      color: color,
      width: width
    });
  }

  /**
   * Add draw function command call to the draw list.
   * 
   * @param {(ctx: CanvasRenderingContext2D) => void} drawCmd - The draw command.
   */
  drawCommand(drawCmd: (ctx: CanvasRenderingContext2D) => void): void {
    this.drawCommands.push(drawCmd);
  }

  /**
   * Set the renderer sorting mode.
   * 
   * @param {Gfx2RenderingMode} mode - The mode.
   */
  setMode(mode: Gfx2RenderingMode): void {
    this.mode = mode;
  }

  /**
   * Move the camera.
   * 
   * @param {number} x - The move in x-axis direction.
   * @param {number} y - The move in y-axis direction.
   */
  moveCamera(x: number, y: number): void {
    this.cameraPosition[0] += x;
    this.cameraPosition[1] += y;
  }

  /**
   * Sets the css filter property of the canvas.
   * 
   * @param {string} filter - The filter parameter is a string that represents the CSS filter property's value.
   * It can be used to apply various visual effects to an element, such as blur, brightness, contrast,
   * grayscale, etc.
   */
  setFilter(filter: string): void {
    this.canvas.style.filter = filter;
  }

  /**
   * Checks if the canvas element has an active filter.
   */
  hasFilter(): boolean {
    return this.canvas.style.filter != '' && this.canvas.style.filter != 'none';
  }

  /**
   * Returns the world-space position from the client-space position.
   * 
   * @param {number} clientX - The horizontal client coordinate.
   * @param {number} clientY - The vertical client coordinate.
   */
  getWorldPosFromDocument(clientX: number, clientY: number): vec2 {
    const rect = this.canvas.getBoundingClientRect();
    const x = ((clientX - rect.x) / this.cameraScale[0]) + this.cameraPosition[0] - this.canvas.width * 0.5;
    const y = ((clientY - rect.y) / this.cameraScale[1]) + this.cameraPosition[1] - this.canvas.height * 0.5;
    return [x, y];
  }

  /**
   * Returns the world-space position from the canvas center.
   * 
   * @param {number} x - The horizontal canvas coordinate.
   * @param {number} y - The vertical canvas coordinate.
   */
  getWorldPosFromCanvasCenter(x: number, y: number): vec2 {
    const wx = (x / this.cameraScale[0]) + this.cameraPosition[0];
    const wy = (y / this.cameraScale[1]) + this.cameraPosition[1];
    return [wx, wy];
  }

  /**
   * Returns the resolution width of the canvas.
   */
  getWidth(): number {
    return this.canvas.clientWidth;
  }

  /**
   * Returns the resolution height of the canvas.
   */
  getHeight(): number {
    return this.canvas.clientHeight;
  }

  /**
   * Returns the 2D rendering context of the canvas element.
   */
  getContext(): CanvasRenderingContext2D {
    return this.ctx;
  }

  /**
   * Set the camera transformation matrix (before position/rotation/scale).
   * 
   * @param {mat3} cameraTransform - The transformation matrix.
   */
  setCameraTransform(cameraTransform: mat3): void {
    this.cameraTransform = cameraTransform;
  }

  /**
   * Returns the camera transformation matrix.
   */
  getCameraTransform(): mat3 {
    return this.cameraTransform;
  }

  /**
   * Sets the camera position.
   * 
   * @param {number} x - The x-coordinate.
   * @param {number} y - The y-coordinate.
   */
  setCameraPosition(x: number, y: number): void {
    this.cameraPosition[0] = x;
    this.cameraPosition[1] = y;
  }

  /**
   * Returns the camera position.
   */
  getCameraPosition(): vec2 {
    return this.cameraPosition;
  }

  /**
   * Returns the X coordinate of the camera position.
   */
  getCameraPositionX(): number {
    return this.cameraPosition[0];
  }

  /**
   * Returns the Y coordinate of the camera position.
   */
  getCameraPositionY(): number {
    return this.cameraPosition[1];
  }

  /**
   * Sets the camera scale.
   * 
   * @param {number} x - The scale factor for the camera in the x-axis.
   * @param {number} y - The scale factor for the camera in the y-axis.
   */
  setCameraScale(x: number, y: number): void {
    this.cameraScale[0] = x;
    this.cameraScale[1] = y;
  }

  /**
   * Returns the camera scale.
   */
  getCameraScale(): vec2 {
    return this.cameraScale;
  }

  /**
   * Returns the camera scale factor on x-axis.
   */
  getCameraScaleX(): number {
    return this.cameraScale[0];
  }

  /**
   * Returns the camera scale factor on y-axis.
   */
  getCameraScaleY(): number {
    return this.cameraScale[1];
  }

  /**
   * Sets the rotation of the camera.
   * 
   * @param {number} cameraRotation - The camera rotation angle in radians.
   */
  setCameraRotation(cameraRotation: number): void {
    this.cameraRotation = cameraRotation;
  }

  /**
   * Returns the camera rotation angle in radians.
   */
  getCameraRotation(): number {
    return this.cameraRotation;
  }

  /**
   * Sets the background color using the provided RGBA values (0 - 255).
   * 
   * @param {number} r - The red component.
   * @param {number} g - The green component.
   * @param {number} b - The blue component.
   * @param {number} a - The alpha value.
   */
  setBgColor(r: number, g: number, b: number, a: number): void {
    this.bgColor[0] = r;
    this.bgColor[1] = g;
    this.bgColor[2] = b;
    this.bgColor[3] = a;
  }

  /**
   * Returns the background color.
   */
  getBgColor(): vec4 {
    return this.bgColor;
  }

  /**
   * Returns a default HTMLImageElement.
   */
  getDefaultTexture(): HTMLImageElement {
    const image = new Image();
    image.src = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';
    return image;
  }

  /**
   * Returns a new texture tinted by the color multiplication.
   */
  getTintedTexture(texture: HTMLImageElement | ImageBitmap, r: number, g: number, b: number): ImageBitmap {
    this.offCanvas.width = texture.width;
    this.offCanvas.height = texture.height;
    this.offCtx.drawImage(texture, 0, 0);

    const imageData = this.offCtx.getImageData(0, 0, texture.width, texture.height);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      data[i + 0] *= r;
      data[i + 1] *= g;
      data[i + 2] *= b;
    }

    this.offCtx.putImageData(imageData, 0, 0);
    return this.offCanvas.transferToImageBitmap();
  }
}

export const gfx2Manager = new Gfx2Manager();

// -------------------------------------------------------------------------------------------
// HELPFUL
// -------------------------------------------------------------------------------------------

function ISOMETRIC_SORT(a: Gfx2Drawable, b: Gfx2Drawable): number {
  if (a.getElevation() < b.getElevation()) {
    return -1;
  }

  if (a.getElevation() > b.getElevation()) {
    return 1;
  }

  return a.getPositionY() - b.getPositionY();
}

function ORTHOGRAPHIC_SORT(a: Gfx2Drawable, b: Gfx2Drawable): number {
  return a.getPositionZ() - b.getPositionZ();
}