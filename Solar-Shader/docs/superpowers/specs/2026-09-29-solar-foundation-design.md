# Solar Shader Foundation Architecture

**Date:** 2026-09-29  
**Repository:** `Aspheral/minecraft`  
**Project root:** `Solar-Shader/`  
**Foundation branch:** `feat/solar-foundation`  
**Design status:** Conversational design approved on 2026-09-29. This written specification requires user review before an implementation plan may be created.  
**Parent specification:** `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-workspace-design.md`

## 1. Purpose

This specification defines the first rendering foundation for Solar Shader.

Solar's long-term goal is an extremely cinematic Minecraft shader with unusually strong real-time performance. The foundation does not attempt to deliver that final look. Its purpose is to establish a compact, measurable, modular rendering skeleton that future lighting, atmosphere, shadows, water, temporal reconstruction, materials, post-processing, and adaptive-performance systems can build on without repeated architectural rewrites.

The foundation must preserve the project rule:

> Make inexpensive techniques look expensive.

That rule begins with avoiding unnecessary render-target bandwidth, reconstructing data when practical, isolating compatibility behavior, and preventing runtime quality logic from becoming entangled with rendering modules.

## 2. Scope

Foundation v0 includes:

- the initial Iris shaderpack program structure,
- a lean hybrid-deferred frame architecture,
- a compact two-target full-resolution color-buffer contract,
- depth-based position reconstruction,
- compact surface-data encoding,
- shared GLSL module boundaries,
- a minimal shader configuration surface,
- a stable quality-consumer interface for future AutoTune,
- debug views for runtime diagnosis,
- static source and mathematical validation,
- generic GLSL validation,
- the first Solar GitHub Actions workflow,
- explicit runtime acceptance criteria,
- performance-baseline recording rules.

Foundation v0 does not include:

- final sunlight or moonlight,
- shadow mapping,
- ambient occlusion,
- indirect-light approximations,
- volumetric fog,
- volumetric clouds,
- reflections,
- final water rendering,
- wet surfaces,
- PBR materials,
- foliage transmission,
- bloom,
- exposure adaptation,
- cinematic tone mapping,
- color grading,
- temporal anti-aliasing,
- temporal reconstruction,
- runtime adaptive-quality control,
- an AutoTune companion implementation,
- compute-shader rendering,
- SSBO-based rendering,
- custom-image dependencies,
- fabricated visual or performance claims.

Those systems require later approved architectural cycles.

## 3. Compatibility Baseline

Compatibility targets are dated engineering references, not permanent promises.

### 3.1 Primary target

As of 2026-09-29, the primary development and runtime reference is:

- Minecraft Java Edition 26.3,
- Fabric,
- Iris 1.11.6,
- Sodium 0.9.2.

Minecraft Java 26.3 released on 2026-09-15. Iris 1.11.6 publishes a Fabric build for Minecraft 26.3 and declares Sodium 0.9.2 as required content.

### 3.2 Secondary compatibility lane

The initial secondary compatibility lane is:

- Minecraft Java Edition 1.21.11,
- Fabric,
- Iris 1.10.x.

A current concrete reference point is Iris 1.10.5 for Fabric 1.21.11 with Sodium 0.8.3.

The secondary lane is not co-equal with the primary architecture target. It exists to detect avoidable compatibility regressions without forcing Solar to design around obsolete behavior.

### 3.3 GLSL baseline

Foundation shader programs use:

```glsl
#version 330 compatibility
```

Current Iris documentation states that Iris patches compatibility-profile shaderpacks and recommends the compatibility profile for ordinary shaderpack development.

No OpenGL 4.2+ facility is required by Foundation v0.

### 3.4 Advanced feature policy

Foundation v0 must not require:

- `COMPUTE_SHADERS`,
- `SSBO`,
- `CUSTOM_IMAGES`.

Current Iris documentation notes that native macOS OpenGL stops at 4.1 and therefore lacks compute shaders, custom images, SSBOs, and other post-4.1 features.

