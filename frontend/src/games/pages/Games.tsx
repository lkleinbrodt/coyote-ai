import "./Games.css";

import { Card } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { useTheme } from "@/components/theme-provider";

interface GameCard {
  title: string;
  description: string;
  path: string;
  icon: string;
  featured?: boolean;
}

export default function Games() {
  const { theme } = useTheme();

  const games: GameCard[] = [
    {
      title: "Gravity Quest",
      description: "Use your tractor beam to collect stars and avoid bombs.",
      path: "/games/gravity-quest",
      icon:
        theme === "dark"
          ? "/icons/gravity-quest.png"
          : "/icons/gravity-quest.png",
      featured: true,
    },
    {
      title: "Shoot The Creeps",
      description:
        "Defend your base from waves of creeps in this action-packed game.",
      path: "/games/shoot-the-creeps",
      icon: "/icons/ShootTheCreeps.png",
    },
    {
      title: "Boids Simulation",
      description: "Watch and interact with an AI-powered flocking simulation",
      path: "/boids",
      icon:
        theme === "dark" ? "/icons/boids-dark.png" : "/icons/boids-light.png",
    },
    {
      title: "Poeltl Chat",
      description: "Play NBA-themed 20 questions against an AI",
      path: "/poeltl",
      icon: theme === "dark" ? "/icons/team-dark.png" : "/icons/team-light.png",
    },
  ];

  return (
    <div className="p-1">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center py-20">
          <h1 className="text-4xl sm:text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-br from-primary to-secondary pb-1">
            Interactive Games
          </h1>
          <p className="text-xl sm:text-2xl text-muted-foreground">
            Explore our collection of AI-powered games and simulations
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
        {games.map((game) => (
          <Link key={game.path} to={game.path} className="block no-underline">
            <Card className="group relative overflow-hidden border-2 hover:border-primary/50 transition-all">
              {game.featured && (
                <div className="absolute top-2 right-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full">
                  Featured
                </div>
              )}
              <div className="p-6">
                <div className="flex items-center justify-center mb-4">
                  <img
                    src={game.icon}
                    alt={game.title}
                    className="w-16 h-16 object-contain transition-transform group-hover:scale-110"
                  />
                </div>
                <h3 className="text-lg font-semibold text-center mb-2">
                  {game.title}
                </h3>
                <p className="text-sm text-muted-foreground text-center">
                  {game.description}
                </p>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
