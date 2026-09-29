# Changelog

All notable Solar Shader project changes will be recorded here.

## Unreleased

### Shader Foundation v0

#### Added

- Implemented the lean hybrid-deferred Foundation frame skeleton.
- Added linear-light HDR scene color using `R11F_G11F_B10F` `colortex0`.
- Added compact `RGB10_A2` SurfaceData in `colortex1`, including octahedral normals, packed block/sky light, and surface classification.
- Added depth-based view-position reconstruction without a position render target.
- Added 21 thin Iris program pairs backed by shared GLSL modules.
- Added explicit metadata-writing versus color-only/translucent render-target ownership.
- Added debug views for normals, reconstructed position/depth, light metadata, and surface classification.
- Added `TARGET_FPS` and `DEBUG_VIEW` Foundation configuration.
- Added the deterministic `SolarQuality` consumer interface for future AutoTune integration.
- Added Python reference tests for SurfaceData packing and reconstruction mathematics.
- Added S0 structural validation and complete-manifest enforcement.
- Added pinned S1 generic GLSL compilation/linking with Khronos glslang 16.5.0 in GitHub Actions.
- Added an empty I0/I1 runtime evidence template.

#### Validation status

- S0: passing on the Foundation branch.
- S1: passing on the Foundation branch.
- I0: pending genuine Minecraft + Iris runtime evidence.
- I1: pending genuine rendered/performance evidence.

S0/S1 do not establish Iris runtime compatibility, visual quality, driver behavior, or FPS.

### Workspace Foundation

#### Added

- Established the Solar Shader workspace and performance architecture specification.
- Defined the 120 FPS mainstream baseline and target-FPS-aware AutoTune philosophy.
- Added the approved workspace implementation plan.
- Established repository entry points, architecture, benchmark, tooling, shader-library, companion, agent-continuity, and roadmap documentation.
- Recorded the connected Vercel `minecraft` project as optional infrastructure for future web-facing Solar tooling.

#### Status

- Workspace scaffolding was integrated into `main`.
- Shader Foundation architecture, specification, plan, source, and S0/S1 validation now exist on `feat/solar-foundation`.

#### Notes

- No final cinematic lighting, shadows, volumetrics, reflections, PBR materials, TAA, or runtime AutoTune controller are implemented by Foundation v0.
- The connected Vercel project is not Solar runtime evidence.
