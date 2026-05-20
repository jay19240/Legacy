import { gfx3Manager } from './gfx3_manager';
import { gfx3MipmapManager } from './gfx3_mipmap_manager';
import { Gfx3Texture } from './gfx3_texture';

/**
 * Singleton 3D textures manager.
 */
export class Gfx3TextureManager {
  textures: Map<string, Gfx3Texture>;
  urls: Map<string, string>;
  blobs: Map<string, Blob>;

  constructor() {
    this.textures = new Map<string, Gfx3Texture>();
    this.urls = new Map<string, string>();
    this.blobs = new Map<string, Blob>();
  }

  /**
   * Loads asynchronously an image from a given path and returns it as a texture, caching it for future use.
   * 
   * @param {string} path - The file path.
   * @param {GPUSamplerDescriptor} [samplerDescriptor] - The sampler texture configuration, see https://www.w3.org/TR/webgpu/#GPUSamplerDescriptor.
   * @param {boolean} [is8bit] - Determine if texture is 8bits encoded.
   * @param {string} storePath - The optionnal store file path.
   */
  async loadTexture(path: string, samplerDescriptor: GPUSamplerDescriptor = {}, is8bit: boolean = false, storePath: string = ''): Promise<Gfx3Texture> {
    storePath = storePath ? storePath : path;

    if (this.textures.has(storePath)) {
      return this.textures.get(storePath)!;
    }

    const res = await fetch(path);
    const img = await res.blob();
    const url = URL.createObjectURL(img);
    const bitmap = await createImageBitmap(img, { colorSpaceConversion: 'none' });
    const texture = gfx3Manager.createTextureFromBitmap(bitmap, is8bit, samplerDescriptor);

    this.textures.set(storePath, texture);
    this.urls.set(storePath, url);
    this.blobs.set(storePath, img);
    return texture;
  }

  /**
   * Load asynchronously an image from a given path and returns a texture with its mipmaps, caching it for future use.
   * 
   * @param {string} path - The file path.
   * @param {GPUSamplerDescriptor} [samplerDescriptor] - The sampler texture configuration, see https://www.w3.org/TR/webgpu/#GPUSamplerDescriptor.
   * @param {boolean} [is8bit] - Determine if texture is 8bits encoded.
   * @param {string} storePath - The optionnal store file path.
   */
  async loadTextureMips(path: string, samplerDescriptor: GPUSamplerDescriptor = {}, is8bit: boolean = false, storePath: string = ''): Promise<Gfx3Texture> {
    storePath = storePath ? storePath : path;

    if (this.textures.has(storePath)) {
      return this.textures.get(storePath)!;
    }

    const res = await fetch(path);
    const img = await res.blob();
    const url = URL.createObjectURL(img);
    const bitmap = await createImageBitmap(img, { colorSpaceConversion: 'none' });
    const texture = gfx3MipmapManager.createTextureFromBitmap(bitmap, is8bit, samplerDescriptor);
    this.textures.set(storePath, texture);
    this.urls.set(storePath, url);
    this.blobs.set(storePath, img);
    return texture;
  }

  /**
   * Load asynchronously a list of cubemap images from a given path and returns it as an texture, caching it for future use.
   * Note: Six images are required, each names postfixed by: right, left, top, bottom, front and back.
   * 
   * @param {string} path - The file path excluding directions postfix.
   * @param {string} storePath - The optionnal store file path.
   */
  async loadCubemapTexture(paths: { right: string, left: string, top: string, bottom: string, front: string, back: string }, storePath: string = ''): Promise<Gfx3Texture> {
    if (this.textures.has(storePath)) {
      return this.textures.get(storePath)!;
    }

    type direction = 'right' | 'left' | 'top' | 'bottom' | 'front' | 'back';
    const dirs = ['right', 'left', 'top', 'bottom', 'front', 'back'];
    const bitmaps: Array<ImageBitmap> = [];

    for (const dir of dirs) {
      await this.loadTexture(paths[dir as direction]);
      const img = this.getTextureBlob(paths[dir as direction])
      const url = this.getTextureURL(paths[dir as direction]);

      const bitmap = await createImageBitmap(img, { colorSpaceConversion: 'none' });
      bitmaps.push(bitmap);
      this.urls.set(storePath, url);
    }

    const texture = gfx3Manager.createCubeMapFromBitmap(bitmaps);
    this.textures.set(storePath, texture);
    return texture;
  }

  /**
   * Deletes a texture if it exists, otherwise it throws an error.
   * 
   * @param {string} path - The file path.
   */
  deleteTexture(path: string): void {
    if (!this.textures.has(path)) {
      throw new Error('Gfx3TextureManager::deleteTexture(): The texture file doesn\'t exist, cannot delete !');
    }

    const texture = this.textures.get(path)!;
    texture.gpuTexture.destroy();

    const url = this.urls.get(path)!;
    URL.revokeObjectURL(url);

    this.textures.delete(path);
    this.urls.delete(path);
    this.blobs.delete(path);
  }

  /**
   * Returns a texture or throws an error if doesn't exist.
   * 
   * @param {string} path - The file path.
   */
  getTexture(path: string): Gfx3Texture {
    if (!this.textures.has(path)) {
      throw new Error('Gfx2TextureManager::getTexture(): The texture file doesn\'t exist, cannot get !');
    }

    return this.textures.get(path)!;
  }

  /**
   * Returns the URL of a texture.
   * 
   * @param {string} path - The file path.
   */
  getTextureURL(path: string, refresh: boolean = false): string {
    if (!this.urls.has(path)) {
      throw new Error('Gfx3TextureManager::getTextureURL(): The texture file doesn\'t exist, cannot get !');
    }

    if (refresh) {
      const url = this.urls.get(path)!;
      const blob = this.blobs.get(path)!;
      URL.revokeObjectURL(url);
      this.urls.set(path, URL.createObjectURL(blob));
    }

    return this.urls.get(path)!;
  }

  /**
   * Returns the Blob of a texture.
   * 
   * @param {string} path - The file path.
   */
  getTextureBlob(path: string): Blob {
    if (!this.blobs.has(path)) {
      throw new Error('Gfx3TextureManager::getTextureBlob(): The texture file doesn\'t exist, cannot get !');
    }

    return this.blobs.get(path)!;
  }

  /**
   * Checks if a texture exists.
   * 
   * @param {string} path - The path file.
   */
  hasTexture(path: string): boolean {
    return this.textures.has(path);
  }

  /**
   * Deletes all stored textures.
   */
  releaseTextures(): void {
    for (const path of this.textures.keys()) {
      const url = this.urls.get(path)!;
      URL.revokeObjectURL(url);
  
      const texture = this.textures.get(path)!;
      texture.gpuTexture.destroy();
      this.textures.delete(path);
      this.urls.delete(path);
      this.blobs.delete(path);
    }
  }
}

export const gfx3TextureManager = new Gfx3TextureManager();