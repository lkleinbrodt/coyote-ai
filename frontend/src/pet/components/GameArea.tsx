import React, { useCallback, useEffect, useState } from "react";

import { Food } from "./Food";
import { Pet } from "./Pet";

interface FoodItem {
  id: number;
  position: { x: number; y: number };
  isEaten: boolean;
}

export const GameArea: React.FC = () => {
  const [petPosition, setPetPosition] = useState({
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  });
  const [targetPosition, setTargetPosition] = useState<{
    x: number;
    y: number;
  } | null>(null);
  const [foods, setFoods] = useState<FoodItem[]>([]);
  const [nextFoodId, setNextFoodId] = useState(0);
  const [currentTargetId, setCurrentTargetId] = useState<number | null>(null);

  const findNextFood = useCallback(() => {
    // Find the next uneaten food after the current target
    let foundCurrent = currentTargetId === null;
    const nextFood = foods.find((food) => {
      if (!foundCurrent) {
        if (food.id === currentTargetId) {
          foundCurrent = true;
        }
        return false;
      }
      return !food.isEaten;
    });

    if (nextFood) {
      setCurrentTargetId(nextFood.id);
      setTargetPosition(nextFood.position);
      return true;
    } else {
      setCurrentTargetId(null);
      setTargetPosition(null);
      return false;
    }
  }, [foods, currentTargetId]);

  const handleClick = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - 12;
    const y = e.clientY - rect.top - 12;

    const newFood: FoodItem = {
      id: nextFoodId,
      position: { x, y },
      isEaten: false,
    };

    setFoods((prev) => [...prev, newFood]);
    setNextFoodId((prev) => prev + 1);

    // If no current target, start with this food
    if (currentTargetId === null) {
      setCurrentTargetId(newFood.id);
      setTargetPosition(newFood.position);
    }
  };

  useEffect(() => {
    if (!targetPosition || currentTargetId === null) return;

    const movePet = () => {
      setPetPosition((current) => {
        const dx = targetPosition.x - current.x;
        const dy = targetPosition.y - current.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Calculate speed based on distance for smoother movement
        const baseSpeed = 5;
        const speed = Math.min(baseSpeed, distance / 2);

        if (distance < 20) {
          // Mark only the current target food as eaten
          setFoods((prev) =>
            prev.map((food) =>
              food.id === currentTargetId ? { ...food, isEaten: true } : food
            )
          );

          // Find next food after a short delay
          setTimeout(() => {
            findNextFood();
          }, 500); // Add a small delay before moving to next food

          return current;
        }

        const ratio = speed / distance;

        return {
          x: current.x + dx * ratio,
          y: current.y + dy * ratio,
        };
      });
    };

    const interval = setInterval(movePet, 16);
    return () => clearInterval(interval);
  }, [targetPosition, currentTargetId, findNextFood]);

  // Clean up eaten food after animation
  useEffect(() => {
    const cleanup = setTimeout(() => {
      setFoods((prev) => prev.filter((food) => !food.isEaten));
    }, 1000);
    return () => clearTimeout(cleanup);
  }, [foods]);

  return (
    <div
      className="relative w-full h-screen bg-gradient-to-b from-blue-100 to-blue-200 cursor-pointer"
      onClick={handleClick}
    >
      <Pet position={petPosition} targetPosition={targetPosition} />
      {foods.map((food) => (
        <Food key={food.id} position={food.position} isEaten={food.isEaten} />
      ))}

      {/* Instructions */}
      <div className="absolute top-4 left-4 bg-white/80 p-4 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Pet Simulator</h2>
        <p className="text-gray-600">
          Click anywhere to place food! Your pet will eat them in order.
        </p>
      </div>
    </div>
  );
};
