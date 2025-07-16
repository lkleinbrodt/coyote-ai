import React from 'react';

const services = [
  {
    title: 'AI Integrations',
    description: 'Chatbots, ML models, API tools',
  },
  {
    title: 'Process Automation',
    description: 'Eliminate repetitive tasks',
  },
  {
    title: 'Custom AI Tools',
    description: 'Tailor-made solutions for business workflows',
  },
  {
    title: 'AI Strategy',
    description: 'Help businesses figure out where AI fits',
  },
];

const Services: React.FC = () => {
  return (
    <section id="services" className="bg-white py-16">
      <div className="container mx-auto text-center">
        <h2 className="mb-12 text-3xl font-bold">What I Can Help You With</h2>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {services.map((service) => (
            <div
              key={service.title}
              className="rounded-lg border p-6 shadow-sm"
            >
              <h3 className="mb-2 text-xl font-semibold">{service.title}</h3>
              <p className="text-gray-600">{service.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
