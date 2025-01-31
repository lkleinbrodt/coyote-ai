import "./Boids.css"; // You'll need to create this file

import * as THREE from "three";

import { BOID_CONFIG, CAMERA_CONFIG } from "../config";

import { Boid } from "../classes/Boid";
import { ControlsTooltip } from "../components/ControlsTooltip";
import { useEffect } from "react";

export default function OriginalBoid() {
  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Create walls
    const wallGeometry = new THREE.BoxGeometry(
      BOID_CONFIG.bounds * 2,
      BOID_CONFIG.bounds * 2,
      BOID_CONFIG.bounds * 2
    );
    const wallMaterial = new THREE.MeshBasicMaterial({
      color: 0x808080,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide,
      wireframe: true,
    });
    const walls = new THREE.Mesh(wallGeometry, wallMaterial);
    scene.add(walls);

    // Create boids using new Boid class
    const boids: Boid[] = [];
    for (let i = 0; i < BOID_CONFIG.numBoids; i++) {
      const boid = new Boid(BOID_CONFIG, i);
      scene.add(boid.mesh);
      boids.push(boid);
    }

    camera.position.copy(CAMERA_CONFIG.initialPosition);
    camera.lookAt(0, 0, 0); // Look at the center of the scene

    // Camera control parameters
    const cameraState = {
      moveSpeed: CAMERA_CONFIG.moveSpeed,
      rotateSpeed: CAMERA_CONFIG.rotateSpeed,
      moveVector: new THREE.Vector3(),
      keysPressed: new Set(),
    };

    // Handle key events
    const handleKeyDown = (event: KeyboardEvent) => {
      cameraState.keysPressed.add(event.key);
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      cameraState.keysPressed.delete(event.key);
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    function updateCamera() {
      // Rotation controls (arrow keys)
      if (cameraState.keysPressed.has("ArrowLeft")) {
        camera.rotateY(cameraState.rotateSpeed);
      }
      if (cameraState.keysPressed.has("ArrowRight")) {
        camera.rotateY(-cameraState.rotateSpeed);
      }
      if (cameraState.keysPressed.has("ArrowUp")) {
        camera.rotateX(cameraState.rotateSpeed);
      }
      if (cameraState.keysPressed.has("ArrowDown")) {
        camera.rotateX(-cameraState.rotateSpeed);
      }

      // Movement controls (WASD + QE)
      cameraState.moveVector.set(0, 0, 0);

      if (cameraState.keysPressed.has("w")) {
        cameraState.moveVector.z = -cameraState.moveSpeed;
      }
      if (cameraState.keysPressed.has("s")) {
        cameraState.moveVector.z = cameraState.moveSpeed;
      }
      if (cameraState.keysPressed.has("a")) {
        cameraState.moveVector.x = -cameraState.moveSpeed;
      }
      if (cameraState.keysPressed.has("d")) {
        cameraState.moveVector.x = cameraState.moveSpeed;
      }
      if (cameraState.keysPressed.has("q")) {
        cameraState.moveVector.y = -cameraState.moveSpeed;
      }
      if (cameraState.keysPressed.has("e")) {
        cameraState.moveVector.y = cameraState.moveSpeed;
      }

      // Apply movement relative to camera's rotation
      camera.translateX(cameraState.moveVector.x);
      camera.translateY(cameraState.moveVector.y);
      camera.translateZ(cameraState.moveVector.z);

      // Handle space bar for reset
      if (cameraState.keysPressed.has(" ")) {
        boids.forEach((boid) => boid.reset());
        camera.position.copy(CAMERA_CONFIG.initialPosition);
        camera.lookAt(0, 0, 0);
        cameraState.keysPressed.delete(" "); // Remove to prevent continuous reset
      }
    }

    function animate() {
      updateCamera();

      boids.forEach((boid) => {
        const acceleration = new THREE.Vector3();

        // Calculate flocking behavior
        let nearby = 0;
        const center = new THREE.Vector3();
        const avgVelocity = new THREE.Vector3();
        const separation = new THREE.Vector3();

        boids.forEach((other) => {
          if (other !== boid) {
            const distance = boid.getPosition().distanceTo(other.getPosition());

            if (distance < BOID_CONFIG.visualRange) {
              // Cohesion - move towards center of mass
              center.add(other.getPosition());

              // Alignment - match velocity of neighbors
              avgVelocity.add(other.getVelocity());

              // Separation - avoid crowding
              if (distance < BOID_CONFIG.visualRange * 0.5) {
                const diff = boid
                  .getPosition()
                  .clone()
                  .sub(other.getPosition());
                diff.divideScalar(distance * distance);
                separation.add(diff);
              }

              nearby++;
            }
          }
        });

        if (nearby > 0) {
          // Apply cohesion
          center.divideScalar(nearby);
          center.sub(boid.getPosition());
          center.multiplyScalar(BOID_CONFIG.centeringFactor);
          acceleration.add(center);

          // Apply alignment
          avgVelocity.divideScalar(nearby);
          avgVelocity.sub(boid.getVelocity());
          avgVelocity.multiplyScalar(BOID_CONFIG.matchingFactor);
          acceleration.add(avgVelocity);

          // Apply separation
          separation.multiplyScalar(BOID_CONFIG.avoidFactor);
          acceleration.add(separation);
        }

        // Calculate average hue for color updates
        if (nearby > 0) {
          let avgHue = 0;
          boids.forEach((other) => {
            if (other !== boid) {
              const distance = boid
                .getPosition()
                .distanceTo(other.getPosition());
              if (distance < BOID_CONFIG.visualRange) {
                avgHue += other.getHue();
              }
            }
          });
          avgHue /= nearby;
          boid.updateColor(avgHue, nearby);
        }

        // Add wall avoidance
        const wallAvoidance = new THREE.Vector3();
        const position = boid.getPosition();
        const bounds = BOID_CONFIG.bounds;
        const margin = BOID_CONFIG.margin;

        // X walls
        if (position.x > bounds - margin) {
          wallAvoidance.x = bounds - position.x - margin;
        } else if (position.x < -bounds + margin) {
          wallAvoidance.x = -bounds - position.x + margin;
        }

        // Y walls
        if (position.y > bounds - margin) {
          wallAvoidance.y = bounds - position.y - margin;
        } else if (position.y < -bounds + margin) {
          wallAvoidance.y = -bounds - position.y + margin;
        }

        // Z walls
        if (position.z > bounds - margin) {
          wallAvoidance.z = bounds - position.z - margin;
        } else if (position.z < -bounds + margin) {
          wallAvoidance.z = -bounds - position.z + margin;
        }

        wallAvoidance.multiplyScalar(BOID_CONFIG.wallAvoidFactor);
        acceleration.add(wallAvoidance);

        // Apply forces and update position
        boid.applyForce(acceleration);
        boid.updatePosition();
      });

      renderer.render(scene, camera);
    }
    renderer.setAnimationLoop(animate);

    // Cleanup function
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      document.body.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, []);

  return (
    <div id="visualization-container">
      <ControlsTooltip />
    </div>
  );
}
