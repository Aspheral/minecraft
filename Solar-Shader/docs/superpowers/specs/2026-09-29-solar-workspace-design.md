# Solar Shader Workspace and Performance Architecture

**Date:** 2026-09-29  
**Repository:** `Aspheral/minecraft`  
**Project root:** `Solar-Shader/`  
**Branch:** `feat/solar-workspace`  
**Status:** Written specification awaiting user review  
**Revision:** 3 — adds refresh/frame-cap-aware AutoTune budgeting

## 1. Purpose

`Aspheral/minecraft` is a monorepo intended to hold multiple independent Minecraft-related projects over time. Solar Shader is the first project and must remain isolated under `Solar-Shader/`.

Solar Shader's product goal is to combine:

1. extremely cinematic real-time visuals,
2. unusually high performance,
3. automatic scaling across mainstream through enthusiast hardware,
4. a protected visual identity that does not collapse into an ugly low-quality mode merely to chase a frame-rate number.

GitHub is the canonical source of project truth. The repository must be usable as the persistent engineering workspace for development performed through normal ChatGPT conversations using GitHub, Superpowers, Context7, and other explicitly connected tools. The workflow must not assume that the user has a local IDE, local terminal, Minecraft runtime, Codex, or ChatGPT Work available during every development session.

## 2. Repository Model

Permanent project boundaries are directories, not branches.

- `main` is the stable integrated state of the Minecraft monorepo.
- `Solar-Shader/` permanently contains Solar Shader.
- Future Minecraft projects receive their own top-level directories.
- Feature branches are temporary development timelines and are merged back into `main`.
- Solar Shader work must not modify unrelated top-level projects unless explicitly requested.

Example future monorepo:

```text
minecraft/
├── README.md
├── Solar-Shader/
├── Another-Shader/
├── Mods/
├── Resource-Packs/
└── Tools/
```

## 3. Solar Shader Workspace Target

The workspace milestone establishes durable project boundaries, engineering documentation, benchmark conventions, and locations for future shader and AutoTune work without prematurely generating a large rendering pipeline.

Target structure:

```text
minecraft/
├── README.md
└── Solar-Shader/
    ├── README.md
    ├── CHANGELOG.md
    ├── benchmarks/
    │   └── README.md
    ├── companion/
    │   └── Solar-AutoTune/
    │       └── README.md
    ├── docs/
    │   ├── architecture/
    │   │   └── README.md
    │   └── superpowers/
    │       ├── specs/
    │       │   └── 2026-09-29-solar-workspace-design.md
    │       └── plans/
    │           └── README.md
    ├── shaders/
    │   └── lib/
    │       └── README.md
    └── tools/
        └── README.md
```

Git does not preserve empty directories, so implementation may use README files to establish intended boundaries.

No actual rendering pipeline or companion-mod implementation belongs in the workspace-only milestone.

## 4. Shaderpack Layout Assumptions

Current Iris documentation confirms that a shaderpack contains a top-level `shaders/` directory inside the pack root. Shared GLSL library files may be organized under `shaders/lib/`, and `shaders.properties` belongs inside `shaders/` when introduced.

Accordingly:

- `Solar-Shader/` is the eventual shaderpack root.
- Runtime shader files will live under `Solar-Shader/shaders/`.
- Shared GLSL modules will live under `Solar-Shader/shaders/lib/`.
- `shaders.properties` will eventually live at `Solar-Shader/shaders/shaders.properties`.
- Runtime files must be introduced by later rendering milestones rather than by workspace scaffolding simply to make the tree look full.

## 5. Product Visual Contract

Solar Shader should pursue a cinematic visual identity rather than simple photorealism or a checklist of expensive effects.

Long-term target systems include:

