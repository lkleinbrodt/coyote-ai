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
    scene.fog = new THREE.FogExp2(0x87ceeb, 0.0015);

    // Create skybox
    const skyboxGeometry = new THREE.BoxGeometry(1000, 1000, 1000);
    const skyboxMaterials = Array(6)
      .fill(null)
      .map(
        () =>
          new THREE.MeshBasicMaterial({
            color: 0x87ceeb, // Light blue color
            side: THREE.BackSide,
          })
      );
    const skybox = new THREE.Mesh(skyboxGeometry, skyboxMaterials);
    scene.add(skybox);

    // Create terrain
    const terrainGeometry = new THREE.PlaneGeometry(
      BOID_CONFIG.bounds.width * 4,
      BOID_CONFIG.bounds.depth * 4,
      100,
      100
    );

    // Add height variation to terrain
    const vertices = terrainGeometry.attributes.position.array;
    for (let i = 0; i < vertices.length; i += 3) {
      const amplitude = 2;
      vertices[i + 1] =
        amplitude *
        (Math.random() - 0.5) *
        Math.sin(vertices[i] / 10) *
        Math.cos(vertices[i + 2] / 10);
    }
    terrainGeometry.attributes.position.needsUpdate = true;
    terrainGeometry.computeVertexNormals();

    // Create ground material with a simple color and roughness
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x2d5a27, // Dark green color
      roughness: 0.8,
      metalness: 0.2,
    });

    const ground = new THREE.Mesh(terrainGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -20; // Adjusted height to be more visible
    ground.receiveShadow = true;
    scene.add(ground);

    // Enhanced lighting setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // Increased ambient light intensity
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.5); // Increased sun light intensity
    sunLight.position.set(50, 100, 50);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 500;
    sunLight.shadow.camera.left = -100;
    sunLight.shadow.camera.right = 100;
    sunLight.shadow.camera.top = 100;
    sunLight.shadow.camera.bottom = -100;
    scene.add(sunLight);

    // Add some environmental elements (trees/rocks)
    const addEnvironmentalElement = (x: number, z: number, scale: number) => {
      const geometry = new THREE.ConeGeometry(1, 4, 8);
      const material = new THREE.MeshStandardMaterial({ color: 0x2d5a27 });
      const element = new THREE.Mesh(geometry, material);
      element.position.set(x, -BOID_CONFIG.bounds.height + 2, z);
      element.scale.set(scale, scale, scale);
      element.castShadow = true;
      element.receiveShadow = true;
      scene.add(element);
    };

    // Add random trees/rocks around the terrain
    for (let i = 0; i < 20; i++) {
      const x = (Math.random() - 0.5) * BOID_CONFIG.bounds.width * 3;
      const z = (Math.random() - 0.5) * BOID_CONFIG.bounds.depth * 3;
      const scale = 1 + Math.random() * 2;
      addEnvironmentalElement(x, z, scale);
    }

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    document.body.appendChild(renderer.domElement);

    // Create walls (make them more transparent and add slight color)
    const wallGeometry = new THREE.BoxGeometry(
      BOID_CONFIG.bounds.width * 2,
      BOID_CONFIG.bounds.height * 2,
      BOID_CONFIG.bounds.depth * 2
    );
    const wallMaterial = new THREE.MeshBasicMaterial({
      color: 0xadd8e6,
      transparent: true,
      opacity: 0.03,
      side: THREE.BackSide,
      wireframe: true,
    });
    const walls = new THREE.Mesh(wallGeometry, wallMaterial);
    scene.add(walls);

    // Create flock
    const flock = new Flock(BOID_CONFIG, scene);
    setFlock(flock);

    // Handle space bar for reset
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === " ") {
        flock.reset();
        cameraController.reset();
      }
    };

    const cameraController = new CameraController(CAMERA_CONFIG);
    window.addEventListener("keydown", handleKeyDown);

    function animate() {
      cameraController.update();
      flock.update();
      renderer.render(scene, cameraController.getCamera());
    }

    renderer.setAnimationLoop(animate);

    // Handle window resize
    const handleResize = () => {
      const camera = cameraController.getCamera();
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
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
