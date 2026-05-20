/**
 * Singleton textures manager.
 */
export class Gfx2TextureManager {
  textures: Map<string, ImageBitmap>;
  urls: Map<string, string>;
  blobs: Map<string, Blob>;

  constructor() {
    this.textures = new Map<string, ImageBitmap>();
    this.urls = new Map<string, string>();
    this.blobs = new Map<string, Blob>();
  }

  /**
   * Loads asynchronously an image from a given path, caching it for future use and returns it as an `ImageBitmap`.
   * 
   * @param {string} path - The file path.
   * @param {string} storePath - The optionnal store file path.
   */
  async loadTexture(path: string, storePath: string = ''): Promise<ImageBitmap> {
    storePath = storePath ? storePath : path;

    if (this.textures.has(storePath)) {
      return this.textures.get(storePath)!;
    }

    const res = await fetch(path);
    const img = await res.blob();
    const url = URL.createObjectURL(img);
    const bitmap = await createImageBitmap(img);

    this.textures.set(storePath, bitmap);
    this.urls.set(storePath, url);
    this.blobs.set(storePath, img);
    return bitmap;
  }

  /**
   * Deletes a texture if it exists, otherwise it throws an error.
   * 
   * @param {string} path - The file path.
   */
  deleteTexture(path: string): void {
    if (!this.textures.has(path)) {
      throw new Error('Gfx2TextureManager::deleteTexture(): The texture file doesn\'t exist, cannot delete !');
    }

    const url = this.urls.get(path)!;
    URL.revokeObjectURL(url);

    this.textures.delete(path);
    this.urls.delete(path);
    this.blobs.delete(path);
  }

  /**
   * Returns an `ImageBitmap` object for a given texture path, or throws an error if the texture doesn't exist.
   * 
   * @param {string} path - The file path.
   */
  getTexture(path: string): ImageBitmap {
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
      throw new Error('Gfx2TextureManager::getTextureURL(): The texture file doesn\'t exist, cannot get !');
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
      throw new Error('Gfx2TextureManager::getTextureBlob(): The texture file doesn\'t exist, cannot get !');
    }

    return this.blobs.get(path)!;
  }

  /**
   * Checks if texture exists.
   * 
   * @param {string} path - The file path.
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

      this.textures.delete(path);
      this.urls.delete(path);
      this.blobs.delete(path);
    }
  }
}

export const gfx2TextureManager = new Gfx2TextureManager();