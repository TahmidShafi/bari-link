import React from 'react';

export type PipelineMode = 'constraint' | 'no_constraint' | 'raw';

interface ModeSwitchProps {
  currentMode: PipelineMode;
  onChange: (mode: PipelineMode) => void;
}

export const ModeSwitch: React.FC<ModeSwitchProps> = ({ currentMode, onChange }) => {
  const modes: Array<{ id: PipelineMode; label: string; tooltip: string }> = [
    {
      id: 'constraint',
      label: 'Resolved (kinship constraint ON)',
      tooltip: 'Champion pipeline: Splink Fellegi-Sunter + min-cut listed_as_other_member constraints + bridge pruning',
    },
    {
      id: 'no_constraint',
      label: 'Resolved (constraint OFF)',
      tooltip: 'Counterfactual: Same predictions & bridge pruning, but without listed_as_other_member cannot-link cuts',
    },
    {
      id: 'raw',
      label: 'Raw Splink edges (live union-find)',
      tooltip: 'Baseline: Direct connected components over pairs with weight >= t_link (in-browser union-find worker)',
    },
  ];

  return (
    <div className="mode-switch-group">
      <label id="mode-switch-label">Linkage Pipeline Mode</label>
      <div
        className="mode-buttons"
        role="radiogroup"
        aria-labelledby="mode-switch-label"
      >
        {modes.map((m) => {
          const isSelected = currentMode === m.id;
          return (
            <button
              key={m.id}
              type="button"
              role="radio"
              aria-checked={isSelected}
              className={`mode-btn ${isSelected ? 'active' : ''}`}
              title={m.tooltip}
              onClick={() => onChange(m.id)}
            >
              {m.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};

