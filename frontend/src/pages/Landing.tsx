import "./Landing.css";

import ProductCard from "../components/ProductCard";
import React from "react";
import { motion } from "framer-motion";
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
      // category: "games",
    },
    {
      title: "AutoDraft",
      description: "Generate AI-powered drafts for your projects",
      icon:
        theme === "dark"
          ? "icons/drafting-compass-dark.png"
          : "icons/drafting-compass-light.png",
      link: "/autodraft",
      // category: "aiTools",
    },
    {
      title: "Cheffrey",
      description:
        "Discover recipes, plan meals, and share cookbooks with friends!",
      icon:
        theme === "dark"
          ? "icons/chef_hat_stamp.png"
          : "icons/chef_hat_stamp_light.png",
      link: "https://cheffrey.org",
      // category: "mobileApps",
    },
    {
      title: "Reminder-Mate",
      description: "Get reminders for your tasks and events",
      icon:
        theme === "dark"
          ? "icons/reminder-dark.png"
          : "icons/reminder-light.png",
      link: "https://reminder-mate.vercel.app/",
      // category: "mobileApps",
    },
  ];

  return (
    <div className="p-1">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-column flex-start z-10"
      >
        <div className="max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center py-20">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-4xl sm:text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-br from-primary to-primary pb-1 text-left"
            >
              Hi, I'm Landon
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-xl sm:text-2xl text-muted-foreground text-left"
            >
              I like to build software. Here's some stuff I've built.
            </motion.p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex flex-column mb-2"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4">
          {products.map((product, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 * index }}
            >
              <ProductCard {...product} />
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Landing;
