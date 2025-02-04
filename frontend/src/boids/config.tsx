import * as THREE from "three";

import { BoidConfig, CameraConfig } from "./types";

const BOID_CONFIG: BoidConfig = {
  // Color configuration
  baseHue: Math.random(), // Random starting hue for the flock
  hueRange: 0.9, // How much the hue can vary from the base hue
  colorInfluenceFactor: 0.1, // How much a boid's color is influenced by neighbors
  colorUpdateSpeed: 0.8, // How quickly colors change

  // Movement and flocking behavior
  visualRange: 2.5, // Distance within which boids can see each other
  centeringFactor: 0.005, // Cohesion - strength of attraction to flock center
  matchingFactor: 0.05, // Alignment - strength of velocity matching
  avoidFactor: 0.05, // Separation - strength of collision avoidance
  wallAvoidFactor: 4, // Wall avoidance strength
  maxSpeed: 0.2, // Maximum movement speed
  minSpeed: 0.1, // Minimum movement speed

  // Environment configuration
  bounds: {
    width: 35, // X-axis
    height: 20, // Y-axis
    depth: 35, // Z-axis
  },
  margin: 3, // Distance from walls to start avoiding them

  // Flock configuration
  numBoids: 500, // Total number of boids
  constantColorPercentage: 0.1, // Percentage of boids that maintain constant color
};

const CAMERA_CONFIG: CameraConfig = {
  moveSpeed: 0.5,
  rotateSpeed: 0.02,
  initialPosition: new THREE.Vector3(28, 0, 28),
};

export { BOID_CONFIG, CAMERA_CONFIG };
