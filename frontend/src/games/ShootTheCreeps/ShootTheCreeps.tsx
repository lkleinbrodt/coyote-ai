import React from "react";

const ShootTheCreeps: React.FC = () => {
  return (
    <div
      className="fixed inset-0"
      style={{
        top: "var(--navbar-height)",
        height: "calc(100vh - var(--navbar-height))",
      }}
    >
      <iframe
        src="/ShootTheCreepsWeb/Shoot the Creeps.html"
        className="w-full h-full"
        title="Shoot The Creeps"
        allow="fullscreen"
      />
    </div>
  );
};

export default ShootTheCreeps;
