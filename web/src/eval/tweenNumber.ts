import { useEffect, useRef, useState } from 'react';

const TWEEN_DURATION_MS = 180;

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Tweens a numeric display value when it changes *after* initial mount.
 * - Initial mount or null/undefined -> number transition: returns `target` immediately (no tween).
 * - `prefers-reduced-motion: reduce`: returns `target` immediately.
 * - Subsequent numeric changes while mounted: smoothly interpolates over 180ms ease-out.
 */
export function useTweenedNumber(target: number | null | undefined): number | null | undefined {
  const [display, setDisplay] = useState<number | null | undefined>(target);
  const prevTargetRef = useRef<number | null | undefined>(target);
  const currentValRef = useRef<number | null | undefined>(target);

  useEffect(() => {
    const prevTarget = prevTargetRef.current;
    prevTargetRef.current = target;

    if (
      target === null ||
      target === undefined ||
      typeof target !== 'number' ||
      !Number.isFinite(target)
    ) {
      currentValRef.current = target;
      setDisplay(target);
      return;
    }

    // No tween on initial mount (prevTarget === target) or null-to-value transition
    if (
      prevTarget === null ||
      prevTarget === undefined ||
      typeof prevTarget !== 'number' ||
      !Number.isFinite(prevTarget) ||
      prevTarget === target ||
      prefersReducedMotion()
    ) {
      currentValRef.current = target;
      setDisplay(target);
      return;
    }

    const from =
      typeof currentValRef.current === 'number' && Number.isFinite(currentValRef.current)
        ? currentValRef.current
        : prevTarget;

    if (from === target) {
      setDisplay(target);
      return;
    }

    let rafId = 0;
    const startTime = performance.now();

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / TWEEN_DURATION_MS);
      const next = from + (target - from) * easeOutCubic(progress);
      currentValRef.current = next;
      setDisplay(next);
      if (progress < 1) {
        rafId = window.requestAnimationFrame(tick);
      } else {
        currentValRef.current = target;
        setDisplay(target);
      }
    };

    rafId = window.requestAnimationFrame(tick);
    return () => {
      if (rafId) {
        window.cancelAnimationFrame(rafId);
      }
    };
  }, [target]);

  return display;
}
