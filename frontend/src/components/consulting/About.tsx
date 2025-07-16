import React from 'react';

const About: React.FC = () => {
  return (
    <section id="about" className="py-16">
      <div className="container mx-auto text-center">
        <h2 className="mb-6 text-3xl font-bold">About Me</h2>
        <p className="mx-auto mb-6 max-w-2xl text-gray-700">
          I’m Lando — a data scientist turned full-stack AI consultant. I help
          clients integrate intelligent systems that save time and unlock
          business potential.
        </p>
        <ul className="mx-auto mb-6 max-w-md list-disc text-left text-gray-600">
          <li>5+ years of experience</li>
          <li>Python, JavaScript/TypeScript, React</li>
          <li>Served clients in e-commerce, SaaS, and healthcare</li>
        </ul>
      </div>
    </section>
  );
};

export default About;
