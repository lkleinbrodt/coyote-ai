import React from 'react';
import { Cookie } from 'lucide-react';

interface FoodProps {
  position: { x: number; y: number };
  isEaten: boolean;
}

export const Food: React.FC<FoodProps> = ({ position, isEaten }) => {
  return (
    <div 
      className={`absolute transition-all duration-500 ${
        isEaten ? 'opacity-0 scale-0' : 'opacity-100 scale-100'
      }`}
      style={{ 
        left: position.x, 
        top: position.y,
      }}
    >
      <Cookie size={24} className="text-yellow-600" />
    </div>
  );
}