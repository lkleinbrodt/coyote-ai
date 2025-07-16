import React from 'react';

const testimonials = [
  {
    name: 'Jane Doe',
    quote: 'Lando transformed our operations with his AI expertise.',
  },
  {
    name: 'John Smith',
    quote: 'Outstanding solutions that saved us countless hours.',
  },
];

const Testimonials: React.FC = () => {
  return (
    <section id="testimonials" className="bg-white py-16">
      <div className="container mx-auto text-center">
        <h2 className="mb-12 text-3xl font-bold">What People Are Saying</h2>
        <div className="grid gap-8 md:grid-cols-2">
          {testimonials.map((t) => (
            <div key={t.name} className="rounded-lg border p-6 shadow-sm">
              <p className="mb-4 italic text-gray-600">"{t.quote}"</p>
              <p className="font-semibold">- {t.name}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
