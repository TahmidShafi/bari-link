import React from 'react';

export const Banner: React.FC = () => {
  return (
    <aside className="synthetic-banner" role="alert" aria-label="Synthetic Data Notice">
      <strong>NOTICE:</strong> All data are synthetic. No real person is represented.
    </aside>
  );
};