- physically convincing sunlight and moonlight,
- atmospheric scattering,
- volumetric clouds,
- volumetric fog,
- high-quality sunrise and sunset rendering,
- stylized but believable sky rendering,
- water reflection and refraction,
- underwater rendering,
- weather-aware lighting,
- soft and contact shadows,
- foliage transmission,
- emissive lighting,
- bloom,
- exposure adaptation,
- tone mapping,
- cinematic color grading,
- ambient occlusion,
- indirect-light approximations,
- cave and interior lighting,
- night lighting,
- temporal anti-aliasing/reconstruction,
- stable distant rendering,
- improved materials,
- water caustics where practical,
- biome-aware atmosphere.

The intended result must remain readable during actual gameplay. Effects that look impressive in still screenshots but produce severe ghosting, shimmer, instability, latency, or unreadable scenes are not considered successful.

## 6. Performance Contract

Performance is an architectural constraint, not a final optimization pass.

The primary real-time target is:

**At least 120 FPS during normal gameplay on a contemporary mainstream gaming-PC class at 1080p under the project's defined benchmark conditions.**

At 120 FPS, the corresponding nominal total frame budget is:

**8.33 ms per frame.**

120 FPS is the primary Solar design baseline, not a mandatory target for every user. In `AUTO`, Solar should respect a lower intentional gameplay cap where it can be determined. A player targeting 60 FPS has a nominal 16.67 ms total frame budget and should receive materially higher visual quality than the same machine targeting 120 FPS, provided the additional work remains stable.

The project must not claim universal 120 FPS on every machine, resolution, render distance, modpack, scene, driver, or Minecraft version. Benchmark claims must always include the test conditions.

### 6.1 Mainstream baseline

The baseline is a hardware class, not one permanently frozen GPU SKU.

The project's mainstream reference profile should be periodically refreshed from current gaming-PC hardware adoption data. At the time of this specification, the intended class is approximately:

- 1080p primary rendering,
- 12–16 chunk render distance for the main benchmark profile,
- contemporary mainstream discrete-GPU capability approximately in the RTX 3060 through RTX 4060 class,
- a typical modern gaming CPU rather than a high-end workstation requirement.

A second upper-mainstream benchmark profile should cover 1440p.

This prevents Solar from being optimized around either obsolete low-end hardware or an enthusiast-only machine.

### 6.2 Quality scaling principle

Solar should maximize visual quality subject to the performance budget.

Conceptually:

```text
maximize perceived image quality
subject to:
    target frame budget
    minimum cinematic quality floor
    temporal stability constraints
    compatibility constraints
```

A stronger machine should automatically receive more expensive rendering until either:

1. Solar reaches its maximum real-time quality ceiling, or
2. the selected performance target is approached.

A high-end GPU must not be artificially limited to mainstream-quality settings merely because those settings satisfy the baseline target.

## 7. AutoTune Architecture

Solar will use a hybrid adaptive-quality architecture.

### 7.1 Layer A — shader-native adaptation

Solar Shader itself must remain useful without any companion mod.

Current Iris documentation exposes runtime values including:

- `frameTime` — duration of the previous frame in seconds,
- `viewWidth` — screen width in pixels,
- `viewHeight` — screen height in pixels,
- `far` — current render distance in blocks.

The shader-native adaptive controller may use these values, plus Solar-owned temporal state where technically appropriate, to adjust scalable rendering work.

The controller must react to sustained performance trends rather than single-frame spikes.

Design requirements:

- use smoothed or windowed performance measurements,
- use hysteresis so quality does not oscillate rapidly,
- reduce expensive effects gradually when over budget,
- restore quality more conservatively than it removes it,
- avoid visible quality popping where feasible,
- protect minimum visual-quality floors,
- never treat one unusually slow frame as evidence that the system tier changed.

### 7.2 Layer B — static profiles and user controls

Iris `shaders.properties` supports:

- named profiles,
- option sliders,
- conditional program enablement,
- disabling individual programs through profiles,
- required and optional Iris feature declarations.

Solar should eventually expose at least:

- `AUTO` — recommended default,
- `PERFORMANCE`,
- `BALANCED`,
- `CINEMATIC`,
- `ULTRA`,
- an optional non-real-time or screenshot-oriented maximum-quality mode if later justified.