Future subsystem specifications may introduce optional accelerated paths using verified Iris feature flags. The base renderer remains the broad compatibility path until measured evidence justifies a stronger requirement.

The long-term compatibility philosophy is:

> Broad baseline, selective acceleration.

## 4. Rendering Architecture

Solar Foundation uses a **lean hybrid-deferred architecture**.

It is not a large traditional deferred renderer. Opaque and cutout geometry write a compact G-buffer, expensive derived work can later occur in deferred/composite stages, and translucent geometry remains forward-rendered unless a later approved design changes that boundary.

Conceptual frame flow:

```text
Minecraft / Iris geometry
        |
        v
Solar opaque + cutout gbuffers
        |
        |-- colortex0: HDR scene/base color
        |-- colortex1: compact SurfaceData
        |-- depthtex*: Iris-owned depth
        |
        v
deferred
        |
        |-- decode SurfaceData
        |-- reconstruct position from depth
        |-- foundation-neutral processing / diagnostics
        |
        v
forward translucency
water / translucent hand / weather / fallback translucent geometry
        |
        v
composite
        |
        |-- pass-through or debug visualization
        |
        v
final
        |
        v
display
```

Foundation deferred processing must remain visually conservative. It proves data flow and reconstruction. It does not attempt to define Solar's final lighting identity.

## 5. Full-Resolution Buffer Contract

Foundation v0 owns exactly two full-resolution color targets.

| Buffer | Format | Foundation role |
| --- | --- | --- |
| `colortex0` | `R11F_G11F_B10F` | HDR scene/base color |
| `colortex1` | `RGB10_A2` | compact opaque/cutout surface metadata |

Iris-owned `depthtex0`, `depthtex1`, and `depthtex2` are inputs, not Solar allocations.

No Foundation v0 feature may claim `colortex2+`, an SSBO, or a custom image without a later approved specification changing this contract.

### 5.1 Scene color

`colortex0` uses `R11F_G11F_B10F`.

Reasons:

- 32 bits per pixel, comparable in storage width to RGBA8,
- supports HDR values required by later lighting, emissives, bloom, exposure, and tone mapping,
- avoids rebuilding the scene-color pipeline when HDR lighting arrives,
- alpha persistence is not required by Foundation v0.

Foundation output remains readable rather than aesthetically final.

#### 5.1.1 Color-space contract

`colortex0` is Solar's **linear-light HDR working buffer**.

Foundation and all later lighting math must operate in linear light. Gamma/display-encoded color must not be used as the working lighting space.

Texture, vertex-color, or other source values are converted at the appropriate boundary when their source representation requires it. The Foundation implementation plan must verify the actual Iris/Minecraft source semantics before choosing conversion functions rather than assuming every input has the same transfer function.

Foundation v0 does not implement Solar's artistic tone mapper. Its `final` boundary performs only the minimum display transfer needed to present the neutral linear scene readably. Later exposure, tone mapping, and color-grading specifications replace that minimal presentation path without changing the internal linear-light contract.

#### 5.1.2 Foundation clear policy

For Foundation v0:

- `colortex0` clears every frame to black before scene rendering unless verified Iris behavior makes an equivalent clear implicit,
- `colortex1` clears every frame to zero,
- zero in `colortex1` decodes to the invalid/background surface class,
- opaque/cutout geometry may write `colortex1`,
- forward translucent programs must not target or blend into `colortex1`.

Later temporal buffers may deliberately preserve history, but that is outside this Foundation contract.

### 5.2 SurfaceData

`colortex1` uses `RGB10_A2` and stores Foundation v0 `SurfaceData`.

Logical allocation:

```text
R10 : octahedral normal X
G10 : octahedral normal Y
B10 : packed lighting metadata
A2  : surface class
```

For Foundation v0, `B10` is defined as:

```text
5 bits : sky-light value
5 bits : block-light value
```

