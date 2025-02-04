import "./Boids.css"; // You'll need to create this file

import * as THREE from "three";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { BOID_CONFIG, CAMERA_CONFIG } from "../config";
import { useEffect, useState } from "react";

import { BoidsTooltip } from "../components/BoidsTooltip";
import { CameraController } from "../classes/CameraController";
import { ControlsTooltip } from "../components/ControlsTooltip";
import { Flock } from "../classes/Flock";
import { Slider } from "@/components/ui/slider"; // You'll need to import this

export default function Boids() {
  const [speed, setSpeed] = useState(BOID_CONFIG.maxSpeed);
  const [flock, setFlock] = useState<Flock | null>(null);

  useEffect(() => {
    // Scene setup
    const scene = new THREE.Scene();

    // Add sky background
    scene.background = new THREE.Color(0x87ceeb); // Light blue sky color

    // Add ground plane
    const groundGeometry = new THREE.PlaneGeometry(
      BOID_CONFIG.bounds.width * 2,
      BOID_CONFIG.bounds.depth * 2
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
    setFlock(flock); // Store flock instance in state

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

  // Add effect to update speed
  useEffect(() => {
    if (flock) {
      flock.setMaxSpeed(speed);
    }
  }, [speed, flock]);

  return (
    <div id="visualization-container">
      <div className="absolute top-4 right-4 py-[var(--navbar-height)]">
        <Accordion type="single" collapsible className="min-w-[200px]">
          <AccordionItem value="controls">
            <AccordionTrigger>How to fly</AccordionTrigger>
            <AccordionContent>
              <ControlsTooltip />
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="boids">
            <AccordionTrigger>What are boids?</AccordionTrigger>
            <AccordionContent>
              <BoidsTooltip />
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="speed">
            <AccordionTrigger>Speed Control</AccordionTrigger>
            <AccordionContent>
              <div className="px-2">
                <Slider
                  value={[speed]}
                  onValueChange={([newSpeed]) => setSpeed(newSpeed)}
                  min={0.05}
                  max={0.4}
                  step={0.01}
                  className="my-4"
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
