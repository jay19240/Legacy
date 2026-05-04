export interface EnginePackItem<T> {
  name: string;
  ext: string;
  object: T;
  blobUrl: string;
};

export class EnginePackItemList<T> extends Map<string, EnginePackItem<T>> {
  constructor() {
    super();
  }

  getObject(name: string): T {
    const item = this.get(name);
    if (!item) {
      throw new Error('EnginePack::EnginePackItemList::getObject(): item not found !');
    }

    return item.object;
  }

  findWithRegex(regex: RegExp): T {
    for (const item of this.values()) {
      if (regex.test(item.name)) {
        return item.object;
      }
    }

    throw new Error(`EnginePackItemList::findWithRegex(): No match for ${regex}`);
  }
}