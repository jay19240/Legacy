import { eventManager } from '../core/event_manager';
import { coreManager } from '../core/core_manager';

export interface InputPad {
  index: number;
  id: string;
  nButtons: number;
  nAxes: number;
  axes: Array<number>;
  hat: Array<number>;
  pressed: Array<boolean>;
}

export interface InputAction {
  id: string;
  inputSource: InputSource;
  eventKey: string;
}

export type InputSource = 'keyboard' | 'gamepad0' | 'gamepad1' | 'gamepad2' | 'gamepad3';
export enum InputPadAxis {
  UP = 0,
  DOWN = 1,
  LEFT = 2,
  RIGHT = 3
};

/**
 * Singleton input manager.
 * Handle various sources such as keyboard, mouse and gamepad.
 * It emit 'E_ACTION_ONCE' with data { actionId }.
 * It emit 'E_ACTION' with data { actionId }.
 * It emit 'E_ACTION_RELEASED' with data { actionId }
 * It emit 'E_MOUSE_DOWN' with data { buttons }
 * It emit 'E_MOUSE_DOWN_ONCE' with data { buttons }
 * It emit 'E_MOUSE_UP'
 * It emit 'E_MOUSE_MOVE' with data { movementX, movementY }
 * It emit 'E_MOUSE_DRAG' with data { movementX, movementY }
 * It emit 'E_MOUSE_WHEEL' with data { delta }
 * It emit 'E_POINTER_LOCK_CHANGED' with data { lockChanged }
 * It emit 'E_GAMEPAD_CONNECTED' with data { id }
 * It emit 'E_GAMEPAD_DISCONNECTED' with data { id }
 * It emit 'E_GAMEPAD_REMOVED' with data { id }
 * 
 * Default actions table:
 * ■ ACTION => KEYBOARD => GAMEPAD
 * ■ OK => Enter => 0
 * ■ BACK => Escape => 1
 * ■ SELECT => Space => BtnSelect
 * ■ LEFT => ArrowLeft => PadLeft
 * ■ RIGHT => ArrowRight => PadRight
 * ■ UP => ArrowUp => PadTop
 * ■ DOWN => ArrowDown => PadBottom
 */
export class InputManager {
  container: HTMLDivElement;
  keyMap: Map<string, boolean>;
  actionMap: Map<string, boolean>;
  actionOnceMap: Map<string, number>;
  actionRegister: Map<string, InputAction>;
  pads: Array<InputPad>;
  padsInterval: NodeJS.Timeout | number | undefined;
  mouseDown: boolean;
  mousePosition: vec2;
  mouseWheel: number;
  dragStartPosition: vec2;
  pointerLockEnabled: boolean;
  pointerLockCaptured: boolean;
  gamepadEnabled: boolean;

