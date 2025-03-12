import "./Landing.css";

import ProductCard from "../components/ProductCard";
import React from "react";
import { toast } from "@/hooks/use-toast";
import { useEffect } from "react";
import { useTheme } from "@/components/theme-provider";

const Landing: React.FC = () => {
  const { theme } = useTheme();
  useEffect(() => {
    const authError = localStorage.getItem("authError");
    if (authError) {
      toast({
        title: "Session expired",
        description: authError,
      });
      localStorage.removeItem("authError");
    }
  }, []);

  const products = [
    {
      title: "Games",
      description: "Collection of interactive games and simulations",
      icon: theme === "dark" ? "icons/games-dark.png" : "icons/games-light.png",
      link: "/games",
      featured: true,
    },
    {
      title: "AutoDraft",
      description: "Generate AI-powered drafts for your projects",
      icon:
        theme === "dark"
          ? "icons/drafting-compass-dark.png"
          : "icons/drafting-compass-light.png",
      link: "/autodraft",
    },
    {
      title: "Cheffrey",
      description:
        "Your AI sous-chef helps you discover, share, and create delicious recipes",
      icon:
        theme === "dark"
          ? "icons/chef_hat_stamp.png"
          : "icons/chef_hat_stamp_light.png",
      link: "https://apps.apple.com/us/app/cheffrey/id6503424946",
    },
    // {
    //   title: "Poeltl-Chat",
    //   description: "Play a game of NBA themed 20-questions against an AI",
    //   icon: theme === "dark" ? "icons/team-dark.png" : "icons/team-light.png",
    //   link: "/poeltl",
    // },
    {
      title: "Reminder-Mate",
      description: "Get reminders for your tasks and events",
      icon:
        theme === "dark"
          ? "icons/reminder-dark.png"
          : "icons/reminder-light.png",
      link: "https://reminder-mate.vercel.app/",
    },
  ];

  return (
    <div className="p-1">
      <div className="flex flex-column flex-start z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-20">
            <h1 className="text-4xl sm:text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-br from-primary to-secondary pb-1">
              Let AI lighten your load
            </h1>
            <p className="text-xl sm:text-2xl text-muted-foreground">
              We help you leverage Artificial Intelligence to streamline your
              work and improve your productivity
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-column mb-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
          {products.map((product, index) => (
            <ProductCard key={index} {...product} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Landing;
