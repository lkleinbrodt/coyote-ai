import "./Boids.css"; // You'll need to create this file

import * as THREE from "three";

import { useEffect } from "react";

// Add these at the top of the file, after imports
const baseHue = Math.random(); // Random starting hue
const hueRange = 0.9; // How much the hue can vary

// Add this constant near the other boid parameters
const colorInfluenceFactor = 0.1; // How much a boid's color is influenced by neighbors

export default function Visualization() {
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

    // Create boids
    const boids = [];
    const numBoids = 250;
    const constantColorPercentage = 0.1; // 10% of boids will have constant colors
    const numConstantColorBoids = Math.floor(
      numBoids * constantColorPercentage
    );

    // Boid parameters
    const visualRange = 2.5;
    const centeringFactor = 0.005; // cohesion
    const matchingFactor = 0.05; // alignment
    const avoidFactor = 0.05; // separation
    const wallAvoidFactor = 0.5; // wall avoidance strength
    const maxSpeed = 0.2;
    const minSpeed = 0.1;
    const bounds = 15; // size of the box
    const margin = 2; // how far from walls to start avoiding

    // Add these constants near the other boid parameters
    const colorUpdateSpeed = 0.8; // How quickly colors change

    const wallGeometry = new THREE.BoxGeometry(
      bounds * 2,
      bounds * 2,
      bounds * 2
    );
    const wallMaterial = new THREE.MeshBasicMaterial({
      color: 0x808080,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide, // Render on the inside of the box
      wireframe: true,
    });
    const walls = new THREE.Mesh(wallGeometry, wallMaterial);
    scene.add(walls);

    // Create cone geometry for boids
    const geometry = new THREE.ConeGeometry(0.2, 0.5, 8);
    geometry.rotateX(Math.PI / 2); // Rotate to point forward

    for (let i = 0; i < numBoids; i++) {
      // Generate a random initial hue within the range
      const initialHue = baseHue + (Math.random() * 2 - 1) * hueRange;

      const material = new THREE.MeshBasicMaterial({
        color: new THREE.Color().setHSL(initialHue, 1, 0.5),
      });
      const boid = new THREE.Mesh(geometry, material);

      // Store the random initial hue
      boid.userData.hue = initialHue;

      // Determine if this boid should have a constant color
      boid.userData.constantColor = i < numConstantColorBoids;

      // Random initial positions and velocity
      boid.position.set(
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20
      );

      boid.userData.velocity = new THREE.Vector3(
        (Math.random() - 0.5) * 0.1,
        (Math.random() - 0.5) * 0.1,
        (Math.random() - 0.5) * 0.1
      );

      scene.add(boid);
      boids.push(boid);
    }

    camera.position.set(28, 0, 28); // Position camera at 45-degree angle
    camera.lookAt(0, 0, 0); // Look at the center of the scene

    // Camera control parameters
    const cameraState = {
      moveSpeed: 0.5,
      rotateSpeed: 0.02,
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
        boids.forEach(resetBoid);
        // Reset camera position and rotation
        camera.position.set(28, 28, 28);
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
            const distance = boid.position.distanceTo(other.position);

            if (distance < visualRange) {
              // Cohesion - move towards center of mass
              center.add(other.position);

              // Alignment - match velocity of neighbors
              avgVelocity.add(other.userData.velocity);

              // Separation - avoid crowding
              if (distance < visualRange * 0.5) {
                const diff = boid.position.clone().sub(other.position);
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
          center.sub(boid.position);
          center.multiplyScalar(centeringFactor);
          acceleration.add(center);

          // Apply alignment
          avgVelocity.divideScalar(nearby);
          avgVelocity.sub(boid.userData.velocity);
          avgVelocity.multiplyScalar(matchingFactor);
          acceleration.add(avgVelocity);

          // Apply separation
          separation.multiplyScalar(avoidFactor);
          acceleration.add(separation);
        }

        if (!boid.userData.constantColor && nearby > 0) {
          // Calculate average hue of nearby boids
          let avgHue = 0;
          boids.forEach((other) => {
            if (other !== boid) {
              const distance = boid.position.distanceTo(other.position);
              if (distance < visualRange) {
                avgHue += other.userData.hue;
              }
            }
          });
          avgHue /= nearby;

          // Smoothly transition the boid's hue towards the average
          boid.userData.hue +=
            (avgHue - boid.userData.hue) *
            colorUpdateSpeed *
            colorInfluenceFactor;

          // Ensure hue stays within the desired range around baseHue
          const hueDiff = ((boid.userData.hue - baseHue + 0.5) % 1) - 0.5;
          boid.userData.hue =
            baseHue + Math.max(-hueRange, Math.min(hueRange, hueDiff));

          // Update the boid's color
          (boid.material as THREE.MeshBasicMaterial).color.setHSL(
            boid.userData.hue,
            1,
            0.5
          );
        }

        // Add wall avoidance
        const wallAvoidance = new THREE.Vector3();

        // X walls
        if (boid.position.x > bounds - margin) {
          wallAvoidance.x = bounds - boid.position.x - margin;
        } else if (boid.position.x < -bounds + margin) {
          wallAvoidance.x = -bounds - boid.position.x + margin;
        }

        // Y walls
        if (boid.position.y > bounds - margin) {
          wallAvoidance.y = bounds - boid.position.y - margin;
        } else if (boid.position.y < -bounds + margin) {
          wallAvoidance.y = -bounds - boid.position.y + margin;
        }

        // Z walls
        if (boid.position.z > bounds - margin) {
          wallAvoidance.z = bounds - boid.position.z - margin;
        } else if (boid.position.z < -bounds + margin) {
          wallAvoidance.z = -bounds - boid.position.z + margin;
        }

        wallAvoidance.multiplyScalar(wallAvoidFactor);
        acceleration.add(wallAvoidance);

        // Update velocity and position
        boid.userData.velocity.add(acceleration);

        // Limit speed
        const speed = boid.userData.velocity.length();
        if (speed > maxSpeed) {
          boid.userData.velocity.multiplyScalar(maxSpeed / speed);
        } else if (speed < minSpeed) {
          boid.userData.velocity.multiplyScalar(minSpeed / speed);
        }

        // Update position
        boid.position.add(boid.userData.velocity);

        // Point in direction of movement
        boid.lookAt(boid.position.clone().add(boid.userData.velocity));

        // Ensure boids stay within bounds
        boid.position.x = Math.max(-bounds, Math.min(bounds, boid.position.x));
        boid.position.y = Math.max(-bounds, Math.min(bounds, boid.position.y));
        boid.position.z = Math.max(-bounds, Math.min(bounds, boid.position.z));
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
      <div className="controls-tooltip">
        <h3>Camera Controls</h3>
        <div className="control-section">
          <div className="control-group">
            <div className="key-group">
              <div className="key">↑</div>
              <div className="key-row">
                <div className="key">←</div>
                <div className="key">↓</div>
                <div className="key">→</div>
              </div>
            </div>
            <span>Rotate Camera</span>
          </div>

          <div className="control-group">
            <div className="key-group">
              <div className="key">W</div>
              <div className="key-row">
                <div className="key">A</div>
                <div className="key">S</div>
                <div className="key">D</div>
              </div>
            </div>
            <span>Move Camera</span>
          </div>

          <div className="control-group">
            <div className="key-row">
              <div className="key">Q</div>
              <div className="key">E</div>
            </div>
            <span>Up / Down</span>
          </div>

          <div className="control-group">
            <div className="key-row">
              <div className="key">Space</div>
            </div>
            <span>Reset</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Add this function near the other boid-related functions
function resetBoid(boid: THREE.Mesh) {
  // Reset position
  boid.position.set(
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20
  );

  // Reset velocity
  boid.userData.velocity.set(
    (Math.random() - 0.5) * 0.1,
    (Math.random() - 0.5) * 0.1,
    (Math.random() - 0.5) * 0.1
  );

  // Reset color
  const newHue = baseHue + (Math.random() * 2 - 1) * hueRange;
  boid.userData.hue = newHue;
  (boid.material as THREE.MeshBasicMaterial).color.setHSL(newHue, 1, 0.5);
}
