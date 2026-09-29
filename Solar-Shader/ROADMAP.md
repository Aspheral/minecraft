# Solar Shader Roadmap

This roadmap describes the current intended development direction. It is not a claim that every listed rendering feature is already designed, approved, or implemented.

Each substantial rendering subsystem receives its own design/specification cycle before implementation.

## Milestone 0 — Workspace and Engineering Foundation

Status: complete on `feat/solar-workspace`; pending integration into `main`.

Scope:

- monorepo/project boundaries,
- durable architecture/spec/plan locations,
- benchmark methodology,
- 120 FPS mainstream baseline,
- target-FPS-aware AutoTune philosophy,
- optional companion boundary,
- agent continuity documentation,
- static-vs-runtime validation rules.

No rendering pipeline is part of this milestone.

## Milestone 1 — Shader Foundation Architecture

Next architectural cycle.

Expected questions include:

- target Minecraft/Iris compatibility range,
- initial shader program/pass structure,
- render targets and buffer ownership,
- reusable GLSL module boundaries,
- configuration/profile structure,
- initial CI/static-validation strategy,
- minimal runtime foundation that can be genuinely tested in Minecraft.

No foundation implementation should begin until its design and plan are approved.

## Later Milestone Families

The ordering below is directional and may change as architecture and profiling data develops.

### Lighting and Shadows

Potential scope:

- sun/moon lighting,
- shadow architecture,
- filtering/contact shadows,
- emissive behavior,
- interior/cave lighting,
- indirect-light approximations.

### Atmosphere and Clouds

Potential scope:

- sky model,
- atmospheric scattering,
- volumetric fog,
- volumetric clouds,
- sunrise/sunset behavior,
- weather-aware and biome-aware atmosphere.

### Materials and Water

Potential scope:

- water reflection/refraction,
- underwater rendering,
- wet surfaces,
- material response,
- foliage transmission,
- caustics where practical.

### Temporal Reconstruction

Potential scope:

- anti-aliasing,
- reprojection,
- temporal accumulation/reuse,
- upsampling,
- stability controls,
- ghosting/shimmer mitigation.

### Adaptive Performance / AutoTune

Potential scope:

- normalized quality budget,
- target-FPS controller,
- hysteresis and smoothing,
- subsystem quality curves,
- quality floors,
- performance telemetry,
- automatic profile/envelope selection.

### Optional Solar AutoTune Companion

Potential scope only after verified Iris/Sodium integration research:

- richer hardware/configuration detection,
- configured FPS cap awareness,
- VSync/refresh behavior where supported,
- initial quality-envelope calibration,
- telemetry or settings integration if supported.

The shaderpack must remain useful without this companion.

## Web and Benchmark Tooling

The connected Vercel `minecraft` project may later host web-facing documentation, benchmark viewers, release utilities, or related Solar tooling if an approved plan calls for it.

It is not the shader runtime and should not drive rendering architecture.

## Decision Rule

Optimize for:

```text
cinematic quality + temporal stability + gameplay readability
subject to:
    selected target frame-time budget
    protected quality floor
    verified platform constraints
```

The project should aim for effects that look expensive because they are engineered intelligently, not because they brute-force the GPU.
