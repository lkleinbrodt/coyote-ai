import "./Boids.css"; // You'll need to create this file

import * as THREE from "three";

import { BOID_CONFIG, CAMERA_CONFIG } from "../config";

import { CameraController } from "../classes/CameraController";
import { ControlsTooltip } from "../components/ControlsTooltip";
import { Flock } from "../classes/Flock";
import { useEffect } from "react";

export default function Boids() {
  useEffect(() => {
    // Scene setup
    const scene = new THREE.Scene();

    // Add sky background
    scene.background = new THREE.Color(0x87ceeb); // Light blue sky color

    // Add ground plane
    const groundGeometry = new THREE.PlaneGeometry(
      BOID_CONFIG.bounds.width * 4,
      BOID_CONFIG.bounds.depth * 4
    );
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x90ee90, // Light green
      roughness: 0.8,
      metalness: 0.2,
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -BOID_CONFIG.bounds.height; // Position at bottom of bounding box
    scene.add(ground);

    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    // Add directional light (sunlight)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    const cameraController = new CameraController(CAMERA_CONFIG);

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    document.body.appendChild(renderer.domElement);

    // Create walls
    const wallGeometry = new THREE.BoxGeometry(
      BOID_CONFIG.bounds.width * 2,
      BOID_CONFIG.bounds.height * 2,
      BOID_CONFIG.bounds.depth * 2
    );
    const wallMaterial = new THREE.MeshBasicMaterial({
      color: 0x808080,
      transparent: true,
      opacity: 0.05, // Make walls more transparent
      side: THREE.BackSide,
      wireframe: true,
    });
    const walls = new THREE.Mesh(wallGeometry, wallMaterial);
    scene.add(walls);

    // Create flock
    const flock = new Flock(BOID_CONFIG, scene);

    // Handle space bar for reset
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === " ") {
        flock.reset();
        cameraController.reset();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    function animate() {
      cameraController.update();
      flock.update();
      renderer.render(scene, cameraController.getCamera());
    }

    renderer.setAnimationLoop(animate);

    // Handle window resize
    const handleResize = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", handleResize);

    // Cleanup function
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("resize", handleResize);
      cameraController.dispose();
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
