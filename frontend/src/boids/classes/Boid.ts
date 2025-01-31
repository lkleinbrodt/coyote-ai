import * as THREE from "three";

import { BoidConfig } from "../types";

export class Boid {
  mesh: THREE.Mesh;
  velocity: THREE.Vector3;
  private hue: number;
  private readonly constantColor: boolean;
  private readonly config: BoidConfig;

  constructor(config: BoidConfig, index: number) {
    this.config = config;

    // Create geometry
    const geometry = new THREE.ConeGeometry(0.2, 0.5, 8);
    geometry.rotateX(Math.PI / 2); // Rotate to point forward

    // Initialize color
    this.hue = config.baseHue + (Math.random() * 2 - 1) * config.hueRange;
    const material = new THREE.MeshBasicMaterial({
      color: new THREE.Color().setHSL(this.hue, 1, 0.5),
    });

    // Create mesh
    this.mesh = new THREE.Mesh(geometry, material);

    // Initialize properties
    this.constantColor =
      index < Math.floor(config.numBoids * config.constantColorPercentage);
    this.velocity = new THREE.Vector3(
      (Math.random() - 0.5) * 0.1,
      (Math.random() - 0.5) * 0.1,
      (Math.random() - 0.5) * 0.1
    );

    // Set initial position
    this.setRandomPosition();
  }

  setRandomPosition(): void {
    const bounds = this.config.bounds;
    this.mesh.position.set(
      (Math.random() - 0.5) * (bounds.width * 2),
      (Math.random() - 0.5) * (bounds.height * 2),
      (Math.random() - 0.5) * (bounds.depth * 2)
    );
  }

  updatePosition(): void {
    this.mesh.position.add(this.velocity);
    this.mesh.lookAt(this.mesh.position.clone().add(this.velocity));
    this.enforcePositionBounds();
  }

  enforcePositionBounds(): void {
    const bounds = this.config.bounds;
    this.mesh.position.x = Math.max(
      -bounds.width,
      Math.min(bounds.width, this.mesh.position.x)
    );
    this.mesh.position.y = Math.max(
      -bounds.height,
      Math.min(bounds.height, this.mesh.position.y)
    );
    this.mesh.position.z = Math.max(
      -bounds.depth,
      Math.min(bounds.depth, this.mesh.position.z)
    );
  }

  applyForce(force: THREE.Vector3): void {
    this.velocity.add(force);
    this.enforceSpeedLimits();
  }

  enforceSpeedLimits(): void {
    const speed = this.velocity.length();
    if (speed > this.config.maxSpeed) {
      this.velocity.multiplyScalar(this.config.maxSpeed / speed);
    } else if (speed < this.config.minSpeed) {
      this.velocity.multiplyScalar(this.config.minSpeed / speed);
    }
  }

  updateColor(averageHue: number, nearbyCount: number): void {
    if (this.constantColor || nearbyCount === 0) return;

    this.hue +=
      (averageHue - this.hue) *
      this.config.colorUpdateSpeed *
      this.config.colorInfluenceFactor;

    // Keep hue within range
    const hueDiff = ((this.hue - this.config.baseHue + 0.5) % 1) - 0.5;
    this.hue =
      this.config.baseHue +
      Math.max(-this.config.hueRange, Math.min(this.config.hueRange, hueDiff));

    (this.mesh.material as THREE.MeshBasicMaterial).color.setHSL(
      this.hue,
      1,
      0.5
    );
  }

  reset(): void {
    this.setRandomPosition();
    this.velocity.set(
      (Math.random() - 0.5) * 0.1,
      (Math.random() - 0.5) * 0.1,
      (Math.random() - 0.5) * 0.1
    );

    const newHue =
      this.config.baseHue + (Math.random() * 2 - 1) * this.config.hueRange;
    this.hue = newHue;
    (this.mesh.material as THREE.MeshBasicMaterial).color.setHSL(
      newHue,
      1,
      0.5
    );
  }

  // Getter methods
  getPosition(): THREE.Vector3 {
    return this.mesh.position;
  }

  getVelocity(): THREE.Vector3 {
    return this.velocity;
  }

  getHue(): number {
    return this.hue;
  }
}
