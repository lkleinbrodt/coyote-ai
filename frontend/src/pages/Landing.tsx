import "./Landing.css";

import { Calendar } from "lucide-react";
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
      softwareType: "web",
    },
    {
      title: "AutoDraft",
      description: "Generate AI-powered drafts for your projects",
      icon:
        theme === "dark"
          ? "icons/drafting-compass-dark.png"
          : "icons/drafting-compass-light.png",
      link: "/autodraft",
      softwareType: "web",
    },
    {
      title: "Cheffrey",
      description:
        "Discover recipes, plan meals, and share cookbooks with friends!",
      icon:
        theme === "dark"
          ? "icons/chef_hat_stamp.png"
          : "icons/chef_hat_stamp_light.png",
      link: "https://www.cheffrey.org/",
      softwareType: "mobile",
    },

    {
      title: "Slate",
      description:
        "Everyone loves a to-do app. I made one that works best for me.",
      icon: theme === "dark" ? "icons/slate.png" : "icons/slate.png",
      link: "https://apps.apple.com/us/app/slateplanner/id6752905295",
      softwareType: "mobile",
    },
    {
      title: "Touchstone Calendar",
      description: "View gym classes and events from Touchstone climbing gyms",
      icon: Calendar,
      link: "/touchstone",
      softwareType: "web",
    },
    {
      title: "CopyCat Bundler",
      description:
        "VSCode extension that bundles your entire codebase into a single context window.",
      icon: "icons/copycat.png",
      link: "https://marketplace.visualstudio.com/items?itemName=LandonKleinbrodt.copycatBundler",
      softwareType: "ide",
    },
    {
      title: "Explain Like I'm ___",
      description: "Explore a topic at different levels of complexity",
      icon: theme === "dark" ? "icons/ELI.png" : "icons/ELI.png",
      link: "/explain",
      softwareType: "web",
    },
    {
      title: "Reminder-Mate",
      description: "Get reminders for your tasks and events",
      icon:
        theme === "dark"
          ? "icons/reminder-dark.png"
          : "icons/reminder-light.png",
      link: "https://reminder-mate.vercel.app/",
      softwareType: "web",
    },
    // {
    //   title: "Character Explorer",
    //   description: "Find characters who have similar speech patterns",
    //   icon: "",
    //   link: "/character-explorer",
    //   softwareType: "web",
    // },
  ];

  return (
    <div className="p-1">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col flex-start z-10"
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
              I like to build software. This site is a collection of the things
              I've built - games, AI tools, mobile apps, and whatever else I've
              been messing around with lately. Enjoy!
            </motion.p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex flex-col mb-2"
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
      <footer className="w-full text-center text-xs text-muted-foreground py-2 opacity-80">
        <a href="/privacy" className="underline hover:text-primary">
          Privacy Policy
        </a>
        {" | "}
        <a href="/terms" className="underline hover:text-primary">
          Terms of Service
        </a>
      </footer>
    </div>
  );
};

export default Landing;
