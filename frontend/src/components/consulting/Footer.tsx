import React from 'react';

const Footer: React.FC = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="bg-gray-800 py-6 text-center text-white">
      <div className="container mx-auto space-y-2">
        <p>Lando AI Consulting</p>
        <div className="flex justify-center gap-4">
          <a href="https://github.com" className="hover:text-indigo-400">
            GitHub
          </a>
          <a href="https://linkedin.com" className="hover:text-indigo-400">
            LinkedIn
          </a>
          <a href="mailto:hello@example.com" className="hover:text-indigo-400">
            Email
          </a>
        </div>
        <p className="text-sm">© {year}</p>
      </div>
    </footer>
  );
};

export default Footer;
