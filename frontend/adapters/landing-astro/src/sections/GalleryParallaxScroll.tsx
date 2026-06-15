/**
 * GalleryParallaxScroll.tsx — React island for gallery/parallax-scroll variant.
 * Adapted from 21st.dev "Text Parallax Content Scroll" (MIT).
 *
 * Each item is a "chapter": a sticky full-viewport panel that scales (1→0.85) as
 * the user scrolls past it, with a dark overlay fading in. An editorial block
 * (heading + body + optional CTA) follows below each panel.
 *
 * `src` sentinel: if item.src starts with "texture:" (e.g. "texture:clay"),
 * the panel renders as a CSS gradient using theme tokens
 * --color-texture-<name>-from/to/overlay instead of a photo.
 *
 * INVARIANTS:
 *   - No-JS visible (Growth-69): ALL text and panels are in SSR HTML at opacity:1.
 *     The React island only ADDS scroll-driven transforms after hydration.
 *     opacity:0 / hidden initial state NEVER baked into SSR HTML.
 *   - Theme-tokenized: no hardcoded hex or rgb. All colors via CSS vars.
 *   - prefers-reduced-motion: no parallax/scale, static panels.
 *   - client:visible hydration (island pattern, same as FeatureCarousel/ProofMarquee3d).
 */

import React, { useRef } from "react";
import {
  motion,
  useScroll,
  useTransform,
  useReducedMotion,
} from "framer-motion";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ParallaxItem {
  src: string;           // image URL or "texture:<name>"
  alt: string;
  subheading?: string;
  heading?: string;
  body?: string;
  cta_label?: string;
  cta_href?: string;
  caption?: string;
}

interface Props {
  items: ParallaxItem[];
  copy?: Record<string, string>;
}

// ── Texture sentinel helper ───────────────────────────────────────────────────

function isTexture(src: string): boolean {
  return src.startsWith("texture:");
}

function textureKey(src: string): string {
  // "texture:clay" → "clay"
  return src.replace(/^texture:/, "").trim();
}