The source Minecraft light range is quantized to the 5-bit fields through a documented codec function. The implementation must not expose physical channel packing outside the surface codec.

The two-bit surface class is:

```text
0 = invalid / sky / background
1 = regular opaque surface
2 = cutout or foliage-capable surface
3 = reserved
```

This is not the final Solar material model.

### 5.3 Surface codec interface

Rendering modules consume logical data, not buffer channels.

The GLSL interface should be equivalent in responsibility to:

```glsl
struct SurfaceData {
    vec3 normal;
    float skyLight;
    float blockLight;
    int surfaceClass;
};

vec4 encodeSurface(SurfaceData surface);
SurfaceData decodeSurface(vec4 packed);
```

Exact signatures may vary during planning if GLSL constraints justify a different representation, but the abstraction boundary is mandatory.

No consumer may depend directly on `colortex1.r`, `.g`, `.b`, or `.a` semantics.

## 6. Buffer Allocation Rule

Every later render target must answer:

1. Why does this buffer exist?
2. Why cannot the value be reconstructed at acceptable cost and quality?
3. Why does it require this resolution?
4. Why does it require this format and precision?

A later subsystem specification must provide convincing answers before allocating persistent storage.

Current Iris exposes at least the traditional first 16 `colortex` attachments and newer Iris versions increased the available count to 32. Solar Foundation deliberately stays within the conservative first two.

The existence of spare attachments is not permission to consume them.

## 7. Depth and Position Reconstruction

Solar Foundation does not store position in a color target.

Opaque position is reconstructed from screen coordinates and depth using Iris-provided projection/model-view matrices and their inverses.

Conceptual reconstruction:

```text
screen UV + depth
      |
      v
clip / NDC position
      |
      v  gbufferProjectionInverse
view position
      |
      v  gbufferModelViewInverse
camera-relative/world-space representation as needed
```

For opaque deferred work, `depthtex1` is the preferred depth source because Iris documents it as excluding transparent geometry.

Future temporal systems may use Iris-provided previous-frame matrices and previous camera position. Foundation v0 does not allocate a motion-vector target.

A future specification may add explicit motion vectors only if measured stability/performance evidence justifies the bandwidth.

## 8. Opaque, Cutout, and Translucent Ownership

Opaque and cutout geometry participate in the compact G-buffer.

Translucency remains forward-rendered after Foundation deferred processing.

Foundation must not base its architecture on `separateEntityDraws`. Current Iris documentation warns that this property is broken in newer versions.

Water receives an explicit Solar program from the beginning because its future semantics differ fundamentally from ordinary opaque terrain.

The translucent hand path is also explicit.

Other specialized geometry may initially use Iris' documented fallback relationships until a later subsystem needs different semantics.

## 9. Initial Program Set

Foundation v0 should explicitly own approximately the following G-buffer entry points:

```text
gbuffers_basic
gbuffers_textured
gbuffers_textured_lit
gbuffers_terrain
gbuffers_skybasic
gbuffers_skytextured
gbuffers_hand
gbuffers_hand_water
gbuffers_water
gbuffers_weather
```

Foundation also owns:

```text
deferred
composite
final
```

Iris-documented fallback behavior may initially handle specialized programs such as:

```text
gbuffers_entities
gbuffers_block
gbuffers_damagedblock
gbuffers_particles
gbuffers_armor_glint
gbuffers_beaconbeam
```

The implementation plan must verify the final entry-point list against the current Iris fallback table before code is written.

No shadow program exists in Foundation v0.

## 10. Dimension Strategy

Foundation v0 uses the base `shaders/` tree for all dimensions.

It must not introduce:

- `world0/`,
- `world-1/`,
- `world1/`.

Current Iris documentation states that once legacy `worldN` folders are present, programs are loaded from those folders rather than from the base shader directory.

Overworld, Nether, and End therefore share the Foundation program architecture.

Dimension-specific visual behavior should later be data/configuration driven where practical. Separate dimension program trees require a later architectural justification.

## 11. Reduced-Resolution Future Work

