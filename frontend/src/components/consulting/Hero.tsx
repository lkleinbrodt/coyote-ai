import React from "react";

const Hero: React.FC = () => {
  return (
    <section
      id="hero"
      className="flex min-h-[80vh] flex-col items-center justify-center bg-gray-50 text-center"
    >
      <h1 className="mb-4 text-4xl font-extrabold md:text-6xl">
        Let AI Lighten Your Load.
      </h1>
      <p className="mb-8 max-w-xl text-lg text-gray-600">
        I help small to mid-sized businesses integrate AI to automate, optimize,
        and scale.
      </p>
      <img
        src="/icons/coyote_logo.png"
        alt="AI Illustration"
        className="mb-8 h-32 w-32"
      />
      <a
        href="#contact"
        className="rounded-md bg-indigo-600 px-6 py-3 font-medium text-white hover:bg-indigo-700"
      >
        Book a Free Consult
      </a>
    </section>
  );
};

export default Hero;