Static profiles establish coarse architectural choices. Runtime adaptation performs fine-grained work inside the selected envelope.

A runtime adaptation system must not depend on recompiling the shader every few frames.

### 7.3 Layer C — optional Solar AutoTune companion

`Solar-Shader/companion/Solar-AutoTune/` is reserved for an optional future companion that can perform richer startup calibration than a shaderpack alone can reliably perform.

Its intended responsibilities are:

- establish a better initial quality envelope,
- identify relevant hardware capabilities where supported,
- account for the actual display resolution,
- account for Minecraft/render-distance configuration,
- determine the user's configured frame-rate limit where supported,
- account for VSync and monitor refresh behavior where supported,
- distinguish an intentional frame cap from genuine rendering overload,
- optionally provide richer performance telemetry,
- choose sensible initial Solar settings,
- avoid forcing a high-end system to begin at a mainstream quality level.

The companion is an enhancement, not a hard dependency.

Solar Shader must still load and expose useful manual/static/adaptive behavior without it.

The exact companion-to-Iris integration mechanism is deliberately not assumed in this workspace specification. Before implementing the companion, a dedicated architectural cycle must verify the current Iris/Sodium APIs and select a supported integration path rather than inventing one.

## 8. Adaptive Quality Budget

Solar should use the conceptual model of a normalized quality budget:

```text
Solar quality budget: 0.0 → 1.0
```

Individual subsystems interpret that budget according to perceptual value and GPU cost rather than scaling every feature uniformly.

Examples of scalable systems include:

- volumetric resolution,
- volumetric ray/sample count,
- cloud quality,
- reflection resolution,
- reflection trace precision,
- shadow filtering,
- shadow distance,
- ambient-occlusion quality,
- indirect-light quality,
- water reflection quality,
- temporal reconstruction quality,
- secondary atmospheric sampling.

The renderer should prefer degrading expensive details that produce small perceptual gains before degrading effects central to Solar's identity.

## 9. Protected Quality Floor

AutoTune is allowed to make Solar cheaper, but not visually incoherent.

The following categories should eventually receive explicit minimum-quality rules:

- core lighting behavior,
- tone mapping and color science,
- temporal stability,
- basic shadow readability,
- atmosphere sufficient to preserve the Solar look,
- material coherence,
- water readability,
- exposure behavior.

If the machine cannot sustain the configured target FPS without violating the protected quality floor, Solar should stop reducing quality and report, where technically possible, that the selected target cannot be maintained under the current conditions.

The project must not silently degrade into a radically different visual product simply to display "120 FPS."

## 10. Target FPS and Frame-Time Controller Requirements

Solar must separate **hardware capability** from **the user's intended frame-rate target**.

The nominal total frame budget is:

```text
budget_ms = 1000 / target_fps
```

Reference values:

| Target FPS | Nominal total frame budget |
| ---: | ---: |
| 30 | 33.33 ms |
| 60 | 16.67 ms |
| 75 | 13.33 ms |
| 90 | 11.11 ms |
| 120 | 8.33 ms |
| 144 | 6.94 ms |
| 165 | 6.06 ms |
| 240 | 4.17 ms |

These are total-frame budgets, not permission for Solar to consume the entire interval. Minecraft, CPU work, other mods, driver overhead, and frame-pacing reserve still require headroom.

### 10.1 AUTO target selection

The recommended default policy is:

1. If a lower intentional game cap can be determined reliably, use that cap as the AutoTune performance target.
2. If the game is uncapped or capped above 120 FPS, use **120 FPS** as Solar's default cinematic-performance target unless the user explicitly selects a higher target.
3. If VSync effectively limits presentation below 120 FPS and that limit can be determined reliably, AutoTune may use the effective presentation target.
4. Never lower the target merely because a demanding scene temporarily performs poorly. Performance shortfalls should cause quality adaptation, not silently redefine the user's desired frame rate.
5. Never infer the configured cap from `frameTime` alone.

