const boidRules = [
  {
    rule: "Separation",
    description: "Avoid crowding nearby flockmates",
  },
  {
    rule: "Alignment",
    description: "Steer towards average heading of flockmates",
  },
  {
    rule: "Cohesion",
    description: "Move toward the center of nearby flockmates",
  },
] as const;

export function BoidsTooltip() {
  return (
    <div className="text-white font-sans">
      <div className="flex flex-col gap-3">
        <p className="text-sm">
          Boids are artificial life that simulate flocking behavior of birds.
          Each boid follows three simple rules:
        </p>
        {boidRules.map((rule, i) => (
          <div key={i} className="flex items-start gap-4">
            <div className="bg-white/20 border border-white/40 rounded px-2.5 py-1.5 text-sm min-w-[100px]">
              {rule.rule}
            </div>
            <span className="text-sm">{rule.description}</span>
          </div>
        ))}
        <p className="text-sm text-white/80">
          Together, these simple rules create complex, natural-looking flocking
          patterns!
        </p>
      </div>
    </div>
  );
}