Current Iris supports explicit `size.buffer.<bufferName>` configuration for reduced-resolution color targets.

Iris also documents that changing a color target's size prevents G-buffer programs from writing to it.

Solar treats that as a useful architectural boundary:

- compact geometry information stays full resolution,
- later expensive derived effects may run at half, quarter, checkerboard, interleaved, or otherwise reduced resolution in deferred/composite stages,
- reconstruction then restores full-resolution presentation.

Candidate future users include:

- volumetric clouds,
- fog,
- ambient occlusion,
- indirect-light approximations,
- reflections,
- atmospheric integration,
- bloom intermediates.

No reduced-resolution target is allocated by Foundation v0.

## 12. GLSL Module Architecture

Root shader files are thin program launchers.

Shared behavior lives under `Solar-Shader/shaders/lib/`.

Recommended structure:

```text
Solar-Shader/shaders/
|
|-- shaders.properties
|-- gbuffers_*.vsh / gbuffers_*.fsh
|-- deferred.vsh / deferred.fsh
|-- composite.vsh / composite.fsh
|-- final.vsh / final.fsh
|
`-- lib/
    |-- config.glsl
    |
    |-- core/
    |   |-- math.glsl
    |   |-- color.glsl
    |   |-- space.glsl
    |   |-- encoding.glsl
    |   `-- compatibility.glsl
    |
    |-- surface/
    |   |-- surface_data.glsl
    |   |-- surface_encode.glsl
    |   `-- surface_decode.glsl
    |
    |-- quality/
    |   `-- quality.glsl
    |
    |-- debug/
    |   `-- debug_view.glsl
    |
    `-- programs/
        |-- gbuffer_vertex.glsl
        |-- gbuffer_fragment.glsl
        |-- fullscreen_vertex.glsl
        |-- deferred_fragment.glsl
        |-- composite_fragment.glsl
        `-- final_fragment.glsl
```

The implementation plan may merge tiny libraries when separation does not improve ownership or testability. The architecture is about boundaries, not folder count.

Root shader programs should identify their semantic role and delegate to shared code.

Conceptually:

```glsl
#version 330 compatibility

