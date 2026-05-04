import { gfx3Manager } from '@lib/legacy';
import { gfx3MeshRenderer } from '@lib/legacy';
import { gfx3ParticlesRenderer } from '@lib/legacy';
import { gfx3WaterRenderer } from '@lib/legacy';
import { gfx3SkyboxRenderer } from '@lib/legacy';
import { Screen } from '@lib/legacy';
import { Gfx3MeshJSM } from '@lib/legacy';
import { EnginePack3D } from '@lib/legacy';
import { gfx3DebugRenderer } from '@lib/legacy';
// ---------------------------------------------------------------------------------------

class GameScreen extends Screen {
  pack: EnginePack3D;
  player: Gfx3MeshJSM;

  constructor() {
    super();
    this.pack = new EnginePack3D();
    this.player = new Gfx3MeshJSM();
  }

  async onEnter() {
    this.pack = await EnginePack3D.createFromFile('orbit', './scene.blend.pak');
    this.player = this.pack.jsm.getObject('Player');

    this.player.setRotationY(0.3);

    gfx3MeshRenderer.setDirLight(true, [0, -1, -1], [1, 1, 1], [0.2, 0.2, 0.2]);
  }

  update(ts: number) {
    this.pack.update(ts);
    // this.player.rotate(0, ts * 0.001, 0);
  }

  draw() {
    gfx3Manager.beginDrawing();
    this.pack.draw();
    gfx3Manager.endDrawing();
  }

  render(ts: number) {
    gfx3Manager.beginRender();
    gfx3Manager.beginPassRender(0);
    
    gfx3SkyboxRenderer.render();
    gfx3MeshRenderer.render(ts);
    
    gfx3ParticlesRenderer.render();
    gfx3WaterRenderer.render();
    gfx3DebugRenderer.render();

    gfx3Manager.endPassRender();
    gfx3Manager.endRender();
  }
}

export { GameScreen };