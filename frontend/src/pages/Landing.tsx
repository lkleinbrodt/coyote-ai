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
      title: "Boids",
      description: "Visualize boids in 3D",
      icon: theme === "dark" ? "icons/boids-dark.png" : "icons/boids-light.png",
      link: "/boids",
    },
    {
      title: "Cheffrey",
      description: "Your AI sous-chef helps you discover, share, and create",
      icon:
        theme === "dark"
          ? "icons/chef_hat_stamp.png"
          : "icons/chef_hat_stamp_light.png",
      link: "https://apps.apple.com/us/app/cheffrey/id6503424946",
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
      title: "Poeltl-Chat",
      description: "Play a game of NBA themed 20-questions against an AI",
      icon: theme === "dark" ? "icons/team-dark.png" : "icons/team-light.png",
      link: "/poeltl",
    },

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
    <div className="landing-page">
      <div className="hero-section">
        {/* <img
          src="icons/coyote_logo.png"
          className="logo"
          alt="Coyote AI logo"
        />

        {user && (
          <div className="flex flex-col justify-center items-center">
            <span className="user-message text-center">{user.name}</span>
          </div>
        )}

        <div className="welcome-container">
          <h1>Welcome</h1>
          <div className="welcome-blurb">Check out our projects below!</div>
        </div> */}
      </div>
      <div className="product-section">
        <h1>Projects</h1>
        <div className="product-grid">
          {products.map((product, index) => (
            <ProductCard key={index} {...product} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Landing;
