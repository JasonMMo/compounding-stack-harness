/**
 * FeatureCarousel.tsx — React island for the "carousel" features variant.
 * Adapted from 21st.dev "Feature Carousel" by 0xUrvish (MIT).
 *
 * Changes from source:
 *   - `motion/react` -> `framer-motion` (already installed).
 *   - @hugeicons/* removed; lucide-react used instead (icon string -> component lookup).
 *   - cn() defined locally via clsx + tailwind-merge (no @/lib/utils alias).
 *   - Hardcoded FEATURES array removed; data comes from props (items[]).
 *   - No-JS rule (Growth-69): first feature's label, description, and image are
 *     visible in SSR without JavaScript. The left-panel tab list uses a static
 *     fallback <div> block (always rendered); JS-driven AnimatePresence/motion
 *     tabs are progressive enhancement only. Right panel: first image rendered as
 *     a plain <img> in a <noscript>-safe static block; JS users see the animated
 *     stack. opacity:0 is NEVER baked into the SSR of the initial slide.
 *   - prefers-reduced-motion: auto-advance disabled; framer-motion spring
 *     transitions replaced with instant (duration:0) transitions.
 *   - Colors tokenised: background uses --color-primary, overlays use theme tokens.
 */

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import {
  Brain,
  Layers,
  Gauge,
  Shield,
  Globe,
  Zap,
  Star,
  Cloud,
  Smartphone,
  BarChart2,
  CheckCircle,
  Settings,
  type LucideProps,
} from "lucide-react";

type LucideIcon = React.ComponentType<LucideProps>;

// ── Helpers ───────────────────────────────────────────────────────────────────

function cn(...inputs: unknown[]): string {
  return twMerge(clsx(inputs));
}

// ── Icon lookup ───────────────────────────────────────────────────────────────
// Maps icon string (from manifest items[].icon) to a lucide component.
// Fallback: CheckCircle.

const ICON_MAP: Record<string, LucideIcon> = {
  brain: Brain,
  layers: Layers,
  gauge: Gauge,
  shield: Shield,
  globe: Globe,
  zap: Zap,
  star: Star,
  cloud: Cloud,
  smartphone: Smartphone,
  barchart: BarChart2,
  chart: BarChart2,
  check: CheckCircle,
  settings: Settings,
};