#define SOLAR_PROGRAM_TERRAIN
#include "/lib/programs/gbuffer_fragment.glsl"
```

Program-specific logic belongs behind explicit program identifiers or small dedicated modules rather than broad copy-paste.

## 13. Configuration Ownership

Shader-visible Solar options are centralized in:

```text
/lib/config.glsl
```

Current Iris documentation requires shader options defined in multiple files to be defined identically. Centralizing the declarations prevents divergence.

`shaders.properties` owns:

- user-facing screen organization,
- profile relationships,
- sliders,
- coarse conditional program enablement,
- Iris feature declarations,
- custom CPU-side variables/uniforms when later justified.

`config.glsl` owns canonical shader-visible option declarations.

## 14. Quality-Control Layers

Solar distinguishes three control layers.

### 14.1 Architectural options

These select major algorithms or whole passes. They change rarely and may affect compiled shader structure.

Examples in later cycles:

- volumetric clouds on/off,
- reflection architecture,
- indirect-light pass on/off,
- expensive shadow algorithm selection.

### 14.2 Quality envelope

Profiles define the permitted quality range.

The long-term profile family is:

- `AUTO`,
- `PERFORMANCE`,
- `BALANCED`,
- `CINEMATIC`,
- `ULTRA`.

Foundation v0 must not invent fake visual distinctions between these profiles before scalable rendering systems exist.

The implementation plan may establish profile plumbing without exposing all profile buttons, or defer profile UI until profile values produce meaningful differences.

### 14.3 Runtime quality budget

Future adaptive performance uses fine-grained runtime scaling inside the chosen quality envelope.

Runtime adaptation must not repeatedly enable/disable whole shader programs.

Coarse structure is profile/compile-time controlled. Fine effort is runtime controlled.

## 15. Target FPS

Foundation configuration establishes the concept of user intent through `TARGET_FPS`.

The default is:

```text
TARGET_FPS = 120
```

Intended discrete targets include, where practical:

```text
30
60
75
90
120
144
165
240
```

The user's selected target is not inferred from `frameTime`.

The workspace performance contract remains:

- an intentional 60 FPS target has a nominal 16.67 ms total frame interval,
- 120 FPS has 8.33 ms,
- 240 FPS has 4.17 ms,
- uncapped play or caps above 120 FPS default to Solar's 120 FPS cinematic-performance target unless the user explicitly chooses higher,
- lower intentional targets may unlock more quality,
- the shader does not own the entire total frame interval.

Foundation v0 does not implement the adaptive controller.

## 16. Stable Quality Consumer Interface

Rendering modules must not know how AutoTune works.

They consume a stable logical quality interface equivalent in responsibility to:

```glsl
struct SolarQuality {
    float global;
    float atmosphere;
    float clouds;
    float shadows;
    float reflections;
    float indirectLight;
    float postProcessing;
};
```

with an accessor equivalent to:

```glsl
SolarQuality solarGetQuality();
```

Foundation v0 returns deterministic static values.

Later implementations may source quality from:

- static profile values,
- shader-native adaptive control,
- optional companion calibration,
- a combination of those mechanisms.

Rendering modules must not be rewritten merely because the quality controller changes.

This interface is the renderer-facing AutoTune boundary.

## 17. No Speculative AutoTune State Allocation

Foundation v0 does not reserve:

- a persistent `colortex`,
- a 1x1 temporal control texture,
- an SSBO,
- a custom image,
- another hidden GPU-state mechanism

for AutoTune.

The later adaptive-performance architecture chooses its temporal state mechanism after verified API research and measurement.

Iris `shaders.properties` custom variables/uniforms remain available as a potential tool, but Foundation does not assume they provide the complete semantics required by a stable frame-by-frame controller.

## 18. Program Enablement Policy

Iris `program.<program>.enabled` is used only for coarse, user/profile-driven structural choices.

A valid later use is enabling an optional expensive pass when a profile/architectural option calls for it.

It must not be used as a per-frame performance control.

Rule:

> Profiles decide which expensive passes exist. Runtime quality decides how hard enabled passes work.

## 19. Compatibility Abstraction

Version-specific Iris/Minecraft behavior belongs behind:

```text
/lib/core/compatibility.glsl
```

Current Iris provides macros including `IS_IRIS` and `IRIS_VERSION`.

Solar may use such macros when a verified behavior difference requires them.

Version checks must not be scattered throughout rendering modules.

If behavior is common, no compatibility branch exists.

If behavior differs, the common renderer calls a compatibility abstraction.

## 20. Debug Views

Foundation includes a developer-facing `DEBUG_VIEW` option with at least:

```text
0 = normal output
1 = decoded normals
2 = reconstructed depth / position visualization
3 = packed light metadata
4 = surface classification
```

The exact visualization mapping may be refined during implementation planning.

Debug views are diagnostic instrumentation, not aesthetic features.

Normal-view runtime acceptance should show coherent face-orientation groups. Depth/position visualization should remain stable through camera motion. Light metadata should vary coherently with Minecraft lighting. Surface classes should appear in expected opaque/cutout regions.

## 21. Evidence Model

Solar formally distinguishes four validation levels.

| Level | Evidence | What it establishes |
| --- | --- | --- |
| `S0` | source/repository checks | structural and architectural invariants |
| `S1` | generic GLSL validation | generic GLSL/preprocessor correctness |
| `I0` | Iris runtime load/compile | Iris patching and actual runtime shader compilation/loading |
| `I1` | rendered Minecraft evidence | rendered correctness, visual behavior, temporal stability, measured performance |

Passing one level does not imply the next.

A claim that Solar works in Iris requires `I0`.

A claim about visual quality or measured FPS requires `I1`.

## 22. Why Generic GLSL Is Not Iris Runtime Validation

Current Iris documentation states that shaderpack source is passed through Iris' `glsl-transformer` patcher before the patched code is compiled for the GPU.

Consequences include:

- patched source differs from repository source,
- error line numbers may correspond to patched code,
- the patcher may repair code that would otherwise fail,
- patching itself may expose behavior a generic validator cannot reproduce,
- Iris reserves internal naming patterns including `iris_`, `irisMain`, and `moj_import`.

Therefore generic GLSL checks are useful `S1` evidence only.

## 23. Static Validation Tooling

Foundation introduces a small dependency-light validator under:

```text
Solar-Shader/tools/
```

The preferred implementation language is Python unless planning uncovers a concrete reason to use another tool.

The validator should verify at least:

- expected shader entry points exist,
- `#version` placement is valid,
- referenced GLSL include paths exist,
- include graph cycles are rejected,
- Iris-reserved internal naming patterns are not introduced by Solar symbols,
- canonical config declarations are not duplicated inconsistently,
- expected `RENDERTARGETS` mappings are present,
- `colortex0` and `colortex1` formats match the Foundation contract,
- no Foundation allocation claims `colortex2+`,
- no `world0`, `world-1`, or `world1` directories appear,
- `COMPUTE_SHADERS`, `SSBO`, and `CUSTOM_IMAGES` are not required,
- Solar-specific files remain inside `Solar-Shader/` except approved shared monorepo infrastructure such as GitHub workflow files,
- the validator's own messages never claim runtime Iris success.

