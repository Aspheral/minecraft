# Solar Shader

Solar Shader is a Minecraft shader project focused on **extremely cinematic visuals, high temporal stability, and unusually strong real-time performance**.

The project is being designed so visual quality scales intelligently with the machine and the player's intended frame-rate target instead of forcing every system into the same preset.

## Performance Target

The mainstream design baseline is **at least 120 FPS during normal gameplay at 1080p under defined benchmark conditions**, using a contemporary mainstream gaming-PC class as the reference rather than an enthusiast-only machine.

At 120 FPS, the nominal total frame interval is 8.33 ms. Solar does not assume the shader owns that entire interval because Minecraft, CPU work, other mods, drivers, and frame-pacing reserve all consume time too.

Lower intentional frame-rate targets unlock larger visual budgets. For example, a player intentionally targeting 60 FPS has a 16.67 ms total frame interval, so AutoTune should eventually be able to spend more time on higher-quality clouds, shadows, reflections, indirect lighting, atmosphere, and related effects than the same machine targeting 120 FPS.

This is a project target, not a benchmark result. Foundation v0 does not yet have I1 evidence establishing a particular FPS.

## AutoTune

Solar is planned around a hybrid adaptive-quality architecture:

1. **Shader-native adaptation** may use runtime information available to the shader, such as frame timing, screen dimensions, and render distance, to fine-tune scalable work.
2. **Static profiles and controls** will provide predictable quality envelopes such as Auto, Performance, Balanced, Cinematic, and Ultra once enough scalable systems exist for those labels to be meaningful.
3. **Optional Solar AutoTune companion** may later provide richer hardware/configuration awareness, including intended FPS cap and presentation behavior where supported.

The shaderpack must remain useful without the companion.

Foundation v0 implements only a stable renderer-facing quality interface with deterministic static values. It does **not** implement runtime adaptive quality.

## Current Status

Solar has completed the **Shader Foundation v0 source and static-validation milestone** on `feat/solar-foundation`.

Implemented foundation pieces include:

- a GLSL 330 compatibility baseline,
- a lean hybrid-deferred frame skeleton,
- `R11F_G11F_B10F` linear-light scene color in `colortex0`,
- compact `RGB10_A2` SurfaceData in `colortex1`,
- depth-based view-position reconstruction without a position render target,
- explicit opaque/cutout versus forward-translucent ownership,
- 21 thin Iris program pairs backed by shared GLSL modules,
- developer debug views,
- `TARGET_FPS` configuration plumbing,
- the static Solar quality-consumer ABI,
- Python reference math,
- complete S0 structural validation,
- pinned generic S1 GLSL compilation/linking in GitHub Actions.

The authoritative Foundation specification is:

- [Solar Shader Foundation Architecture](docs/superpowers/specs/2026-09-29-solar-foundation-design.md)

The approved Foundation implementation plan is:

- [Solar Shader Foundation Implementation Plan](docs/superpowers/plans/2026-09-29-solar-foundation.md)

The parent workspace specification remains:

- [Solar Shader Workspace and Performance Architecture](docs/superpowers/specs/2026-09-29-solar-workspace-design.md)

## Compatibility Reference

Dated 2026-09-29:

- Primary reference: Minecraft Java 26.3 + Fabric + Iris 1.11.6 + Sodium 0.9.2.
- Secondary lane: Minecraft Java 1.21.11 + Fabric + Iris 1.10.x.

These are engineering references and must be rechecked when version-sensitive work changes.

## Validation

Solar uses explicit evidence levels:

- **S0:** repository/source architecture checks.
- **S1:** generic GLSL validation with pinned Khronos glslang.
- **I0:** real Iris/Minecraft shaderpack discovery, load, patch, and compile evidence.
- **I1:** rendered visual, stability, and measured performance evidence.

The current Foundation branch has S0/S1 evidence. **S0/S1 do not prove Iris runtime compatibility**, visual correctness, driver behavior, or any FPS result.

I0 and I1 remain pending until genuine Minecraft + Iris runtime evidence is recorded.

Use [the Foundation runtime evidence template](benchmarks/foundation-runtime-template.md) when that evidence becomes available.

## Web Infrastructure

The connected Vercel `minecraft` project remains optional future infrastructure for documentation, benchmark viewers, release utilities, or related approved web tooling.

It is not the shader runtime, has not been used to validate Foundation rendering, and is not deployed as part of this milestone.