That last rule is critical. A game intentionally capped at 60 FPS naturally presents about 16.67 ms frame cadence even when substantial GPU headroom remains. Treating that cadence as proof of overload would cause Solar to reduce quality precisely when it should be spending the user's extra budget.

### 10.2 Standalone shader behavior

Current Iris documentation exposes `frameTime`, but the documentation query performed for this revision did not surface a shader-visible uniform for the user's configured maximum frame rate, VSync state, or monitor refresh rate.

Therefore the standalone shader must not pretend it can always discover those values.

Without the optional companion, Solar should expose a clear target-FPS control, with `120` as the default and common targets such as 30, 60, 75, 90, 120, 144, 165, and 240 available where practical.

The exact option representation must be verified against the final `shaders.properties` design before implementation.

### 10.3 Controller behavior

For any selected target:

- derive the nominal frame interval from the selected target,
- reserve safety headroom rather than filling the complete interval,
- use smoothed or windowed frame-time measurements,
- reduce quality only after sustained evidence that the usable budget is exceeded,
- restore quality more conservatively than it removes it,
- use hysteresis and rate limits to prevent oscillation,
- preserve the protected cinematic quality floor,
- allow higher quality at lower targets when headroom exists.

Exact thresholds, reserve ratios, time windows, and control equations belong to the dedicated adaptive-performance specification and must be measured rather than guessed.

## 11. Performance Engineering Rules

Every major rendering feature must have an understood approximate GPU cost.

Preferred techniques include, where appropriate:

- temporal reuse,
- temporal accumulation,
- reprojection,
- adaptive sampling,
- lower-resolution intermediate buffers,
- intelligent upsampling,
- interleaved/checkerboard rendering,
- hierarchical calculations,
- early rejection,
- distance-based quality reduction,
- adaptive ray/sample counts,
- cached lighting information,
- spatial reconstruction,
- temporal reconstruction,
- optimized shadow sampling,
- optimized volumetric rendering,
- noise-driven sampling,
- selective high-quality rendering based on visual importance.

The renderer should prefer clever approximations with excellent visual return over brute-force sample counts.

A visually spectacular effect that consumes an unjustified portion of the 8.33 ms frame budget should be treated as an engineering problem to solve, not an unavoidable badge of quality.

## 12. Benchmarking Contract

Repeatable benchmark scenarios must eventually cover at least:

- dense forest,
- open plains,
- mountains,
- large bodies of water,
- villages,
- caves,
- Nether,
- End,
- sunrise,
- midday,
- sunset,
- night,
- rain,
- thunderstorms,
- heavy foliage,
- long render distances.

Record, where measurable:

- average FPS,
- 1% low FPS,
- GPU frame time,
- CPU frame time,
- major rendering-pass timings,
- render resolution,
- render distance,
- shader profile,
- AutoTune state,
- selected target FPS,
- configured game FPS cap where known,
- VSync state where known,
- monitor refresh rate where known,
- Minecraft version,
- Iris version,
- Sodium version where applicable,
- GPU,
- CPU,
- relevant modpack context.

Average FPS alone is insufficient. Frame pacing and 1% lows matter.

Benchmark results produced without a real Minecraft runtime must be clearly labeled as static or synthetic and must not be presented as measured in-game performance.

## 13. Documentation Model

Durable architectural knowledge must live in the repository rather than only in ChatGPT conversations.

Solar-specific Superpowers artifacts live under:

- `Solar-Shader/docs/superpowers/specs/`
- `Solar-Shader/docs/superpowers/plans/`

Additional long-lived architectural documentation lives under:

- `Solar-Shader/docs/architecture/`

Benchmark methodology and results belong under:

- `Solar-Shader/benchmarks/`

The Solar README should eventually identify:

- project purpose,
- current development status,
- compatibility targets,
- repository layout,
- performance target,
- AutoTune concept,
- validation limitations,
- links to architectural documentation.