function resolveIcon(name?: string): LucideIcon {
  if (!name) return CheckCircle;
  return ICON_MAP[name.toLowerCase()] ?? CheckCircle;
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface FeatureCarouselItem {
  title: string;
  description: string;
  icon?: string;
  image?: string;
}

export interface FeatureCarouselProps {
  items: FeatureCarouselItem[];
  heading?: string;
  subhead?: string;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const AUTO_PLAY_INTERVAL = 3500;
const ITEM_HEIGHT = 65;

const wrap = (min: number, max: number, v: number): number => {
  const rangeSize = max - min;
  return ((((v - min) % rangeSize) + rangeSize) % rangeSize) + min;
};

// ── Component ─────────────────────────────────────────────────────────────────

export function FeatureCarousel({ items, heading, subhead }: FeatureCarouselProps) {
  // Clamp to at least 1 item to avoid divide-by-zero.
  const features = items.length > 0 ? items : [];

  const [step, setStep] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // Detect reduced-motion at mount; SSR-safe.
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  useEffect(() => {
    setPrefersReducedMotion(
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }, []);

  const count = features.length;
  const currentIndex = count > 0 ? ((step % count) + count) % count : 0;

  const nextStep = useCallback(() => {
    setStep((prev) => prev + 1);
  }, []);

  const handleChipClick = (index: number) => {
    if (count === 0) return;
    const diff = (index - currentIndex + count) % count;
    if (diff > 0) setStep((s) => s + diff);
  };

  // Auto-advance: disabled under reduced-motion or when paused.
  useEffect(() => {
    if (isPaused || prefersReducedMotion || count <= 1) return;
    const interval = setInterval(nextStep, AUTO_PLAY_INTERVAL);
    return () => clearInterval(interval);
  }, [nextStep, isPaused, prefersReducedMotion, count]);

  const getCardStatus = (index: number) => {
    const diff = index - currentIndex;
    const len = count;
    let nd = diff;
    if (diff > len / 2) nd -= len;
    if (diff < -len / 2) nd += len;
    if (nd === 0) return "active";
    if (nd === -1) return "prev";
    if (nd === 1) return "next";
    return "hidden";
  };

  // Transition config: instant under reduced-motion.
  const springLeft = prefersReducedMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 90, damping: 22, mass: 1 };

  const springRight = prefersReducedMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 260, damping: 25, mass: 0.8 };

  if (features.length === 0) return null;

  const firstItem = features[0];
  const firstIcon = resolveIcon(firstItem.icon);

  return (
    <section
      className="w-full py-16 md:py-24"
      aria-label={heading ?? "Features"}
    >
      {/* Optional section heading */}
      {(heading || subhead) && (
        <div className="mx-auto max-w-7xl px-6 mb-10 text-center">
          {heading && (
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary,#0f172a)] mb-3 tracking-tight">
              {heading}
            </h2>
          )}
          {subhead && (
            <p className="text-[var(--color-text-secondary,#475569)] text-lg max-w-2xl mx-auto">
              {subhead}
            </p>
          )}
        </div>
      )}

      <div className="w-full max-w-7xl mx-auto md:px-8">
        {/*
          No-JS fallback: render the first feature fully visible outside the
          animated container. Hidden from JS users via the `no-js-only` approach:
          we use a <noscript> block so it is invisible when JS runs, but visible
          and fully opacity:1 in SSR/no-JS environments.
        */}
        <noscript>
          <div className="rounded-2xl border border-[var(--color-border,#e2e8f0)] p-8 flex flex-col gap-4 bg-[var(--color-bg-surface,#fff)]">
            {React.createElement(firstIcon, {
              className: "w-8 h-8 text-[var(--color-primary,#6D28D9)]",
              "aria-hidden": "true",
            })}
            <div className="text-sm font-semibold uppercase tracking-widest text-[var(--color-primary,#6D28D9)]">
              {firstItem.title}
            </div>
            {firstItem.image && (
              <img
                src={firstItem.image}
                alt={firstItem.title}
                className="w-full max-w-md rounded-xl object-cover"
                style={{ opacity: 1 }}
              />
            )}
            <p className="text-[var(--color-text-secondary,#475569)]">
              {firstItem.description}
            </p>
          </div>
        </noscript>

        {/*
          JS-enabled carousel.
          No-JS rule: the first card's img must have opacity:1 in static SSR HTML.
          We achieve this by:
          1. Using `initial={false}` on all motion.div cards (framer-motion does NOT
             bake an initial opacity:0 into SSR HTML when initial=false).
          2. The `animate` prop sets opacity reactively AFTER hydration.
          3. Before hydration (SSR/no-JS), all cards receive no inline style from
             framer-motion, so the browser default opacity:1 applies to the first card.
          4. We additionally render a static visible-by-default first-item block
             in the left panel (see "SSR-visible first item" below).
        */}
        <div className="relative overflow-hidden rounded-[2.5rem] lg:rounded-[4rem] flex flex-col lg:flex-row min-h-[600px] lg:aspect-video border border-[var(--color-border,rgba(0,0,0,0.1))]">

          {/* ── Left: scrolling tab list ─────────────────────────────────── */}
          <div
            className="w-full lg:w-[40%] min-h-[350px] md:min-h-[450px] lg:h-full relative z-30 flex flex-col items-start justify-center overflow-hidden px-8 md:px-16 lg:pl-16"
            style={{ background: "var(--color-primary, #6D28D9)" }}
          >
            {/* Fade masks */}
            <div
              className="absolute inset-x-0 top-0 h-12 md:h-20 lg:h-16 z-40 pointer-events-none"
              style={{
                background:
                  "linear-gradient(to bottom, var(--color-primary,#6D28D9) 0%, transparent 100%)",
              }}
              aria-hidden="true"
            />
            <div
              className="absolute inset-x-0 bottom-0 h-12 md:h-20 lg:h-16 z-40 pointer-events-none"
              style={{
                background:
                  "linear-gradient(to top, var(--color-primary,#6D28D9) 0%, transparent 100%)",
              }}
              aria-hidden="true"
            />

            {/*
              SSR-visible first item (no-JS rule): a plain visible block that shows
              the first feature label + icon without any JS or framer-motion.
              Hidden for JS users via the `js-hidden` pattern: we toggle display
              with a CSS class applied on hydration via useEffect.
              Simpler approach used here: render it always, but place it BEHIND the
              motion layer (z-10 vs z-20) so JS users see the animated tabs on top.
              This guarantees no-JS users always see the first item.
            */}
            <div
              className="absolute z-10 flex items-center gap-4 px-6 md:px-10 lg:px-8 py-3.5 rounded-full bg-white"
              style={{ pointerEvents: "none" }}
              aria-hidden="true"
            >
              {React.createElement(resolveIcon(firstItem.icon), {
                size: 18,
                strokeWidth: 2,
                style: { color: "var(--color-primary, #6D28D9)" },
              })}
              <span
                className="font-normal text-sm md:text-[15px] tracking-tight whitespace-nowrap uppercase"
                style={{ color: "var(--color-primary, #6D28D9)" }}
              >
                {firstItem.title}
              </span>
            </div>

            {/* Animated tab strip (JS-only, sits above static fallback at z-20) */}
            <div className="relative w-full h-full flex items-center justify-center lg:justify-start z-20">
              {features.map((feature, index) => {
                const isActive = index === currentIndex;
                const distance = index - currentIndex;
                const wrappedDistance = wrap(
                  -(count / 2),
                  count / 2,
                  distance
                );
                const IconComp = resolveIcon(feature.icon);

                return (
                  <motion.div
                    key={index}
                    style={{ height: ITEM_HEIGHT, width: "fit-content" }}
                    initial={false}
                    animate={{
                      y: wrappedDistance * ITEM_HEIGHT,
                      opacity: 1 - Math.abs(wrappedDistance) * 0.25,
                    }}
                    transition={springLeft}
                    className="absolute flex items-center justify-start"
                  >
                    <button
                      onClick={() => handleChipClick(index)}
                      onMouseEnter={() => setIsPaused(true)}
                      onMouseLeave={() => setIsPaused(false)}
                      className={cn(
                        "relative flex items-center gap-4 px-6 md:px-10 lg:px-8 py-3.5 md:py-5 lg:py-4 rounded-full transition-all duration-700 text-left group border",
                        isActive
                          ? "bg-white border-white z-10"
                          : "bg-transparent text-white/60 border-white/20 hover:border-white/40 hover:text-white"
                      )}
                      style={
                        isActive
                          ? { color: "var(--color-primary, #6D28D9)" }
                          : undefined
                      }
                      aria-pressed={isActive}
                      aria-label={feature.title}
                    >
                      <span
                        className={cn(
                          "flex items-center justify-center transition-colors duration-500"
                        )}
                        style={
                          isActive
                            ? { color: "var(--color-primary, #6D28D9)" }
                            : { color: "rgba(255,255,255,0.4)" }
                        }
                      >
                        <IconComp size={18} strokeWidth={2} aria-hidden="true" />
                      </span>
                      <span className="font-normal text-sm md:text-[15px] tracking-tight whitespace-nowrap uppercase">
                        {feature.title}
                      </span>
                    </button>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* ── Right: image stack ──────────────────────────────────────── */}
          <div className="flex-1 min-h-[500px] md:min-h-[600px] lg:h-full relative flex items-center justify-center py-16 md:py-24 lg:py-16 px-6 md:px-12 lg:px-10 overflow-hidden border-t lg:border-t-0 lg:border-l border-[var(--color-border,rgba(0,0,0,0.1))] bg-[var(--color-bg-surface,#f8fafc)]">
            <div className="relative w-full max-w-[420px] aspect-[4/5] flex items-center justify-center">
              {features.map((feature, index) => {
                const status = getCardStatus(index);
                const isActive = status === "active";
                const isPrev = status === "prev";
                const isNext = status === "next";

                // Determine image: use feature.image if present; fall back to a
                // solid-color placeholder so the card shape is still rendered.
                const hasImage = Boolean(feature.image);

                return (
                  <motion.div
                    key={index}
                    initial={false}
                    animate={{
                      x: isActive ? 0 : isPrev ? -100 : isNext ? 100 : 0,
                      scale: isActive ? 1 : isPrev || isNext ? 0.85 : 0.7,
                      opacity: isActive ? 1 : isPrev || isNext ? 0.4 : 0,
                      rotate: isPrev ? -3 : isNext ? 3 : 0,
                      zIndex: isActive ? 20 : isPrev || isNext ? 10 : 0,
                      pointerEvents: isActive ? "auto" : "none",
                    }}
                    transition={springRight}
                    className="absolute inset-0 rounded-[2rem] md:rounded-[2.8rem] overflow-hidden border-4 md:border-8 bg-[var(--color-bg-surface,#fff)]"
                    style={{ borderColor: "var(--color-bg-surface, #fff)" }}
                  >
                    {hasImage ? (
                      <img
                        src={feature.image}
                        alt={feature.title}
                        className={cn(
                          "w-full h-full object-cover transition-all duration-700",
                          isActive
                            ? "grayscale-0"
                            : "grayscale blur-[2px] brightness-75"
                        )}
                        /* No inline opacity here — framer-motion sets opacity on
                           the parent motion.div, not on the img. The img always
                           has its natural opacity:1 within the card. */
                      />
                    ) : (
                      /* No-image fallback: color panel + centered description */
                      <div
                        className="w-full h-full flex flex-col items-center justify-center p-8 gap-4"
                        style={{
                          background:
                            "linear-gradient(135deg, var(--color-primary,#6D28D9) 0%, var(--color-primary-hover,#5B21B6) 100%)",
                        }}
                      >
                        {React.createElement(resolveIcon(feature.icon), {
                          size: 48,
                          strokeWidth: 1.5,
                          color: "rgba(255,255,255,0.9)",
                          "aria-hidden": "true",
                        })}
                      </div>
                    )}

                    {/* Description overlay (AnimatePresence — JS only) */}
                    <AnimatePresence>
                      {isActive && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: 10 }}
                          transition={prefersReducedMotion ? { duration: 0 } : undefined}
                          className="absolute inset-x-0 bottom-0 p-10 pt-32 bg-gradient-to-t from-black/90 via-black/40 to-transparent flex flex-col justify-end pointer-events-none"
                        >
                          <div
                            className="px-4 py-1.5 rounded-full text-[11px] font-normal uppercase tracking-[0.2em] w-fit shadow-lg mb-3 border"
                            style={{
                              background: "var(--color-bg-surface,#fff)",
                              color: "var(--color-text-primary,#0f172a)",
                              borderColor: "var(--color-border,rgba(0,0,0,0.1))",
                            }}
                          >
                            {index + 1} &bull; {feature.title}
                          </div>
                          <p className="text-white font-normal text-xl md:text-2xl leading-tight drop-shadow-md tracking-tight">
                            {feature.description}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Active indicator dot */}
                    <div
                      className={cn(
                        "absolute top-8 left-8 flex items-center gap-3 transition-opacity duration-300",
                        isActive ? "opacity-100" : "opacity-0"
                      )}
                      aria-hidden="true"
                    >
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{
                          background: "var(--color-accent-warm, #AB5527)",
                          boxShadow: "0 0 8px var(--color-accent-warm, #AB5527)",
                        }}
                      />
                      <span className="text-white/80 text-[10px] font-normal uppercase tracking-[0.3em] font-mono">
                        Feature {index + 1}
                      </span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default FeatureCarousel;
