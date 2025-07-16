import React from 'react';

type Project = {
  name: string;
  description: string;
};

const projects: Project[] = [
  {
    name: 'Sales Chatbot',
    description:
      'Conversational bot that qualifies leads and integrates with CRM (React, Node.js, OpenAI).',
  },
  {
    name: 'Analytics Pipeline',
    description:
      'Automated data pipeline providing daily business insights (Python, AWS).',
  },
  {
    name: 'Custom Internal Tools',
    description: 'Suite of productivity apps tailored for client workflows.',
  },
];

const Projects: React.FC = () => {
  return (
    <section id="projects" className="bg-gray-50 py-16">
      <div className="container mx-auto text-center">
        <h2 className="mb-12 text-3xl font-bold">What I've Built</h2>
        <div className="grid gap-8 md:grid-cols-3">
          {projects.map((project) => (
            <div key={project.name} className="rounded-lg border p-6 shadow-sm">
              <h3 className="mb-2 text-xl font-semibold">{project.name}</h3>
              <p className="text-gray-600">{project.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Projects;
