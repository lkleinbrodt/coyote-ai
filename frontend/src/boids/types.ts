import * as THREE from "three";

export interface BoidConfig {
  baseHue: number;
  hueRange: number;
  colorInfluenceFactor: number;
  visualRange: number;
  centeringFactor: number;
  matchingFactor: number;
  avoidFactor: number;
  wallAvoidFactor: number;
  maxSpeed: number;
  minSpeed: number;
  bounds: {
    width: number;
    height: number;
    depth: number;
  };
  margin: number;
  colorUpdateSpeed: number;
  numBoids: number;
  constantColorPercentage: number;
}

export interface CameraConfig {
  moveSpeed: number;
  rotateSpeed: number;
  initialPosition: THREE.Vector3;
}

export interface Boid extends THREE.Mesh {
  userData: {
    velocity: THREE.Vector3;
    hue: number;
    constantColor: boolean;
  };
}
