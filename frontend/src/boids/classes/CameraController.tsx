import * as THREE from "three";

import { CameraConfig } from "../types";

export class CameraController {
  private camera: THREE.PerspectiveCamera;
  private readonly config: CameraConfig;
  private moveVector: THREE.Vector3;
  private keysPressed: Set<string>;

  constructor(config: CameraConfig) {
    this.config = config;
    this.moveVector = new THREE.Vector3();
    this.keysPressed = new Set();

    // Initialize camera
    this.camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    this.reset();

    // Bind event listeners
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleResize = this.handleResize.bind(this);

    // Add event listeners
    window.addEventListener("keydown", this.handleKeyDown);
    window.addEventListener("keyup", this.handleKeyUp);
    window.addEventListener("resize", this.handleResize);
  }

  private handleKeyDown(event: KeyboardEvent): void {
    this.keysPressed.add(event.key);
  }

  private handleKeyUp(event: KeyboardEvent): void {
    this.keysPressed.delete(event.key);
  }

  private handleResize(): void {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
  }

  update(): void {
    // Handle rotation (arrow keys)
    if (this.keysPressed.has("ArrowLeft")) {
      this.camera.rotateY(this.config.rotateSpeed);
    }
    if (this.keysPressed.has("ArrowRight")) {
      this.camera.rotateY(-this.config.rotateSpeed);
    }
    if (this.keysPressed.has("ArrowUp")) {
      this.camera.rotateX(this.config.rotateSpeed);
    }
    if (this.keysPressed.has("ArrowDown")) {
      this.camera.rotateX(-this.config.rotateSpeed);
    }

    // Handle movement (WASD + QE)
    this.moveVector.set(0, 0, 0);

    if (this.keysPressed.has("w")) {
      this.moveVector.z = -this.config.moveSpeed;
    }
    if (this.keysPressed.has("s")) {
      this.moveVector.z = this.config.moveSpeed;
    }
    if (this.keysPressed.has("a")) {
      this.moveVector.x = -this.config.moveSpeed;
    }
    if (this.keysPressed.has("d")) {
      this.moveVector.x = this.config.moveSpeed;
    }
    if (this.keysPressed.has("q")) {
      this.moveVector.y = -this.config.moveSpeed;
    }
    if (this.keysPressed.has("e")) {
      this.moveVector.y = this.config.moveSpeed;
    }

    // Apply movement relative to camera's rotation
    this.camera.translateX(this.moveVector.x);
    this.camera.translateY(this.moveVector.y);
    this.camera.translateZ(this.moveVector.z);
  }

  reset(): void {
    this.camera.position.copy(this.config.initialPosition);
    this.camera.lookAt(0, 0, 0);
  }

  getCamera(): THREE.PerspectiveCamera {
    return this.camera;
  }

  dispose(): void {
    window.removeEventListener("keydown", this.handleKeyDown);
    window.removeEventListener("keyup", this.handleKeyUp);
    window.removeEventListener("resize", this.handleResize);
  }
}
