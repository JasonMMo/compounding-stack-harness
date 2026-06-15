/**
 * HeroGlowyWaves.tsx — React island for the "glowy-waves" hero variant.
 * Adapted from 21st.dev "Glowy Waves Hero" by moumensoliman (MIT).
 *
 * Changes from source:
 *   - shadcn Button removed; replaced with plain <a> using our design tokens.
 *   - Hardcoded copy replaced with props: headline, subhead, cta, pills, stats.
 *   - prefers-reduced-motion: framer-motion entrance skipped (content immediately
 *     visible) — mirrors BaseLayout motion guard. Canvas still runs but with
 *     reduced influence (matching source behaviour for canvas itself).
 *   - Colors read from CSS custom properties emitted by build-tokens.mjs:
 *       --color-primary, --color-hero-bg-from, --color-hero-bg-to, etc.
 */

import { motion, type Variants } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { useEffect, useRef } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface WaveConfig {
  offset: number;
  amplitude: number;
  frequency: number;
  color: string;
  opacity: number;
}

export interface HeroGlowyWavesProps {
  headline: string;
  subhead: string;
  cta: { label: string; href: string };
  pills?: string[];
  stats?: { label: string; value: string }[];
}

// ── Framer-motion variant defs ────────────────────────────────────────────────

// Approach (A): opacity is always 1 in both hidden and visible variants.
// This ensures SSR/no-JS render never carries opacity:0 — content is always
// visible. JS users see a slide/scale-in entrance. Zero hydration-mismatch risk.
const containerVariants: Variants = {
  hidden: { opacity: 1, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, staggerChildren: 0.12 },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 1, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

const statsVariants: Variants = {
  hidden: { opacity: 1, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.6, ease: "easeOut", staggerChildren: 0.08 },
  },
};

// ── Component ─────────────────────────────────────────────────────────────────

