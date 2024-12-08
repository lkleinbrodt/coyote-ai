import "./Landing.css";

import ProductCard from "../components/ProductCard";
import React from "react";
import { useAuth } from "@/contexts/AuthContext";

const Landing: React.FC = () => {
  const { user } = useAuth();
  const products = [
    {
      title: "Reminder-Mate",
      description: "Get reminders for your tasks and events",
      icon: "icons/reminder-mate.png",
      link: "https://reminder-mate.vercel.app/",
    },
    {
      title: "Cheffrey",
      description: "Your AI sous-chef helps you discover, share, and create",
      icon: "icons/chef_hat_stamp.png",
      link: "https://apps.apple.com/us/app/cheffrey/id6503424946",
    },
    {
      title: "GuitarPic",
      description: "Selling your guitar just got a lot easier",
      icon: "icons/guitarpic.png",
      link: "",
    },
  ];

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center py-5">
      <div className="container">
        <div className="text-center mb-5">
          <img
            src="icons/coyote_logo.png"
            className="img-fluid mb-3 mx-auto"
            alt="Coyote AI logo"
            style={{ maxWidth: "200px" }}
          />
          <h1 className="brand-title display-4">Coyote AI</h1>
          <p className="tagline lead mb-0">Let AI lighten your load</p>
          {user && <p className="tagline lead mb-0">Hello {user.name}!</p>}
        </div>
        <div className="text-center mb-5">
          <a href="/chat" className="btn btn-primary btn-lg">
            Start Chatting
          </a>
        </div>

        <div className="row justify-content-center align-items-stretch g-4">
          {products.map((product, index) => (
            <div key={index} className="col-md-4 col-sm-12">
              <ProductCard {...product} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Landing;
