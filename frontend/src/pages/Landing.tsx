import "./Landing.css";

import ProductCard from "../components/ProductCard";
import React from "react";
import { useAuth } from "@/contexts/AuthContext";

const Landing: React.FC = () => {
  const { user } = useAuth();
  const products = [
    {
      title: "Poeltl-Chat",
      description: "Play a game of NBA themed 20-questions against an AI",
      icon: "icons/AI Basketball.png",
      link: "/poeltl",
    },
    {
      title: "Cheffrey",
      description: "Your AI sous-chef helps you discover, share, and create",
      icon: "icons/chef_hat_stamp.png",
      link: "https://apps.apple.com/us/app/cheffrey/id6503424946",
    },
    {
      title: "Reminder-Mate",
      description: "Get reminders for your tasks and events",
      icon: "icons/reminder-mate.png",
      link: "https://reminder-mate.vercel.app/",
    },
  ];

  return (
    <div>
      <div className="hero-section">
        <img
          src="icons/coyote_logo.png"
          className="logo"
          alt="Coyote AI logo"
        />
        <h1 className="title">Welcome to Coyote AI</h1>
        {user ? (
          <div className="flex flex-col justify-center items-center">
            <span className="welcome-message">{user.name}</span>
          </div>
        ) : (
          <button className="login-button">Login</button>
        )}

        <div className="product-section">
          {products.map((product, index) => (
            <ProductCard key={index} {...product} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Landing;