export function HeroGlowyWaves({ headline, subhead, cta, pills, stats }: HeroGlowyWavesProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const targetMouseRef = useRef({ x: 0, y: 0 });

  // Check reduced-motion once at mount (used for both canvas and framer variants).
  const prefersReducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId: number;
    let time = 0;

    // Resolve a CSS variable through a temporary DOM element so canvas can use
    // the same token values as the rest of the page.
    const resolveColor = (variables: string[], alpha = 1): string => {
      const rootStyles = getComputedStyle(document.documentElement);
      const tempEl = document.createElement("div");
      tempEl.style.cssText = "position:absolute;visibility:hidden;width:1px;height:1px;";
      document.body.appendChild(tempEl);
      let color = `rgba(255,255,255,${alpha})`;

      for (const variable of variables) {
        const value = rootStyles.getPropertyValue(variable).trim();
        if (value) {
          tempEl.style.backgroundColor = `var(${variable})`;
          const computed = getComputedStyle(tempEl).backgroundColor;
          if (computed && computed !== "rgba(0, 0, 0, 0)") {
            if (alpha < 1) {
              const m = computed.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
              color = m ? `rgba(${m[1]},${m[2]},${m[3]},${alpha})` : computed;
            } else {
              color = computed;
            }
            break;
          }
        }
      }
      document.body.removeChild(tempEl);
      return color;
    };

    const computeThemeColors = () => ({
      // hero-bg-from / hero-bg-to are aurora-specific landing tokens; fall back
      // to --color-hero-bg-from (emitted by build-tokens as --color-hero-bg-from).
      backgroundTop: resolveColor(["--color-hero-bg-from", "--background"], 1),
      backgroundBottom: resolveColor(["--color-hero-bg-to", "--color-hero-bg-from", "--background"], 0.95),
      wavePalette: [
        {
          offset: 0,
          amplitude: 70,
          frequency: 0.003,
          color: resolveColor(["--color-primary"], 0.8),
          opacity: 0.45,
        },
        {
          offset: Math.PI / 2,
          amplitude: 90,
          frequency: 0.0026,
          color: resolveColor(["--color-accent-glow", "--color-primary"], 0.7),
          opacity: 0.35,
        },
        {
          offset: Math.PI,
          amplitude: 60,
          frequency: 0.0034,
          color: resolveColor(["--color-primary-hover", "--color-primary"], 0.65),
          opacity: 0.3,
        },
        {
          offset: Math.PI * 1.5,
          amplitude: 80,
          frequency: 0.0022,
          color: resolveColor(["--color-primary-active", "--color-primary"], 0.25),
          opacity: 0.25,
        },
        {
          offset: Math.PI * 2,
          amplitude: 55,
          frequency: 0.004,
          color: resolveColor(["--color-primary-border", "--color-primary"], 0.2),
          opacity: 0.2,
        },
      ] satisfies WaveConfig[],
    });

    let themeColors = computeThemeColors();

    const observer = new MutationObserver(() => {
      themeColors = computeThemeColors();
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme"],
    });

    // Reduced-motion adjustments for canvas (still runs, just less dramatic).
    const rm = prefersReducedMotion;
    const mouseInfluence = rm ? 10 : 70;
    const influenceRadius = rm ? 160 : 320;
    const smoothing = rm ? 0.04 : 0.1;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    const recenterMouse = () => {
      const p = { x: canvas.width / 2, y: canvas.height / 2 };
      mouseRef.current = p;
      targetMouseRef.current = { ...p };
    };
    const handleResize = () => { resizeCanvas(); recenterMouse(); };
    const handleMouseMove = (e: MouseEvent) => {
      targetMouseRef.current = { x: e.clientX, y: e.clientY };
    };
    const handleMouseLeave = () => recenterMouse();

    resizeCanvas();
    recenterMouse();

    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);

    const drawWave = (wave: WaveConfig) => {
      ctx.save();
      ctx.beginPath();
      for (let x = 0; x <= canvas.width; x += 4) {
        const dx = x - mouseRef.current.x;
        const dy = canvas.height / 2 - mouseRef.current.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const influence = Math.max(0, 1 - dist / influenceRadius);
        const mouseEffect =
          influence * mouseInfluence * Math.sin(time * 0.001 + x * 0.01 + wave.offset);
        const y =
          canvas.height / 2 +
          Math.sin(x * wave.frequency + time * 0.002 + wave.offset) * wave.amplitude +
          Math.sin(x * wave.frequency * 0.4 + time * 0.003) * (wave.amplitude * 0.45) +
          mouseEffect;
        x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = wave.color;
      ctx.globalAlpha = wave.opacity;
      ctx.shadowBlur = 35;
      ctx.shadowColor = wave.color;
      ctx.stroke();
      ctx.restore();
    };

    const animate = () => {
      time += 1;
      mouseRef.current.x += (targetMouseRef.current.x - mouseRef.current.x) * smoothing;
      mouseRef.current.y += (targetMouseRef.current.y - mouseRef.current.y) * smoothing;

      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, themeColors.backgroundTop);
      gradient.addColorStop(1, themeColors.backgroundBottom);
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;
      themeColors.wavePalette.forEach(drawWave);
      animationId = window.requestAnimationFrame(animate);
    };

    animationId = window.requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
      cancelAnimationFrame(animationId);
      observer.disconnect();
    };
  }, []);

  // CTA button — plain <a> with token-based styling (no shadcn dependency).
  const ctaBase =
    "inline-flex items-center gap-2 rounded-[var(--radius-badge,9999px)] px-8 py-3 text-base font-semibold uppercase tracking-[0.2em] transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2";
  const ctaPrimary =
    `${ctaBase} bg-[var(--color-primary,#6D28D9)] text-white hover:bg-[var(--color-primary-hover,#5B21B6)] focus-visible:outline-[var(--color-primary,#6D28D9)]`;
  const ctaOutline =
    `${ctaBase} border border-white/30 bg-white/10 text-white backdrop-blur hover:bg-white/20`;

  // When reduced-motion is active, skip framer-motion hiding and animate
  // immediately (content always visible — no "hidden until intersection" trap).
  const motionInitial = prefersReducedMotion ? "visible" : "hidden";

  return (
    <section
      className="relative isolate flex min-h-screen w-full items-center justify-center overflow-hidden"
      style={{ background: "var(--color-hero-bg-from, #1E1B4B)" }}
      role="region"
      aria-label="Hero section"
    >
      {/* Animated canvas background */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 h-full w-full"
        aria-hidden="true"
      />

      {/* Radial glow overlays — decorative */}
      <div className="absolute inset-0 -z-10 pointer-events-none" aria-hidden="true">
        <div className="absolute left-1/2 top-0 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[var(--color-accent-glow,rgba(139,92,246,0.35))] blur-[140px]" />
        <div className="absolute bottom-0 right-0 h-[360px] w-[360px] rounded-full bg-[var(--color-accent-glow,rgba(139,92,246,0.35))] blur-[120px] opacity-60" />
      </div>

      {/* Content */}
      <div className="relative z-10 mx-auto flex w-full max-w-6xl flex-col items-center px-6 py-24 text-center md:px-8 lg:px-12">
        <motion.div
          variants={containerVariants}
          initial={motionInitial}
          animate="visible"
          className="w-full"
        >
          {/* Badge pill */}
          <motion.div
            variants={itemVariants}
            className="mb-6 inline-flex items-center gap-2 rounded-[var(--radius-badge,9999px)] border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white/80 backdrop-blur"
          >
            <Sparkles className="h-4 w-4 text-[var(--color-primary,#6D28D9)]" aria-hidden="true" />
            AI-powered code generation
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={itemVariants}
            className="mb-6 text-4xl font-[var(--font-weight-display,800)] tracking-[var(--font-letter-spacing-display,-0.03em)] text-white md:text-6xl lg:text-7xl"
            style={{ fontFamily: "var(--font-family-display, inherit)" }}
          >
            {headline.includes(".") ? (
              <>
                {headline.split(".")[0]}.{" "}
                <span
                  style={{ color: "var(--color-primary-border,#C4B5FD)", fontWeight: "inherit" }}
                >
                  {headline.split(".").slice(1).join(".").trim()}
                </span>
              </>
            ) : (
              headline
            )}
          </motion.h1>

          {/* Subhead */}
          <motion.p
            variants={itemVariants}
            className="mx-auto mb-10 max-w-3xl text-lg text-white/70 md:text-2xl"
          >
            {subhead}
          </motion.p>

          {/* CTA group */}
          <motion.div
            variants={itemVariants}
            className="mb-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <a href={cta.href} className={ctaPrimary}>
              {cta.label}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" aria-hidden="true" />
            </a>
            <a href="#contact" className={ctaOutline}>
              Learn more
            </a>
          </motion.div>

          {/* Pills (optional) */}
          {pills && pills.length > 0 && (
            <motion.ul
              variants={itemVariants}
              className="mb-12 flex flex-wrap items-center justify-center gap-3 text-xs uppercase tracking-[0.2em] text-white/70"
            >
              {pills.map((pill) => (
                <li
                  key={pill}
                  className="rounded-[var(--radius-badge,9999px)] border border-white/20 bg-white/10 px-4 py-2 backdrop-blur"
                >
                  {pill}
                </li>
              ))}
            </motion.ul>
          )}

          {/* Stats grid (optional) */}
          {stats && stats.length > 0 && (
            <motion.div
              variants={statsVariants}
              className="grid gap-4 rounded-[var(--radius-card,16px)] border border-white/20 bg-white/10 p-6 backdrop-blur-sm sm:grid-cols-3"
            >
              {stats.map((stat) => (
                <motion.div key={stat.label} variants={itemVariants} className="space-y-1">
                  <div className="text-xs uppercase tracking-[0.3em] text-white/50">
                    {stat.label}
                  </div>
                  <div className="text-3xl font-semibold text-white">
                    {stat.value}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </motion.div>
      </div>
    </section>
  );
}