  constructor() {
    this.container = <HTMLDivElement>document.getElementById('APP');
    this.keyMap = new Map<string, boolean>;
    this.actionMap = new Map<string, boolean>;
    this.actionOnceMap = new Map<string, number>;
    this.actionRegister = new Map<string, InputAction>;
    this.pads = [];
    this.padsInterval;
    this.mouseDown = false;
    this.mousePosition = [0, 0];
    this.mouseWheel = 0;
    this.dragStartPosition = [0, 0];
    this.pointerLockEnabled = false;
    this.pointerLockCaptured = false;
    this.gamepadEnabled = false;

    document.addEventListener('keydown', (e) => this.#handleKeyDown(e));
    document.addEventListener('keyup', (e) => this.#handleKeyUp(e));
    document.addEventListener('pointerdown', (e) => this.#handlePointerDown(e));
    document.addEventListener('pointerup', (e) => this.#handlePointerUp(e));
    document.addEventListener('pointermove', (e) => this.#handlePointerMove(e));
    document.addEventListener('wheel', (e) => this.#handleWheel(e), { passive: false });
    document.addEventListener('pointerlockchange', (e) => this.#handlePointerLockChanged(e), false);
    window.addEventListener('gamepadconnected', (e) => this.#handleGamePadConnected(e));
    window.addEventListener('gamepaddisconnected', (e) => this.#handleGamePadDisconnected(e));

    this.registerAction('keyboard', 'Enter', 'OK');
    this.registerAction('keyboard', 'Escape', 'BACK');
    this.registerAction('keyboard', 'Space', 'SELECT');
    this.registerAction('keyboard', 'ArrowLeft', 'LEFT');
    this.registerAction('keyboard', 'ArrowRight', 'RIGHT');
    this.registerAction('keyboard', 'ArrowUp', 'UP');
    this.registerAction('keyboard', 'ArrowDown', 'DOWN');

    this.registerAction('gamepad0', '0', 'OK');
    this.registerAction('gamepad0', '1', 'BACK');
    this.registerAction('gamepad0', '9', 'SELECT');
    this.registerAction('gamepad0', 'left', 'LEFT');
    this.registerAction('gamepad0', 'right', 'RIGHT');
    this.registerAction('gamepad0', 'up', 'UP');
    this.registerAction('gamepad0', 'down', 'DOWN');

    this.registerAction('gamepad1', '0', 'OK');
    this.registerAction('gamepad1', '1', 'BACK');
    this.registerAction('gamepad1', '9', 'SELECT');
    this.registerAction('gamepad1', 'left', 'LEFT');
    this.registerAction('gamepad1', 'right', 'RIGHT');
    this.registerAction('gamepad1', 'up', 'UP');
    this.registerAction('gamepad1', 'down', 'DOWN');

    this.registerAction('gamepad2', '0', 'OK');
    this.registerAction('gamepad2', '1', 'BACK');
    this.registerAction('gamepad2', '9', 'SELECT');
    this.registerAction('gamepad2', 'left', 'LEFT');
    this.registerAction('gamepad2', 'right', 'RIGHT');
    this.registerAction('gamepad2', 'up', 'UP');
    this.registerAction('gamepad2', 'down', 'DOWN');

    this.registerAction('gamepad3', '0', 'OK');
    this.registerAction('gamepad3', '1', 'BACK');
    this.registerAction('gamepad3', '9', 'SELECT');
    this.registerAction('gamepad3', 'left', 'LEFT');
    this.registerAction('gamepad3', 'right', 'RIGHT');
    this.registerAction('gamepad3', 'up', 'UP');
    this.registerAction('gamepad3', 'down', 'DOWN');
  }

  /**
   * The update function.
   * 
   * @param {number} ts - The timestep.
   */
  update(ts: number): void {
    if (this.gamepadEnabled) {
      this.#updatePadsStatus();
    }

    for (const actionId of this.actionOnceMap.keys()) {
      const state = this.actionOnceMap.get(actionId);
      if (state == 1) {
        this.actionOnceMap.delete(actionId);
      }
      else {
        this.actionOnceMap.set(actionId, 1);
      }
    }
  }

  /**
   * Clear actions cache.
   */
  clearActionsCache() {
    this.actionMap.clear();
    this.actionOnceMap.clear();
  }

  /**
   * Enable or not the gamepad support.
   * 
   * @param {boolean} enabled - The enabled flag.
   */
  enableGamepad(enabled: boolean) {
    this.gamepadEnabled = enabled;
  }

  /**
   * Add an action mapping.
   * 
   * @param {string} inputSource - The device from which the input is received.
   * @param {string} eventKey - The key or button that triggers the action.
   * @param {string} actionId - The unique action identifier.
   */
  registerAction(inputSource: InputSource, eventKey: string, actionId: string): void {
    this.actionRegister.set(inputSource + eventKey, {
      id: actionId,
      inputSource: inputSource,
      eventKey: eventKey
    });
  }

  /**
   * Remove an action mapping.
   * 
   * @param {string} inputSource - The device from which the input is received.
   * @param {string} eventKey - The key or button that triggers the action.
   */
  unregisterAction(inputSource: InputSource, eventKey: string): void {
    this.actionRegister.delete(inputSource + eventKey);
  }

  /**
   * Checks if an action is currently active.
   * 
   * @param {string} actionId - The action identifier.
   */
  isActiveAction(actionId: string): boolean | undefined {
    return this.actionMap.get(actionId);
  }

  /**
   * Checks if an action is just active.
   * 
   * @param {string} actionId - The action identifier.
   */
  isJustActiveAction(actionId: string): boolean {
    return this.actionOnceMap.get(actionId) == 1;
  }

  /**
   * Checks if all specified actions is currently active.
   * 
   * @param {Array<string>} actionIds - The action identifier.
   */
  isActiveActions(actionIds: Array<string>): boolean {
    for (const actionId of actionIds) {
      if (!this.actionMap.get(actionId)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Checks if all specified actions is just active.
   * 
   * @param {Array<string>} actionIds - The action identifier.
   */
  isJustActiveActions(actionIds: Array<string>): boolean {
    for (const actionId of actionIds) {
      if (this.actionOnceMap.get(actionId) != 1) {
        return false;
      }
    }

    return true;
  }

  /**
   * Checks if mouse click is currently active.
   */
  isMouseDown(): boolean {
    return this.mouseDown;
  }

  /**
   * Returns the mouse position.
   */
  getMousePosition(): vec2 {
    return this.mousePosition;
  }

  /**
   * Returns the mouse wheel value.
   */
  getMouseWheel(): number {
    return this.mouseWheel;
  }

  /**
   * Checks if pointer lock is enabled.
   */
  isPointerLockEnabled(): boolean {
    return this.pointerLockEnabled;
  }

  /**
   * Checks if pointer lock is captured.
   */
  isPointerLockCaptured(): boolean {
    return this.pointerLockCaptured;
  }

  /**
   * Enable pointer lock state.
   * 
   * @param {boolean} enabled - The enabled flag.
   */
  setPointerLockEnabled(enabled: boolean): void {
    this.pointerLockEnabled = enabled;
  }

  /**
   * Returns the current drag movement.
   */
  getMouseDragDelta(): vec2 {
    if (!this.mouseDown) {
      return [0, 0];
    }

    return [
      this.mousePosition[0] - this.dragStartPosition[0],
      this.mousePosition[1] - this.dragStartPosition[1]
    ];
  }

  /**
   * Returns a pad or undefined if not found.
   * Note: Pads are automatically added on plug-in.
   * 
   * @param {number} index - The index of the pad.
   */
  getPad(index: number): InputPad | undefined {
    return this.pads.find(p => p.index == index);
  }

  /**
   * Returns a pad axis value or zero if not found.
   *
   * @param {number} index - The index of the pad.
   * @param {number} axis - The index of the pad.
   */
  getPadAxis(index: number, axis: number): number {
    const pad = this.pads.find(p => p.index == index);
    if (!pad) return 0;
    return pad.axes[axis] ?? 0;
  }

  /**
   * Returns the analog stick position as a vec2, with an optional deadzone.
   *
   * @param {number} index - The index of the pad.
   * @param {0 | 1} stick - The stick to read (0 = left, 1 = right).
   * @param {number} deadzone - Radial deadzone below which [0, 0] is returned.
   */
  getPadStick(index: number, stick: 0 | 1, deadzone: number = 0.15): vec2 {
    const pad = this.pads.find(p => p.index == index);
    if (!pad) return [0, 0];
    const x = pad.axes[stick * 2] ?? 0;
    const y = pad.axes[stick * 2 + 1] ?? 0;
    if (Math.hypot(x, y) < deadzone) return [0, 0];
    return [x, y];
  }

  /**
   * Removes a pad.
   * 
   * @param {string} id - The unique identifier of the pad
   */
  removePad(id: string): void {
    this.pads = this.pads.filter(p => p.id != id);
    if (this.pads.length <= 0) {
      clearInterval(this.padsInterval);
      this.padsInterval = undefined;
    }

    eventManager.emit(this, 'E_GAMEPAD_REMOVED', { id: id });
  }

  #addPad(pad: InputPad): void {
    this.pads.push(pad);
  }

  #handleKeyDown(e: KeyboardEvent): boolean {
    const action = this.actionRegister.get('keyboard' + e.code);

    if (!this.keyMap.get(e.code) && action) {
      eventManager.emit(this, 'E_ACTION_ONCE', { e: e, actionId: action.id });
      this.actionMap.set(action.id, true);
      this.actionOnceMap.set(action.id, 0);
    }

    if (action) {
      eventManager.emit(this, 'E_ACTION', { e: e, actionId: action.id });
      this.actionMap.set(action.id, true);
    }

    this.keyMap.set(e.code, true);
    return false;
  }

  #handleKeyUp(e: KeyboardEvent): void {
    const action = this.actionRegister.get('keyboard' + e.code);
    if (action) {
      eventManager.emit(this, 'E_ACTION_RELEASED', { e: e, actionId: action.id });
      this.actionMap.set(action.id, false);
    }

    this.keyMap.set(e.code, false);
  }

  async #handlePointerDown(e: PointerEvent): Promise<void> {
    if (this.pointerLockEnabled && !document.pointerLockElement) {
      await document.body.requestPointerLock();
    }

    const pos = coreManager.getContainerPosFromDocument(e.clientX, e.clientY);
    if (pos[0] == Infinity || pos[1] == Infinity) {
      return;
    }

    if (!this.mouseDown) {
      this.mouseDown = true;
      this.dragStartPosition[0] = pos[0];
      this.dragStartPosition[1] = pos[1];
      eventManager.emit(this, 'E_MOUSE_DOWN_ONCE', { e: e, buttons: e.buttons, x: pos[0], y: pos[1] });
    }

    this.mouseDown = true;
    this.dragStartPosition[0] = pos[0];
    this.dragStartPosition[1] = pos[1];
    eventManager.emit(this, 'E_MOUSE_DOWN', { e: e, buttons: e.buttons, x: pos[0], y: pos[1] });
  }

  #handlePointerUp(e: PointerEvent): void {
    const rect = this.container.getBoundingClientRect();
    const x = (e.clientX - rect.left) - (coreManager.getWidth() / 2);
    const y = (e.clientY - rect.top) - (coreManager.getHeight() / 2);

    this.mouseDown = false;
    this.dragStartPosition[0] = 0;
    this.dragStartPosition[1] = 0;
    eventManager.emit(this, 'E_MOUSE_UP', { e: e, x: x, y: y });
  }

  #handlePointerMove(e: PointerEvent): void {
    if (this.pointerLockEnabled && !this.pointerLockCaptured) {
      return;
    }

    const pos = coreManager.getContainerPosFromDocument(e.clientX, e.clientY);
    if (pos[0] == Infinity || pos[1] == Infinity) {
      return;
    }

    this.mouseDown = e.pointerType == 'mouse' ? (e.buttons & 1) !== 0 : true;
    this.mousePosition = [pos[0], pos[1]];

    eventManager.emit(this, 'E_MOUSE_MOVE', { e: e, movementX: e.movementX, movementY: e.movementY });

    if (this.mouseDown) {
      eventManager.emit(this, 'E_MOUSE_DRAG', { e: e, movementX: e.movementX, movementY: e.movementY });
    }
  }

  #handleWheel(e: WheelEvent): void {
    this.mouseDown = (e.buttons & 1) !== 0;
    this.mouseWheel += Math.sign(e.deltaY);
    eventManager.emit(this, 'E_MOUSE_WHEEL', { e: e, delta: Math.sign(e.deltaY) });
  }

  #handlePointerLockChanged(e: Event): void {
    if (!this.pointerLockEnabled) {
      return;
    }

    if (document.pointerLockElement == document.body) {
      this.pointerLockCaptured = true;
      eventManager.emit(this, 'E_POINTER_LOCK_CHANGED', { e: e, lockCaptured: true });
    }
    else {
      this.pointerLockCaptured = false;
      eventManager.emit(this, 'E_POINTER_LOCK_CHANGED', { e: e, lockCaptured: false });
    }
  }

  #handleGamePadDisconnected(e: GamepadEvent): void {
    this.removePad(e.gamepad.id);
    eventManager.emit(this, 'E_GAMEPAD_DISCONNECTED', { e: e, id: e.gamepad.id });
  }

  #handleGamePadConnected(e: GamepadEvent): void {
    const pad: InputPad = {
      index: e.gamepad.index,
      id: e.gamepad.id,
      nButtons: e.gamepad.buttons.length,
      nAxes: e.gamepad.axes.length,
      axes: [],
      hat: [0, 0, 0, 0],
      pressed: []
    };

    for (let i = 0; i < e.gamepad.buttons.length; i++) {
      pad.pressed[i] = e.gamepad.buttons[i].pressed;
    }

    this.#addPad(pad);
    eventManager.emit(this, 'E_GAMEPAD_CONNECTED', { e: e, id: e.gamepad.id });
  }

  #updatePadsStatus(): void {
    const navigator: any = window.navigator;
    const gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);

    for (const gamepad of gamepads) {
      if (!gamepad) {
        continue;
      }

      const pad = this.getPad(gamepad.index);

      if (pad != null) {
        // Analogs Sticks
        for (let i = 0; i < gamepad.axes.length; i++) {
          pad.axes[i] = gamepad.axes[i];
        }

        // D-Pad
        const hatAxis = gamepad.axes[9];
        let up, down, left, right = 0.0;
        if (hatAxis !== undefined && hatAxis <= 1.0 && hatAxis >= -1.0) {
          up = (hatAxis > -1.05 && hatAxis < -0.6 || hatAxis > 0.9) ? 1.0 : 0.0;
          down = (hatAxis > -0.2 && hatAxis < 0.2) ? 1.0 : 0.0;
          left = (hatAxis > 0.3 && hatAxis < 1.05) ? 1.0 : 0.0;
          right = (hatAxis > -0.8 && hatAxis < -0.3) ? 1.0 : 0.0;

          if (up) {
            const action = this.actionRegister.get('gamepad' + gamepad.index + 'up');
            if (!action) {
              return;
            }

            if (up != pad.hat[InputPadAxis.UP]) eventManager.emit(this, 'E_ACTION_ONCE', { actionId: action.id });
            eventManager.emit(this, 'E_ACTION', { actionId: action.id });
          }
          else if (down) {
            const action = this.actionRegister.get('gamepad' + gamepad.index + 'down');
            if (!action) {
              return;
            }

            if (down != pad.hat[InputPadAxis.DOWN]) eventManager.emit(this, 'E_ACTION_ONCE', { actionId: action.id });
            eventManager.emit(this, 'E_ACTION', { actionId: action.id });
          }
          else if (left) {
            const action = this.actionRegister.get('gamepad' + gamepad.index + 'left');
            if (!action) {
              return;
            }

            if (left != pad.hat[InputPadAxis.LEFT]) eventManager.emit(this, 'E_ACTION_ONCE', { actionId: action.id });
            eventManager.emit(this, 'E_ACTION', { actionId: action.id });
          }
          else if (right) {
            const action = this.actionRegister.get('gamepad' + gamepad.index + 'right');
            if (!action) {
              return;
            }

            if (right != pad.hat[InputPadAxis.RIGHT]) eventManager.emit(this, 'E_ACTION_ONCE', { actionId: action.id });
            eventManager.emit(this, 'E_ACTION', { actionId: action.id });
          }
        }

        pad.hat[InputPadAxis.UP] = up as number;
        pad.hat[InputPadAxis.DOWN] = down as number;
        pad.hat[InputPadAxis.LEFT] = left as number;
        pad.hat[InputPadAxis.RIGHT] = right as number;

        // Buttons
        for (let n = 0; n < gamepad.buttons.length; n++) {
          const action = this.actionRegister.get('gamepad' + gamepad.index + n);

          if (gamepad.buttons[n].pressed && !this.keyMap.get('gamepad' + gamepad.index + '-' + n) && action) {
            eventManager.emit(this, 'E_ACTION_ONCE', { actionId: action.id });
            this.actionOnceMap.set(action.id, 0);
          }

          if (gamepad.buttons[n].pressed && action) {
            eventManager.emit(this, 'E_ACTION', { actionId: action.id });
          }

          if (action) {
            this.actionMap.set(action.id, gamepad.buttons[n].pressed);
          }

          this.keyMap.set('gamepad' + gamepad.index + '-' + n, gamepad.buttons[n].pressed);
          pad.pressed[n] = gamepad.buttons[n].pressed;
        }
      }
    }
  }
}

export const inputManager = new InputManager();