import About from "@/components/consulting/About";
import Contact from "@/components/consulting/Contact";
import Footer from "@/components/consulting/Footer";
// import Header from "@/components/consulting/Header";
import Hero from "@/components/consulting/Hero";
import Projects from "@/components/consulting/Projects";
import React from "react";
import Services from "@/components/consulting/Services";
import Testimonials from "@/components/consulting/Testimonials";

const Consulting: React.FC = () => {
  return (
    <div className="flex min-h-screen flex-col bg-white text-gray-900">
      <main className="flex-1">
        <Hero />
        <About />
        <Services />
        <Projects />
        <Testimonials />
        <Contact />
      </main>
      <Footer />
    </div>
  );
};

export default Consulting;
