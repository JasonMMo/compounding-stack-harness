/**
 * ProofMarquee3d.tsx — React island for the "marquee-3d" logos/proof variant.
 * Adapted from 21st.dev "3D Marquee" by Shatlyk1011 (MIT).
 *
 * Changes from source:
 *   - External supabase defaultImages removed; caller must supply images[].
 *   - Optional heading + subhead text props added (natural for a proof section).
 *   - No-JS / SSR rule (Growth-69): framer-motion columns use NO initial opacity:0.
 *     The `initial` prop is only a transform (y offset); opacity stays at 1 in SSR
 *     output. When JS hydrates, framer-motion's `animate` continues from initial y.
 *   - prefers-reduced-motion: animation duration multiplied 10x and amplitude
 *     reduced to 0 so the grid stays visually static.
 *   - Colors tokenised: overlay gradient reads --color-hero-bg-from/to (or neutral
 *     fallback) so it inherits the active theme without hardcoding.
 *   - cn() helper = twMerge(clsx(...)) — same pattern as source.
 */

import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: unknown[]): string {
  return twMerge(clsx(inputs))
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ProofMarquee3dProps {
  /** Required: image paths (absolute URL or root-relative like /proof/shop-demo.jpg). */
  images: string[]
  /** Optional section heading. */
  heading?: string
  /** Optional short subhead below the heading. */
  subhead?: string
  className?: string
}

// ── Component ─────────────────────────────────────────────────────────────────

export function ProofMarquee3d({
  images,
  heading,
  subhead,
  className,
}: ProofMarquee3dProps) {
  // Split images into 3 columns (same algorithm as source).
  const chunkSize = Math.ceil(images.length / 3)
  const chunks = Array.from({ length: 3 }, (_: unknown, colIndex: number) => {
    const start = colIndex * chunkSize
    return images.slice(start, start + chunkSize)
  })

  // Detect reduced-motion at render time (SSR-safe: typeof window guard).
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches

  // Animation amplitudes: full motion vs. reduced-motion (nearly static).
  const amplitude = prefersReducedMotion ? 2 : 60
  const duration0 = prefersReducedMotion ? 100 : 10
  const duration1 = prefersReducedMotion ? 150 : 15

  return (
    <section
      className={cn(
        'relative w-full overflow-hidden py-12 md:py-16',
        className
      )}
      style={{
        background:
          'linear-gradient(to bottom, var(--color-hero-bg-from, #1E1B4B), var(--color-hero-bg-to, #0F0A2B))',
      }}
      aria-label="Proof wall — generated systems"
    >
      {/* Optional text header */}
      {(heading || subhead) && (
        <div className="relative z-10 mx-auto mb-8 max-w-3xl px-6 text-center">
          {heading && (
            <h2
              className="text-2xl font-[var(--font-weight-display,700)] tracking-tight text-white md:text-3xl"
              style={{ fontFamily: 'var(--font-family-display, inherit)' }}
            >
              {heading}
            </h2>
          )}
          {subhead && (
            <p className="mt-2 text-sm text-white/60 md:text-base">{subhead}</p>
          )}
        </div>
      )}

      {/* 3D marquee grid */}
      {/*
        CRITICAL (Growth-69 no-JS rule):
        - The wrapper div has NO opacity:0.
        - motion.figure's `initial` carries only a y-transform (opacity=1 always).
        - SSR renders columns fully visible; JS hydration continues the translate animation.
      */}
      <div
        className="mx-auto block h-[480px] w-full overflow-hidden rounded-md md:h-[560px]"
        aria-hidden="false"
      >
        <div className="flex size-full items-center justify-center">
          <div className="aspect-square w-[720px] shrink-0 scale-[1.35] md:w-[900px] md:scale-[1.1]">
            <div
              style={{ transform: 'rotateX(45deg) rotateY(0deg) rotateZ(45deg)' }}
              className="relative top-0 right-[-55%] grid size-full origin-top-left grid-cols-3 gap-5 md:right-[-45%]"
            >
              {chunks.map((colImages: string[], colIndex: number) => (
                <motion.figure
                  key={colIndex + '-marquee'}
                  /*
                   * initial: y offset only — opacity is NOT set here (stays 1 for SSR).
                   * animate: target y in opposite direction for the gentle oscillation.
                   * The component is rendered server-side with the initial y value applied
                   * via CSS transform; images remain fully visible before JS loads.
                   */
                  initial={{ y: colIndex % 2 === 0 ? 0 : 0 }}
                  animate={{ y: colIndex % 2 === 0 ? amplitude : -amplitude }}
                  transition={{
                    duration: colIndex % 2 === 0 ? duration0 : duration1,
                    repeat: Infinity,
                    repeatType: 'reverse',
                    ease: 'easeInOut',
                  }}
                  className="flex flex-col items-start gap-4 md:gap-6"
                >
                  {colImages.map((src: string, imageIndex: number) => {
                    // Derive a readable alt from the filename (strip path + extension).
                    const alt = src
                      .split('/')
                      .pop()
                      ?.replace(/\.[^.]+$/, '')
                      ?.replace(/[-_]/g, ' ') ?? `System ${imageIndex + 1}`

                    return (
                      <div className="relative" key={imageIndex + src}>
                        <img
                          src={src}
                          alt={alt}
                          draggable={false}
                          /*
                           * No opacity style here — images are fully visible in SSR.
                           * Tailwind classes use bg-neutral for the loading placeholder.
                           */
                          className={cn(
                            'aspect-[4/3] h-full w-full rounded-lg object-cover select-none',
                            'bg-neutral-800',
                          )}
                          loading="lazy"
                          decoding="async"
                        />
                      </div>
                    )
                  })}
                </motion.figure>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