Static checks should enforce architectural decisions where doing so is deterministic.

## 24. Surface Codec Mathematical Tests

CPU-side reference tests verify the SurfaceData codec mathematics.

Coverage includes:

- octahedral normal encoding,
- octahedral normal decoding,
- positive and negative axes,
- arbitrary normalized directions,
- octant/boundary cases,
- light-field packing/unpacking,
- sky-light range,
- block-light range,
- surface-class packing/unpacking,
- documented quantization error bounds.

These tests establish codec mathematics, not GPU runtime behavior.

The implementation plan must define numerical tolerances rather than using exact floating-point equality.

## 25. Reconstruction Mathematical Tests

CPU-side reference tests verify position reconstruction mathematics with known matrices.

Test pattern:

```text
known view-space position
        |
        v
projection to screen/depth
        |
        v
Foundation inverse reconstruction
        |
        v
compare recovered position within tolerance
```

Coverage should include multiple depths, screen positions, and representative projection matrices.

These tests catch matrix order, perspective divide, handedness, and coordinate-convention errors before runtime testing.

## 26. Generic GLSL Validation

Foundation CI runs a pinned generic GLSL validator against relevant shader units.

It may detect:

- syntax errors,
- type errors,
- malformed expressions,
- missing symbols after local preprocessing,
- certain stage-interface errors,
- broken compile-time branches.

The tool/version must be pinned in the implementation plan or workflow so results do not drift silently.

CI output must explicitly state that generic GLSL validation does not prove Iris runtime compatibility.

## 27. GitHub Actions

Foundation introduces the first Solar GitHub Actions workflow:

```text
.github/workflows/solar-static.yml
```

The workflow should trigger on Solar-relevant changes for pull requests and pushes.

Where practical, path filters should avoid running Solar validation for changes limited to unrelated future monorepo projects.

The workflow should remain compact and understandable, with responsibilities equivalent to:

```text
Solar Static Validation
|
|-- source / architecture checks
|-- SurfaceData codec tests
|-- reconstruction math tests
`-- generic GLSL validation
```

A successful workflow means only that the represented static checks passed.

The workflow must not emit unsupported claims such as:

- Iris compatible,
- renders correctly,
- 120 FPS,
- cinematic quality,
- verified on NVIDIA/AMD/Intel.

## 28. First Genuinely Testable Minecraft Build

The first runtime-capable Foundation build is intentionally visually modest.

Its purpose is to answer:

> Is Solar's rendering skeleton correct enough to build the cinematic renderer on top of it?

Expected runtime flow:

```text
Minecraft world
      |
      v