## 14. Branching Model

Use `main` for stable integrated work.

Solar Shader branches should be descriptive and scoped, for example:

- `feat/solar-workspace`,
- `feat/solar-foundation`,
- `feat/solar-lighting`,
- `feat/solar-shadows`,
- `feat/solar-water`,
- `feat/solar-atmosphere`,
- `feat/solar-autotune`,
- `fix/solar-<issue>`.

Branches are not permanent containers for independent projects.

Substantial future feature work should normally:

1. start from current `main`,
2. use a focused branch,
3. make small meaningful commits,
4. receive available static/CI verification,
5. be reviewed,
6. merge back into `main`.

## 15. ChatGPT Development Contract

Before modifying Solar Shader, ChatGPT should inspect:

1. relevant repository files,
2. the approved specification and implementation plan for the task,
3. recent relevant commits,
4. current external documentation when behavior may have changed.

GitHub is the canonical project state. Conversation memory must never override current repository contents.

For substantial new systems, use the Superpowers flow:

1. brainstorm,
2. approve conversational design,
3. write and commit specification,
4. review and approve specification,
5. write implementation plan,
6. review plan and choose execution method,
7. implement,
8. verify,
9. review,
10. integrate.

Context7 should be used for current Iris, Sodium, rendering-library, and other relevant technical documentation whenever behavior is version-sensitive.

## 16. Validation Boundaries

There is no guaranteed Minecraft runtime available during ChatGPT-only development.

Therefore:

- source inspection is static validation,
- generic GLSL compilation is static validation,
- GitHub Actions checks are static validation,
- successful static validation is not proof that Iris or Minecraft renders the shader correctly,
- visual quality cannot be claimed without genuine runtime output,
- 120 FPS cannot be claimed without measured runtime evidence,
- driver-specific behavior cannot be claimed verified without runtime evidence on relevant hardware.

Iris preprocesses and transforms shader source before final GPU compilation, so generic GLSL validation is useful but not authoritative for full Iris compatibility.

## 17. Out of Scope for Workspace Setup

The workspace setup must not yet implement:

- terrain rendering,
- deferred rendering,
- shadows,
- atmosphere,
- volumetric clouds,
- water,
- reflections,
- ambient occlusion,
- anti-aliasing,
- bloom,
- PBR,
- tone mapping,
- runtime adaptive-quality algorithms,
- Solar AutoTune companion code,
- fabricated benchmark results,
- GitHub Actions that pretend to validate Iris runtime behavior.

Those belong to later approved specifications and implementation plans.

## 18. Workspace Success Criteria

The workspace milestone is complete when:

1. Solar Shader is clearly isolated under `Solar-Shader/`.
2. Root and project documentation make the monorepo/project boundary obvious.
3. Superpowers specification and plan directories are established.
4. Benchmark, tools, and optional companion boundaries are documented.
5. The repository contains no speculative rendering implementation.
6. Future ChatGPT sessions can immediately discover where Solar source and durable decisions belong.
7. Branch conventions are documented.
8. The 120 FPS mainstream baseline and adaptive-quality philosophy are durable repository requirements.
9. Lower intentional FPS targets explicitly unlock larger rendering budgets rather than being treated as performance failures.
10. The workspace is ready for a separate shader-foundation architectural cycle.

## 19. External Technical References

Current Iris documentation was consulted through Context7 using `/irisshaders/docs`, including:

- shaderpack file structure,
- reusable `shaders/lib/` includes,
- `frameTime`,
- `viewWidth`,
- `viewHeight`,
- `far`,
- the documented shader-visible frame timing surface relevant to cap detection,
- `shaders.properties` profiles,
- sliders,
- conditional program enablement,
- per-profile program disabling,
- Iris feature declarations.

Primary documentation repository:

https://github.com/IrisShaders/docs

---

After this written specification is reviewed and approved, the next required step is a dedicated implementation plan for the workspace setup. No rendering or AutoTune implementation should begin as part of that workspace plan.
