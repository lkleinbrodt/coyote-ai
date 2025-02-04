import * as THREE from "three";

import { Boid } from "./Boid";
import { BoidConfig } from "../types";

export class Flock {
  private boids: Boid[] = [];
  private readonly config: BoidConfig;

  constructor(config: BoidConfig, scene: THREE.Scene) {
    this.config = config;
    this.initializeBoids(scene);
  }

  private initializeBoids(scene: THREE.Scene): void {
    for (let i = 0; i < this.config.numBoids; i++) {
      const boid = new Boid(this.config, i);
      scene.add(boid.mesh);
      this.boids.push(boid);
    }
  }

  update(): void {
    this.boids.forEach((boid) => {
      const acceleration = this.calculateAcceleration(boid);
      boid.applyForce(acceleration);
      boid.updatePosition();
    });
  }

  private calculateAcceleration(boid: Boid): THREE.Vector3 {
    const acceleration = new THREE.Vector3();
    const flockingForces = this.calculateFlockingForces(boid);
    const wallAvoidance = this.calculateWallAvoidance(boid);

    acceleration.add(flockingForces);
    acceleration.add(wallAvoidance);

    return acceleration;
  }

  private calculateFlockingForces(boid: Boid): THREE.Vector3 {
    let nearby = 0;
    const center = new THREE.Vector3();
    const avgVelocity = new THREE.Vector3();
    const separation = new THREE.Vector3();
    let avgHue = 0;

    this.boids.forEach((other) => {
      if (other !== boid) {
        const distance = boid.getPosition().distanceTo(other.getPosition());

        if (distance < this.config.visualRange) {
          // Cohesion - move towards center of mass
          center.add(other.getPosition());

          // Alignment - match velocity of neighbors
          avgVelocity.add(other.getVelocity());

          // Separation - avoid crowding
          if (distance < this.config.visualRange * 0.5) {
            const diff = boid.getPosition().clone().sub(other.getPosition());
            diff.divideScalar(distance * distance);
            separation.add(diff);
          }

          // Color influence
          avgHue += other.getHue();
          nearby++;
        }
      }
    });

    const forces = new THREE.Vector3();

    if (nearby > 0) {
      // Apply cohesion
      center.divideScalar(nearby);
      center.sub(boid.getPosition());
      center.multiplyScalar(this.config.centeringFactor);
      forces.add(center);

      // Apply alignment
      avgVelocity.divideScalar(nearby);
      avgVelocity.sub(boid.getVelocity());
      avgVelocity.multiplyScalar(this.config.matchingFactor);
      forces.add(avgVelocity);

      // Apply separation
      separation.multiplyScalar(this.config.avoidFactor);
      forces.add(separation);

      // Update color
      avgHue /= nearby;
      boid.updateColor(avgHue, nearby);
    }

    return forces;
  }

  private calculateWallAvoidance(boid: Boid): THREE.Vector3 {
    const wallAvoidance = new THREE.Vector3();
    const position = boid.getPosition();
    const bounds = this.config.bounds;
    const margin = this.config.margin;

    // X walls
    if (position.x > bounds.width - margin) {
      wallAvoidance.x = bounds.width - position.x - margin;
    } else if (position.x < -bounds.width + margin) {
      wallAvoidance.x = -bounds.width - position.x + margin;
    }

    // Y walls
    if (position.y > bounds.height - margin) {
      wallAvoidance.y = bounds.height - position.y - margin;
    } else if (position.y < -bounds.height + margin) {
      wallAvoidance.y = -bounds.height - position.y + margin;
    }

    // Z walls
    if (position.z > bounds.depth - margin) {
      wallAvoidance.z = bounds.depth - position.z - margin;
    } else if (position.z < -bounds.depth + margin) {
      wallAvoidance.z = -bounds.depth - position.z + margin;
    }

    wallAvoidance.multiplyScalar(this.config.wallAvoidFactor);
    return wallAvoidance;
  }

  reset(): void {
    this.boids.forEach((boid) => boid.reset());
  }

  getBoids(): Boid[] {
    return this.boids;
  }

  setMaxSpeed(speed: number): void {
    this.config.maxSpeed = speed;
    // Update minSpeed to maintain the same ratio with maxSpeed
    this.config.minSpeed = speed * 0.5;
  }
}