Solar compact G-buffer
      |
      v
neutral deferred reconstruction
      |
      v
forward translucency
      |
      v
pass-through / debug composite
      |
      v
final presentation
```

Foundation is successful visually when Minecraft scene information remains readable and structurally coherent through Solar's pipeline.

"Looks cinematic" is not a Foundation v0 acceptance requirement.

## 29. I0 Runtime Acceptance Criteria

On the primary runtime target, a genuine test should verify:

- Iris discovers the shaderpack,
- the shaderpack enables successfully,
- no Solar shader compile failure is reported,
- a world loads,
- Overworld renders,
- Nether renders,
- End renders,
- terrain remains visible and coherent,
- entities remain visible through explicit or fallback programs,
- block entities remain visible through explicit or fallback programs,
- sky renders,
- hand renders,
- water/translucency remains usable,
- weather can render,
- dimension switching does not break the active programs,
- shader reload succeeds,
- debug views can be selected and produce coherent diagnostic output.

A corresponding secondary-lane smoke test should later be run on Minecraft 1.21.11 + Iris 1.10.x.

If no Minecraft runtime is available during ChatGPT-only engineering, `I0` remains explicitly pending.

## 30. I1 Visual and Performance Evidence

Foundation v0 does not claim final visual quality.

Any FPS or frame-time number must come from genuine runtime evidence with conditions attached.

Initial Foundation runtime measurement should record, where available:

- resolution,
- render distance,
- Minecraft version,
- Iris version,
- Sodium version,
- GPU,
- CPU,
- FPS cap,
- VSync,
- monitor refresh rate where known,
- Solar enabled/disabled,
- average FPS,
- 1% low FPS,
- CPU/GPU timing where measurable,
- benchmark scene and camera conditions.

The purpose is to establish an empty-chassis Foundation cost, not to announce that Solar has already achieved its final 120 FPS goal.

Foundation v0 does not fail merely because one arbitrary machine runs below 120 FPS.

The 120 FPS project baseline becomes a meaningful pass/fail target only under the project's defined mainstream benchmark conditions with genuine runtime measurements.

## 31. Future Feature Cost Accounting

Every later major rendering subsystem should eventually compare its incremental frame cost against an appropriate baseline.

A benchmark record should include:

```text
feature
baseline configuration
feature-enabled configuration
scene
resolution
render distance
quality setting
target FPS
delta GPU frame time where measurable
delta average FPS
delta 1% low
```

Incremental frame-time cost is often more informative than raw FPS.

High perceptual gain at low incremental cost is Solar's preferred optimization territory.

## 32. Vercel Boundary

The connected Aspheral Vercel project named `minecraft` is not used by Foundation implementation or validation.

No Foundation task should deploy a web application merely because Vercel is connected.

Future approved cycles may use Vercel for:

- documentation,
- benchmark visualization,
- release tooling,
- performance-history viewers,
- development utilities.

Vercel has no authority over Minecraft shader runtime architecture.

## 33. Implementation Branch and Integration

Implementation planning and later Foundation code stay on:

```text
feat/solar-foundation
```

The branch starts from the integrated workspace milestone on `main`.

No Foundation rendering implementation is written before:

1. this specification is committed,
2. the user approves this written specification,
3. a Superpowers implementation plan is written and committed,
4. the user reviews the plan and selects an execution method.

After implementation, verification and review occur before integration to `main`.

## 34. Foundation v0 Definition of Done

Foundation v0 implementation is complete only when:

1. approved Foundation source exists on `feat/solar-foundation`,
2. the two-buffer full-resolution contract is implemented,
3. opaque/cutout SurfaceData encoding is implemented behind the codec abstraction,
4. position reconstruction is implemented without a position render target,
5. the approved initial program/fallback strategy is implemented,
6. dimension handling uses the shared base shader tree,
7. GLSL modules preserve the approved ownership boundaries,
8. `TARGET_FPS` and debug configuration foundations exist,
9. the renderer-facing quality API exists with deterministic static values,
10. no adaptive controller is falsely implemented,
11. no required compute/SSBO/custom-image dependency is introduced,
12. `S0` validation passes,
13. codec and reconstruction mathematical tests pass,
14. `S1` generic GLSL validation passes,
15. CI accurately labels all static evidence,
16. code review identifies no unresolved architectural violation,
17. runtime validation is either recorded as `I0/I1` evidence or explicitly marked pending,
18. no unmeasured FPS, visual-quality, driver, or Iris-runtime claim is made.

## 35. Known Risks and Deliberate Deferrals

### 35.1 RGB10_A2 metadata precision

The compact SurfaceData format may eventually prove insufficient for richer material data.

Mitigation: physical packing is isolated behind the codec. Later material specifications may revise the storage contract with measured justification.

### 35.2 Fallback-program semantic gaps

Relying on Iris fallbacks may not preserve every geometry-specific semantic needed by later lighting/material systems.

Mitigation: Foundation uses fallbacks only where semantics are currently equivalent enough for structural validation. Later systems add explicit programs when they require different data.

### 35.3 Translucency complexity

Forward translucency is intentionally simple in Foundation. Refraction, water lighting, translucent entity behavior, particles, and sorting require later dedicated design.

### 35.4 Temporal requirements

Foundation avoids motion-vector/history allocations. Later temporal reconstruction may justify new buffers.

### 35.5 Optional acceleration maintenance cost

Maintaining baseline and accelerated paths can create complexity.

Mitigation: no optional accelerated path is introduced without measured benefit large enough to justify maintaining it.

### 35.6 Generic GLSL false confidence

Static compilation can never represent Iris' full patching/runtime environment.

Mitigation: validation levels are explicit and CI language is constrained.

## 36. Architectural Decisions Locked by This Spec

Unless superseded by a later approved specification:

- Solar Foundation is lean hybrid-deferred.
- Foundation owns two full-resolution color targets.
- `colortex0` is `R11F_G11F_B10F` linear-light HDR scene color.
- `colortex1` is `RGB10_A2` SurfaceData and clears to zero each frame.
- position is reconstructed from depth rather than stored,
- opaque/cutout geometry participates in SurfaceData,
- translucency remains forward-rendered,
- Foundation does not rely on `separateEntityDraws`,
- base shader programs serve all dimensions,
- root shader files remain thin,
- shared GLSL modules own common behavior,
- configuration is centralized,
- renderer modules consume a stable quality interface,
- Foundation does not allocate speculative AutoTune state,
- no advanced Iris feature is required,
- coarse program structure is not a per-frame AutoTune mechanism,
- static and runtime evidence are formally separated,
- the first runtime build prioritizes structural correctness over cinematic effects.

## 37. External Technical References

Current Iris documentation was consulted through Context7 using `/irisshaders/docs`, including:

- shaderpack program structure and fallbacks,
- `colortex` behavior,
- color-buffer formats,
- buffer sizing,
- depth buffers,
- projection/model-view uniforms,
- shader settings and profiles,
- `program.enabled`,
- feature flags,
- custom variables/uniforms,
- Iris macros,
- macOS OpenGL limitations,
- Iris shader patching and debug behavior.

Primary Iris documentation repository:

https://github.com/IrisShaders/docs

Current release references checked for this design:

- Minecraft Java Edition 26.3 release page,
- Iris 1.11.6 + Minecraft 26.3 Fabric release metadata,
- Iris 1.10.x + Minecraft 1.21.11 Fabric release metadata.

These compatibility references are dated 2026-09-29 and must be re-checked before later version-sensitive implementation changes.

---

This specification defines architecture only. Approval of this file permits the next Superpowers step: writing the implementation plan. It does not permit implementation before that plan is reviewed and its execution method is approved.
