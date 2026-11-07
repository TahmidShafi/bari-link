import React from 'react';

interface ThresholdSliderProps {
  value: number;
  onChange: (val: number) => void;
  min?: number;
  max?: number;
  step?: number;
}

export const ThresholdSlider: React.FC<ThresholdSliderProps> = ({
  value,
  onChange,
  min = 2.0,
  max = 14.0,
  step = 0.5,
}) => {
  const isSelectedDevOperatingPoint = Math.abs(value - 2.0) < 0.001;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    let nextVal = value;
    if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      nextVal = Math.min(max, value + step);
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      nextVal = Math.max(min, value - step);
    } else if (e.key === 'Home') {
      nextVal = min;
    } else if (e.key === 'End') {
      nextVal = max;
    }
    if (nextVal !== value) {
      e.preventDefault();
      onChange(Math.round(nextVal * 10) / 10);
    }
  };

  return (
    <div className="slider-group">
      <div className="slider-header">
        <label htmlFor="tlink-slider">
          Linkage Threshold (<em>t</em><sub>link</sub>)
          {isSelectedDevOperatingPoint && (
            <span
              className="chip chip-accent"
              style={{ marginLeft: '0.5rem', verticalAlign: 'middle' }}
            >
              ★ selected on dev data (frozen)
            </span>
          )}
        </label>
        <span className="slider-readout num">
          w ≥ {value.toFixed(1)}
        </span>
      </div>

      <input
        id="tlink-slider"
        type="range"
        className="slider-input"
        min={min}
        max={max}
        step={step}
        value={value}
        aria-label="Linkage decision threshold t_link"
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        aria-valuetext={`Threshold weight ${value.toFixed(1)}`}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        onKeyDown={handleKeyDown}
      />
    </div>
  );
};