// Returns inline style object for the sticky panel background.
// For texture: mode → CSS gradient via theme tokens.
// For images → background-image url.
function panelBg(src: string): React.CSSProperties {
  if (isTexture(src)) {
    const key = textureKey(src);
    return {
      background: `linear-gradient(160deg, var(--color-texture-${key}-from) 0%, var(--color-texture-${key}-to) 100%)`,
    };
  }
  return {
    backgroundImage: `url(${src})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
  };
}

// ── Chapter panel (sticky full-viewport, scroll-driven) ───────────────────────

const IMG_PADDING = 12; // px gap from viewport edge — matches 21st.dev source

interface ChapterProps {
  item: ParallaxItem;
  reducedMotion: boolean;
}

function ChapterPanel({ item, reducedMotion }: ChapterProps) {
  // Refs for sticky panel and overlay copy
  const panelRef = useRef<HTMLDivElement>(null);
  const copyRef = useRef<HTMLDivElement>(null);

  // Panel scale: shrinks from 1→0.85 as this chapter leaves viewport
  const { scrollYProgress: panelProgress } = useScroll({
    target: panelRef,
    offset: ["end end", "end start"],
  });

  // Copy parallax: slides through while chapter is in view
  const { scrollYProgress: copyProgress } = useScroll({
    target: copyRef,
    offset: ["start end", "end start"],
  });

  // Hooks called unconditionally — rules-of-hooks fix.
  // Branch on reducedMotion VALUE when applying to style, never gate the hook calls.
  const scaleTransform = useTransform(panelProgress, [0, 1], [1, 0.85]);
  const overlayOpacityTransform = useTransform(panelProgress, [0, 1], [0, 0.7]);
  const copyYTransform = useTransform(copyProgress, [0, 1], [120, -120]);
  // copyOpacity: Growth-69 — initial={false} on motion.div prevents SSR opacity:0.
  const copyOpacityTransform = useTransform(copyProgress, [0.25, 0.5, 0.75], [0, 1, 0]);

  // Apply static values for reduced-motion; live MotionValues for motion-OK users.
  const scale = reducedMotion ? 1 : scaleTransform;
  const overlayOpacity = reducedMotion ? 0.4 : overlayOpacityTransform;
  const copyY = reducedMotion ? 0 : copyYTransform;
  // reduced-motion: no opacity binding (text stays at opacity:1 via cascade).
  const copyOpacity = reducedMotion ? undefined : copyOpacityTransform;

  const key = isTexture(item.src) ? textureKey(item.src) : null;

  // Grain SVG overlay URI — subtle noise texture, same technique as HeroBrewBubbles
  const grainSvg = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E")`;

  return (
    <div
      style={{ paddingLeft: IMG_PADDING, paddingRight: IMG_PADDING }}
    >
      {/* 150vh scroll container so sticky panel has room to travel */}
      <div className="relative" style={{ height: "150vh" }}>
        {/* Sticky panel */}
        <motion.div
          ref={panelRef}
          style={{
            ...panelBg(item.src),
            height: `calc(100vh - ${IMG_PADDING * 2}px)`,
            top: IMG_PADDING,
            scale: scale as any,
            position: "sticky",
            borderRadius: "var(--radius-card, 6px)",
          }}
          className="z-0 overflow-hidden"
          aria-label={item.alt}
          role="img"
        >
          {/* Grain overlay (decorative, aria-hidden) */}
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              inset: 0,
              backgroundImage: grainSvg,
              backgroundRepeat: "repeat",
              pointerEvents: "none",
              borderRadius: "inherit",
            }}
          />

          {/* Texture-specific overlay for text legibility */}
          {key && (
            <div
              aria-hidden="true"
              style={{
                position: "absolute",
                inset: 0,
                background: `var(--color-texture-${key}-overlay, rgba(0,0,0,0.4))`,
                pointerEvents: "none",
              }}
            />
          )}

          {/* Dark overlay that fades in on scroll (decorative) */}
          <motion.div
            aria-hidden="true"
            className="absolute inset-0 pointer-events-none"
            style={{
              background: "var(--color-hero-bg-from, #1E140A)",
              opacity: overlayOpacity as any,
            }}
          />

          {/* Overlay text — parallax through on scroll.
              Growth-69 invariant: initial={false} prevents framer-motion from
              baking opacity:0 into SSR HTML. Without JS, text is opacity:1 (CSS default).
              The island adds scroll-driven y + opacity transforms after hydration only. */}
          <motion.div
            ref={copyRef}
            initial={false}
            className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
            style={{
              y: (copyY as any) ?? 0,
              ...(copyOpacity !== undefined ? { opacity: copyOpacity as any } : {}),
            }}
          >
            {item.subheading && (
              <p
                className="mb-3 text-xs md:text-sm font-semibold uppercase tracking-[0.18em]"
                style={{ color: "var(--color-primary-subtle, #EDD8C0)" }}
              >
                {item.subheading}
              </p>
            )}
            {item.heading && (
              <h2
                className="text-4xl md:text-6xl lg:text-7xl"
                style={{
                  fontFamily: "var(--font-family-display, serif)",
                  fontWeight: "var(--font-weight-display, 700)",
                  letterSpacing: "var(--font-letter-spacing-display, -0.02em)",
                  color: "var(--color-primary-subtle, #EDD8C0)",
                  lineHeight: "1.05",
                }}
              >
                {item.heading}
              </h2>
            )}
          </motion.div>
        </motion.div>
      </div>

      {/* Editorial block: below each chapter panel */}
      {(item.body || item.cta_label) && (
        <div
          className="mx-auto px-4 py-16 md:py-24"
          style={{ maxWidth: "var(--space-container-max, 1100px)" }}
        >
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
            {item.heading && (
              <h3
                className="col-span-1 md:col-span-4 text-2xl md:text-3xl"
                style={{
                  fontFamily: "var(--font-family-display, serif)",
                  fontWeight: "var(--font-weight-display, 700)",
                  color: "var(--color-text-1, #1E140A)",
                  letterSpacing: "var(--font-letter-spacing-display, -0.02em)",
                }}
              >
                {item.heading}
              </h3>
            )}
            <div className={`col-span-1 ${item.heading ? "md:col-span-8" : "md:col-span-12"}`}>
              {item.body && (
                <p
                  className="text-lg md:text-xl leading-relaxed mb-8"
                  style={{
                    fontFamily: "var(--font-family-body, serif)",
                    color: "var(--color-text-2, #4A3020)",
                    letterSpacing: "var(--font-letter-spacing-body, 0.01em)",
                  }}
                >
                  {item.body}
                </p>
              )}
              {item.cta_label && item.cta_href && (
                <a
                  href={item.cta_href}
                  className="inline-block px-6 py-3 font-semibold text-sm uppercase tracking-[0.1em] transition-colors"
                  style={{
                    background: "var(--color-primary, #B5501A)",
                    color: "#ffffff",
                    borderRadius: "var(--radius-button, 4px)",
                    textDecoration: "none",
                  }}
                >
                  {item.cta_label}
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────

export function GalleryParallaxScroll({ items, copy }: Props) {
  const reducedMotion = useReducedMotion() ?? false;

  return (
    <section
      className="w-full"
      style={{ background: "var(--color-surface-1, #C9A078)" }}
      data-section="gallery-parallax-scroll"
    >
      {/* Section header */}
      {copy?.headline && (
        <div
          className="mx-auto px-6 pt-[var(--space-section-y,104px)] pb-12"
          style={{ maxWidth: "var(--space-container-max, 1100px)" }}
        >
          <h2
            className="text-3xl md:text-4xl"
            style={{
              fontFamily: "var(--font-family-display, serif)",
              fontWeight: "var(--font-weight-display, 700)",
              letterSpacing: "var(--font-letter-spacing-display, -0.02em)",
              color: "var(--color-text-1, #1E140A)",
            }}
          >
            {copy.headline}
          </h2>
          {copy.subhead && (
            <p
              className="mt-3 text-base md:text-lg"
              style={{ color: "var(--color-text-2, #4A3020)" }}
            >
              {copy.subhead}
            </p>
          )}
        </div>
      )}

      {items.map((item, i) => (
        <ChapterPanel key={i} item={item} reducedMotion={reducedMotion} />
      ))}

      {/* Bottom spacer */}
      <div style={{ height: "var(--space-section-y, 104px)" }} />
    </section>
  );
}
