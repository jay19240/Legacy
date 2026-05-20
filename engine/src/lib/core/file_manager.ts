/**
 * Singleton files manager.
 */
export class FileManager {
  files: Map<string, any>;
  urls: Map<string, string>;
  blobs: Map<string, Blob>;

  constructor() {
    this.files = new Map<string, any>();
    this.urls = new Map<string, string>();
    this.blobs = new Map<string, Blob>();
  }

  /**
   * Loads asynchronously a file from a given path, caching it for future use and returns it as an `Blob`.
   * 
   * @param {string} path - The file path.
   * @param {string} storePath - The optionnal store file path.
   */
  async loadFile(path: string, storePath: string = '', type: 'blob' | 'json' | 'text' = 'blob'): Promise<any> {
    storePath = storePath ? storePath : path;

    if (this.files.has(storePath)) {
      return this.files.get(storePath)!;
    }

    let data = null;
    const res = await fetch(path);

    if (type == 'blob') {
      data = await res.blob();
      const url = URL.createObjectURL(data);
      this.urls.set(storePath, url);
      this.blobs.set(storePath, data);
    }
    else if (type == 'json') {
      data = await res.json();
    }
    else if (type == 'text') {
      data = await res.text();
    }

    this.files.set(storePath, data);
    return data;
  }

  /**
   * Deletes a file if it exists, otherwise it throws an error.
   * 
   * @param {string} path - The file path.
   */
  deleteFile(path: string): void {
    if (!this.files.has(path)) {
      throw new Error('FileManager::deleteFile(): The texture file doesn\'t exist, cannot delete !');
    }

    const url = this.urls.get(path)!;
    URL.revokeObjectURL(url);

    this.files.delete(path);
    this.urls.delete(path);
    this.blobs.delete(path);
  }

  /**
   * Returns an `Blob` object for a given texture path, or throws an error if the file doesn't exist.
   * 
   * @param {string} path - The file path.
   */
  getFile(path: string): any {
    if (!this.files.has(path)) {
      throw new Error('FileManager::getFile(): The file doesn\'t exist, cannot get !');
    }

    return this.files.get(path)!;
  }

  /**
   * Returns the URL of a file.
   * 
   * @param {string} path - The file path.
   */
  getFileURL(path: string, refresh: boolean = false): string {
    if (!this.urls.has(path)) {
      throw new Error('FileManager::getFileURL(): The file doesn\'t exist, cannot get !');
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
   * Returns the Blob of a file.
   * 
   * @param {string} path - The file path.
   */
  getFileBlob(path: string): Blob {
    if (!this.blobs.has(path)) {
      throw new Error('FileManager::getFileBlob(): The texture file doesn\'t exist, cannot get !');
    }

    return this.blobs.get(path)!;
  }

  /**
   * Checks if file exists.
   * 
   * @param {string} path - The file path.
   */
  hasFile(path: string): boolean {
    return this.files.has(path);
  }

  /**
   * Deletes all stored files.
   */
  releaseFiles(): void {
    for (const path of this.files.keys()) {
      const url = this.urls.get(path)!;
      URL.revokeObjectURL(url);

      this.files.delete(path);
      this.urls.delete(path);
      this.blobs.delete(path);
    }
  }
}

export const fileManager = new FileManager();