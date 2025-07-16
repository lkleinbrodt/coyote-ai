import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 bg-white shadow">
      <nav className="container mx-auto flex items-center justify-between py-4">
        <a href="#hero" className="text-xl font-bold">Lando AI Consulting</a>
        <ul className="hidden gap-6 sm:flex">
          <li><a href="#about" className="hover:text-indigo-600">About</a></li>
          <li><a href="#services" className="hover:text-indigo-600">Services</a></li>
          <li><a href="#projects" className="hover:text-indigo-600">Projects</a></li>
          <li><a href="#contact" className="hover:text-indigo-600">Contact</a></li>
        </ul>
        <a
          href="#contact"
          className="hidden rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 sm:inline-block"
        >
          Let's Talk
        </a>
      </nav>
    </header>
  );
};

export default Header;
