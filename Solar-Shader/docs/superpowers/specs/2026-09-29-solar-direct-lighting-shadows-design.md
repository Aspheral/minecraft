# Solar Direct Lighting + Shadow Foundation Architecture

**Date:** 2026-09-29  
**Repository:** `Aspheral/minecraft`  
**Project root:** `Solar-Shader/`  
**Design branch:** `feat/solar-direct-lighting-shadows`  
**Baseline:** `main` at Foundation merge commit `b5f7d05fc4f3e3a2024c7a5d75d3c92f33ddf281`  
**Design status:** Conversational design and written specification approved on 2026-09-29. Implementation still requires an approved implementation plan and execution method.  
**Parent specifications:**  
- `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-workspace-design.md`
- `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-foundation-design.md`

## 1. Purpose

This specification defines Solar Shader's first genuinely visual rendering subsystem: **Direct Lighting + Shadow Foundation**.

The cycle adds:

- directional celestial lighting,
- a conventional Iris shadow pass,
- a camera-centered distorted shadow map,
- deterministic manual PCF filtering,
- opaque and transparent/colored shadow transmission,
- conservative block/sky-light readability terms,
- weather attenuation,
- shadow-quality envelopes,
- shadow diagnostics,
- static mathematical validation,
- explicit runtime and performance acceptance criteria.

The design is intentionally narrower than the full roadmap's "Lighting and Shadows" family.

A later lighting cycle owns:

- indirect lighting,
- propagated interior lighting,
- emissive material behavior,
- GI/SSGI/voxel lighting,
- advanced contact shadows,
- physically varying penumbrae.

The goal of this cycle is to establish a clean, scalable direct-light/shadow architecture that can remain in place while those later systems are added.

The governing Solar rule remains:

> Make inexpensive techniques look expensive before spending more GPU budget.

## 2. Existing Foundation Contract

This cycle builds on the merged Foundation v0 architecture.

Foundation already provides:

- GLSL 330 compatibility,
- `colortex0` as `R11F_G11F_B10F` linear-light HDR scene color,
- `colortex1` as `RGB10_A2` compact `SurfaceData`,
- view-space normals,
- normalized block and sky light metadata,
- surface classification,
- depth-based view-position reconstruction,
- a neutral `deferred` pass,
- forward color-only/translucent paths,
- a `SolarQuality` ABI,
- `TARGET_FPS`,
- debug views,
- S0/S1 static validation.

This lighting cycle must not expand the full-resolution Solar color-buffer contract.

No `colortex2+` attachment is allocated.

## 3. Scope

### 3.1 Included

This cycle includes:

- explicit Iris shadow programs,
- shared shadow vertex/fragment code,
- shadow-map configuration,
- shadow distortion,
- world/view/player/shadow coordinate conversion,
- deterministic manual PCF,
- transparent and colored shadow approximation,
- receiver bias,
- shadow distance fade,
- direct sun/moon lighting,
- weather attenuation,
- no-skylight dimension handling,
- block/sky readability approximation,
- one public shadow-quality control,
- one additional developer shadow debug view,
- static tests and validation updates,
- runtime acceptance and benchmark methodology updates,
- documentation reconciliation after Foundation merge.

### 3.2 Excluded

This cycle does not implement:

- ambient occlusion,
- GI or SSGI,
- voxel lighting,
- emissive material extraction,
- colored propagated block lighting,
- screen-space contact shadows,
- PCSS,
- temporal shadow accumulation,
- stochastic per-frame shadow jitter,
- TAA/TAAU,
- volumetric shafts,
- atmosphere-derived sunlight,
- physically simulated sky scattering,
- exposure adaptation,
- bloom,
- compute shaders,
- SSBOs,
- custom images,
- additional full-resolution Solar color targets,
- Vercel-hosted runtime or benchmark infrastructure.

## 4. Compatibility Reference

Dated 2026-09-29, Solar continues using:

### Primary reference

- Minecraft Java Edition 26.3,
- Fabric,
- Iris 1.11.6,
- Sodium 0.9.2.

### Secondary lane

- Minecraft Java Edition 1.21.11,
- Fabric,
- Iris 1.10.x.

Version-sensitive behavior must be rechecked before implementation if these references change.

The GLSL baseline remains:

```glsl
#version 330 compatibility
```

No feature introduced by this cycle may require compute shaders, SSBOs, or custom images.

## 5. Why This Architecture

Three architectural families were considered.

### 5.1 Basic fixed shadow map

A 2K map with fixed PCF is simple and relatively inexpensive, but allocates texel density uniformly across the shadow field and therefore spends too much precision on distant geometry.

### 5.2 Distorted single-map shadow system

A single conventional shadow map is distorted in shadow clip space so geometry near the player receives more effective texel density. Manual PCF supplies stable filtering. This is the selected architecture.

Advantages:

- one ordinary Iris shadow-map family,
- no extra full-resolution Solar buffers,
- good near-player detail at 2K-class resolutions,
- predictable compatibility,
- scalable filtering cost,
- raw shadow depth remains available,
- fits the existing Foundation deferred path.

### 5.3 Cascaded or multi-map architecture

Cascaded/multi-map designs can provide stronger long-distance quality, but they increase implementation complexity, state, sampling, and validation burden. Current Iris documentation also describes more advanced shadow-map optimization as difficult within the traditional shaderpack pipeline.

Solar therefore starts with the distorted single-map path and requires measured evidence before considering a more complex replacement.

## 6. Frame Architecture

Foundation v0:

```text
opaque/cutout G-buffer
        |
        v
neutral deferred
        |
        v
forward translucency
        |
        v
composite
        |
        v
final
```

This cycle:

```text
                     shadow geometry
                           |
                           v
                 Iris shadow buffers
                           |
                           |
opaque/cutout G-buffer ----+----> deferred direct lighting
                                      |
                                      v
                              forward translucency
                                      |
                                      v
                                  composite
                                      |
                                      v
                                    final
```

Direct lighting belongs in `deferred`.

`composite` remains a post/diagnostic boundary and must not become the primary lighting stage.

## 7. Shadow Program Ownership

Solar explicitly owns:

```text
shadow
shadow_solid
shadow_cutout
shadow_water
shadow_entities
shadow_block
```

Each program has a thin `.vsh` and `.fsh` wrapper backed by shared code.

Recommended library boundary:

```text
Solar-Shader/shaders/lib/shadow/
    settings.glsl
    transform.glsl
    bias.glsl
    sampling.glsl
    filtering.glsl
    shadow_vertex.glsl
    shadow_fragment.glsl
```

Lighting code is separate:

```text
Solar-Shader/shaders/lib/lighting/
    celestial.glsl
    readability.glsl
    direct.glsl
```

The implementation plan may merge a file only when the resulting ownership remains clear.

## 8. Shadow-Pass Output Contract

Iris predetermines shadow-pass render targets.

Solar shadow fragment programs therefore do **not** use `RENDERTARGETS` to write `colortex`.

Shadow-pass location 0 writes `shadowcolor0`.

For Solar-owned shadow programs, `shadowcolor0.rgb` stores **linear-light caster color** and `shadowcolor0.a` stores the source caster alpha used by the transmission approximation. Textured shadow fragments therefore convert source RGB through Solar's established encoded-to-linear boundary before writing `shadowcolor0`.

Cutout discard decisions still use source alpha before the shadow color write.

Foundation color attachments remain untouched by the shadow pass.

Solar uses the current Iris semantics:

- `shadowtex0`: depth including all shadow-casting geometry,
- `shadowtex1`: depth excluding transparent geometry,
- `shadowcolor0`: color/alpha information from shadow-casting geometry.

No `shadowcolor1` use is required in this cycle.

## 9. Shadow Geometry Behavior

### 9.1 Solid geometry

Solid terrain, opaque entities, and opaque block entities cast ordinary depth shadows.

### 9.2 Cutout geometry

Cutout shadow programs sample `gtexture` and apply the appropriate alpha cutoff before contributing to the shadow map.

Leaves, fences, grass-like cutouts, and similar geometry should cast shaped shadows rather than rectangular cards.

### 9.3 Translucent terrain

`shadow_water` participates in the transparent-shadow path.

The shader settings enable translucent terrain in the shadow pass:

```properties
shadowTranslucent=true
```

The resulting transparency/color data may contribute to colored transmittance.

This cycle does not attempt physically accurate refractive water shadowing.

### 9.4 Entities and block entities

Explicit shadow entity/block wrappers preserve future ownership even if they initially share implementation.

Entity shadow distance is quality-envelope controlled.

## 10. Shadow Quality Option

Solar introduces one public subsystem option:

```glsl
#define SHADOW_QUALITY 2 // [0 1 2 3]
```

The default is `2` (Cinematic).

The approved static envelopes are:

| SHADOW_QUALITY | Label | Resolution | Shadow distance | Max PCF taps | Entity distance multiplier |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | Performance | 1024 | 96 blocks | 4 | 0.50 |
| 1 | Balanced | 2048 | 128 blocks | 6 | 0.70 |
| 2 | Cinematic | 2048 | 160 blocks | 8 | 0.85 |
| 3 | Ultra | 4096 | 192 blocks | 12 | 1.00 |

These values are initial engineering envelopes, not evidence that each tier meets a particular FPS.

The distinction between Balanced and Cinematic is intentionally **not** another shadow-map resolution jump.

4096² is reserved for Ultra because it contains four times as many pixels as 2048².

## 11. Static Envelope and Future Runtime Effort

`SHADOW_QUALITY` controls structural maxima:

- map resolution,
- maximum shadow distance,
- maximum PCF taps,
- entity shadow distance.

The existing:

```glsl
solarGetQuality().shadows
```

remains the future runtime effort input.

During this cycle it returns 1.0, so all behavior is deterministic.

A future AutoTune cycle may map the runtime scalar to:

- actual PCF tap count up to the selected maximum,
- filter radius,
- effective shadow distance within the structural maximum,
- optional transparent-shadow refinement.

AutoTune must not rebuild shadow-map resolution every few frames.

## 12. Core Shadow Constants

For the selected quality envelope, shared shadow settings define Iris-visible constants equivalent in responsibility to:

```glsl
const int shadowMapResolution = ...;
const float shadowDistance = ...;
const float shadowDistanceRenderMul = 1.0;
const float entityShadowDistanceMul = ...;
```

Shadow-pass culling is:

```properties
shadow.culling=true
```

The cycle does not use reversed shadow culling.

Mipmap generation is not required for the initial manual-PCF path.

## 13. Manual Filtering Policy

Solar uses deterministic manual PCF.

Initial shadow buffer filtering is nearest:

```glsl
const bool shadowtex0Nearest = true;
const bool shadowtex1Nearest = true;
const bool shadowcolor0Nearest = true;
```

Solar does not enable hardware shadow filtering in this cycle.

Reasons:

- manual PCF needs raw depth,
- transparent-shadow logic depends on comparing both shadow depth buffers,
- deterministic behavior is easier to validate,
- no additional Iris feature flag is required,
- future algorithms retain access to unmodified shadow depth.

No mipmapped shadow filtering is required in this cycle.

## 14. PCF Sample Pattern

The maximum deterministic kernel contains 12 samples.

The sample list is ordered as symmetric opposite pairs so every approved prefix remains approximately zero-centered.

Approved tap counts are:

```text
4
6
8
12
```

The implementation plan must define one fixed disk/cross-like ordered kernel satisfying:

- each sample lies within the declared unit radius,
- samples are distributed around the receiver rather than clustered on one side,
- the 4-tap prefix is symmetric,
- the 6-tap prefix remains symmetric,
- the 8-tap prefix remains symmetric,
- all 12 taps remain symmetric,
- the centroid of each approved prefix is approximately zero.

There is no per-frame random rotation or temporal jitter in this cycle.

## 15. Shadow Filter Radius

Sample count and filter radius are separate controls.

The initial filter radius is small near the camera and may grow mildly with receiver distance.

The cycle's goal is:

- suppress hard aliasing,
- avoid visibly blocky shadow edges,
- provide modest cinematic softness,
- avoid pretending PCF is a physically accurate penumbra model.

True blocker-distance-driven penumbrae belong to a later PCSS/contact-shadow cycle.

## 16. Shadow Distortion

Solar centralizes one function:

```glsl
vec3 solarDistortShadowClip(vec3 shadowClipPosition);
```

The same function is used:

1. when writing shadow-map geometry,
2. when transforming a deferred receiver into shadow-map coordinates.

The initial distortion model follows the currently documented Iris single-map approach:

```text
radial = length(shadowClip.xy)
factor = radial + 0.1
shadowClip.xy /= factor
shadowClip.z *= 0.5
```

The implementation must guard the divisor against invalid/near-zero behavior even though the additive 0.1 term already protects the common case.

The distortion's purpose is not artistic. It reallocates effective shadow texel density toward geometry close to the player.

Any future change to this equation must update the write and sample paths together.

## 17. Receiver Coordinate Conversion

The deferred pass already reconstructs the receiver's view-space position.

For a valid surface, the shadow-coordinate path is:

```text
screen UV + depth
    |
    v
view position
    |
    v  gbufferModelViewInverse
player space
    |
    v  shadowModelView
shadow view
    |
    v  shadowProjection
shadow clip
    |
    v  solarDistortShadowClip
distorted shadow clip
    |
    v  perspective divide
shadow NDC
    |
    v  *0.5 + 0.5
shadow screen coordinates
```

This matches the current Iris coordinate-space model.

No position render target is added.

## 18. Receiver Coverage and Early Outs

Before PCF, deferred lighting checks:

1. valid SurfaceData,
2. `hasSkylight`,
3. positive direct-light cosine,
4. receiver within effective shadow range/coverage.

If any check fails, no shadow texture sample is required.

Examples:

- background/sky SurfaceData -> no receiver shadow work,
- Nether-like no-skylight dimension -> no celestial direct lighting or shadow sampling,
- back-facing surface -> no celestial direct contribution,
- receiver beyond shadow range -> no shadow lookup.

This cycle may still incur Iris shadow-pass geometry cost in a no-skylight dimension because program availability is shaderpack-level rather than a runtime uniform decision. Avoiding that cost through dimension-specific program routing is deferred unless I1 evidence shows it is worth the added architecture.

## 19. Shadow Distance Fade

Shadow influence must not terminate abruptly.

Define:

```text
fadeStart = 0.85 * effectiveShadowDistance
fadeEnd   = 1.00 * effectiveShadowDistance
```

Behavior:

- receiver distance <= fadeStart: full shadow result,
- fadeStart < distance < fadeEnd: smooth transition toward full direct-light transmittance,
- distance >= fadeEnd: no shadow lookup is required.

The interpolation uses a smoothstep-like monotonic curve.

Receiver distance is measured in player-space horizontal distance unless implementation evidence demonstrates that another metric produces materially better coverage behavior.

## 20. Shadow Bias Architecture

Bias is isolated in:

```text
lib/shadow/bias.glsl
```

The logical interface is equivalent to:

```glsl
float solarShadowBias(
    vec3 normal,
    vec3 lightDirection,
    float receiverDistance,
    float distortionMetric
);
```

The implementation combines:

- a small constant component,
- a normal/slope-dependent component,
- a distance/distortion compensation component where needed.

Required mathematical properties:

- finite for valid inputs,
- never negative,
- grazing-angle bias is not lower than face-on bias,
- adjustment does not discontinuously jump across the valid receiver range.

The exact numeric constants are tunable implementation parameters and must be centralized.

Static tests can prove mathematical properties.

Only I1 rendered evidence can judge acne, Peter Panning, and visible shimmer.

## 21. Opaque Shadow Visibility

For each PCF tap:

```text
allVisibility    = receiverDepth <= shadowtex0Depth
opaqueVisibility = receiverDepth <= shadowtex1Depth
```

PCF averages both quantities across the selected kernel.

Interpretation:

- `allVisibility` represents visibility through the nearest geometry of any transparency class,
- `opaqueVisibility` represents visibility considering only opaque blockers.

The values are transmittance-like:

- 1.0 = light reaches receiver,
- 0.0 = blocked for that depth class.

## 22. Transparent and Colored Shadow Approximation

The direct-light shadow result is RGB transmittance:

```glsl
vec3 solarShadowTransmittance(...);
```

The PCF averages provide:

```text
unblockedFraction          = allVisibility
transparentBlockedFraction = max(opaqueVisibility - allVisibility, 0)
opaqueBlockedFraction      = 1 - opaqueVisibility
```

Opaque blocked fraction contributes zero direct transmittance.

When `transparentBlockedFraction` is meaningfully above zero, Solar performs a **conditional central/representative `shadowcolor0` lookup**, rather than sampling color once per PCF tap.

If the representative color sample has effectively zero alpha even though the PCF footprint detected transparent blocking, Solar uses a neutral scalar transmission fallback derived from the transparent blocked fraction rather than introducing arbitrary color. This prevents undefined/clear-buffer color from tinting a shadow edge.

The transparent transmission approximation is based on current Iris semantics and Solar's linear-light working contract:

```text
casterTransmissionRGB = linearShadowColor.rgb * (1 - shadowColor.a)
```

Because Solar writes linear RGB into `shadowcolor0`, deferred lighting does not apply a second gamma-to-linear conversion when sampling it.

Conceptually:

```text
RGB transmittance
=
vec3(unblockedFraction)
+
transparentBlockedFraction * casterTransmissionRGB
```

and is clamped to the physically meaningful [0,1] range.

This preserves colored/translucent shadows while avoiding a 3-texture-read multiplication for every PCF sample.

The approximation does not attempt multilayer transparent accumulation.

## 23. Transparent Shadow Quality Policy

Colored/translucent shadow identity remains enabled at every shadow-quality envelope.

Quality changes:

- PCF sample count,
- map resolution,
- distance,
- entity caster distance.

It does **not** remove colored shadows entirely.

This follows Solar's quality-floor rule: reduce precision before deleting a defining visual capability.

## 24. Celestial Direct-Light ABI

Solar adds:

```text
lib/lighting/celestial.glsl
```

with a logical interface equivalent to:

```glsl
struct SolarCelestialLight {
    vec3 direction;
    vec3 color;
    float intensity;
};
```

The authoritative directional source is:

```glsl
shadowLightPosition
```

which Iris documents in view space and as matching the active shadow source.

`sunAngle` identifies day/night phase.

The light direction is normalized before use.

## 25. Sun/Moon Source Transition

The active celestial source switches between sun and moon around the horizon.

Solar prevents the source switch from producing a visible energy discontinuity by modulating direct intensity with celestial elevation.

The elevation term is derived camera-invariantly in view space by comparing the normalized celestial direction to Iris's view-space world-up vector:

```glsl
dot(normalize(shadowLightPosition), normalize(upPosition))
```

Using `shadowLightPosition.y` directly is forbidden because view-space Y changes with camera orientation. An equivalent player-space transform is acceptable if it is mathematically identical.

Required behavior:

- zenith-like source -> high elevation factor,
- near-horizon source -> low elevation factor,
- source transition occurs while direct contribution is already small.

No atmospheric scattering is implemented in this cycle.

## 26. Provisional Celestial Appearance

The cycle needs an initial rendering baseline but does not claim final artistic calibration.

All numeric appearance constants are centralized.

Starting intent:

### Sun

- neutral-warm at high elevation,
- somewhat warmer near the horizon,
- normalized direct-light scale around 1.0 before weather/shadow terms.

### Moon

- substantially dimmer than sunlight,
- slightly cool,
- never bright enough to turn midnight into blue daytime.

A practical initial moon direct-intensity scale should remain on the order of a small fraction of noon sunlight, approximately 0.08-0.15 before readability/exposure systems.

These values are tunable and require I1 evidence before being described as visually correct.

## 27. Weather Attenuation

Direct celestial energy responds to:

```glsl
rainStrength
thunderStrength
```

Initial engineering targets:

```text
clear             -> 1.00 direct-energy multiplier
full rain         -> approximately 0.55
full thunder      -> approximately 0.25-0.35
```

The function must be smooth and monotonic:

- increasing rain may not increase direct celestial energy,
- increasing thunder may not increase direct celestial energy.

A multiplicative or equivalent monotonic formulation is acceptable if it reaches the approved ranges.

Atmosphere/cloud appearance is outside this cycle.

## 28. Dimension Handling

Solar continues using one shared base shader tree.

No legacy:

- `world0/`,
- `world-1/`,
- `world1/`.

Direct celestial lighting checks the current Iris-exclusive:

```glsl
uniform bool hasSkylight;
```

Behavior:

- `hasSkylight == true`: celestial direct lighting may apply,
- `hasSkylight == false`: no fake sun/moon direct lighting and no shadow sampling in deferred.

Nether-like dimensions therefore do not receive an invented moon.

The End likewise follows its actual dimension skylight property rather than a hardcoded folder assumption.

## 29. Readability Lighting

This cycle does not implement GI.

However, Foundation already stores normalized:

- `skyLight`,
- `blockLight`.

The deferred direct-light stage uses them to preserve gameplay readability until the future indirect/interior lighting cycle exists.

Logical decomposition:

```text
opaque radiance =
    base readability
  + sky readability
  + block-light readability
  + celestial direct lighting
```

All calculations occur in linear light.

## 30. Base Readability Floor

A very small neutral baseline prevents unlit surfaces from becoming mathematically black before indirect lighting exists.

The baseline must remain weak enough that direct-light contrast is still obvious.

The implementation plan should begin with a low single-digit-percent linear-light scale and keep it centralized for later replacement.

This term is an engineering bridge, not a final ambient-light model.

## 31. Sky Readability Approximation

`SurfaceData.skyLight` contributes a cool-neutral readability term.

The response should be nonlinear enough that low sky-light values do not flatten cave contrast.

The exact response curve is an implementation constant/function, but it must:

- map 0 -> no sky contribution,
- map 1 -> bounded readability contribution,
- be monotonic,
- remain significantly lower than direct noon celestial lighting.

The future indirect/atmosphere cycles may replace this approximation.

## 32. Block-Light Approximation

`SurfaceData.blockLight` contributes a warm readability term through:

```glsl
vec3 solarBlockLightApprox(float blockLight);
```

Required behavior:

- block light 0 -> zero contribution,
- block light 1 -> bounded warm contribution,
- monotonic response,
- no material/emissive classification is implied,
- no colored propagation is claimed.

This keeps torches/lamps meaningful without pretending Solar already has a full emissive lighting system.

## 33. Direct-Lighting Equation

For a valid skylit opaque receiver:

```text
NdotL = max(dot(normal, lightDirection), 0)

directRGB =
    celestialColor
  * celestialIntensity
  * weatherAttenuation
  * elevationFactor
  * NdotL
  * shadowTransmittanceRGB
```

Scene albedo from `colortex0` is then lit by the combined readability/direct-light model.

The implementation must preserve the internal linear-light contract.

No gamma-space lighting is permitted.

## 34. Deferred Integration

The existing neutral `deferred` pass becomes the owner of opaque direct lighting.

It reads:

- `colortex0`,
- `colortex1`,
- `depthtex1`,
- current matrix uniforms,
- shadow matrix uniforms,
- shadow buffers,
- celestial/weather/dimension uniforms.

The default flow must avoid diagnostic-only work.

The existing optimization principle remains:

> If a feature is disabled by compile-time configuration, its unnecessary work should compile out where practical.

## 35. Public Configuration Surface

Solar settings grow to include:

- `TARGET_FPS`,
- `SHADOW_QUALITY`,
- `DEBUG_VIEW`.

Logical UI grouping:

```text
Performance:
    TARGET_FPS
    SHADOW_QUALITY

Developer:
    DEBUG_VIEW
```

The implementation plan must use current Iris settings-screen syntax.

No public sliders for:

- map resolution,
- sample count,
- bias,
- entity multiplier,
- filter radius,
- shadow distance

are exposed in this cycle.

Those remain implementation details of `SHADOW_QUALITY`.

## 36. No Global Profiles Yet

This cycle still does not expose whole-shader:

- AUTO,
- PERFORMANCE,
- BALANCED,
- CINEMATIC,
- ULTRA

profiles.

Only one major scalable visual subsystem exists.

Global profile labels become useful only after multiple substantial systems can be tuned together.

## 37. Debug View

Solar adds:

```text
DEBUG_VIEW = 5
```

for shadow diagnostics.

The diagnostic should visualize shadow transmittance/visibility in a way that makes these failures easy to distinguish:

- receiver outside coverage,
- full direct visibility,
- opaque shadow,
- partial/transparent shadow,
- colored transparent transmission.

The exact diagnostic color coding may be chosen during implementation planning, but it must be deterministic and documented.

Debug mode 0 must not pay for debug-only visualization logic.

## 38. Early-Out Requirements

Deferred direct lighting must have explicit early-outs or compile-time branches for:

- invalid/background SurfaceData,
- `hasSkylight == false`,
- `NdotL <= 0`,
- receiver outside effective shadow range,
- shadow path disabled by configuration if a later implementation adds such a compile-time option.

The implementation should avoid shadow texture access when the result cannot affect direct light.

## 39. Static Reference Math

Python reference math is extended to cover:

- shadow distortion,
- shadow-space projection helpers,
- distance fade,
- PCF kernel invariants,
- bias curve properties,
- celestial elevation/source intensity helper properties,
- weather attenuation,
- readability response bounds where practical.

The reference code validates mathematics, not GPU runtime behavior.

## 40. Required Mathematical Properties

Static tests must verify at least:

### Distortion

- origin remains centered,
- finite output for valid clip positions,
- increasing radial magnitude maps monotonically toward the edge,
- write/sample reference equations remain identical.

### Shadow fade

- full shadow influence before 85% range,
- monotonic transition in the 85%-100% interval,
- no shadow influence after 100% range.

### PCF kernel

- exact supported sizes are 4, 6, 8, 12,
- every selected sample is within unit radius,
- each supported prefix is approximately zero-centered,
- deterministic ordering.

### Bias

- finite,
- non-negative,
- grazing receiver bias >= face-on bias for otherwise equal inputs.

### Weather

- rain does not increase direct-light energy,
- thunder does not increase direct-light energy,
- output remains in the intended bounded range.

### Readability

- zero light values produce no corresponding sky/block contribution,
- responses are monotonic,
- outputs remain bounded.

## 41. S0 Validation Extensions

The Solar structural validator learns the lighting/shadow contract.

Complete mode should enforce:

- all six shadow program pairs exist,
- required shadow libraries exist,
- shadow programs do not target `colortex`,
- `shadowcolor0` is the only required shadow-color output,
- `shadowMapResolution` comes from the `SHADOW_QUALITY` envelope,
- `shadowDistance` comes from the `SHADOW_QUALITY` envelope,
- `shadowDistanceRenderMul = 1.0`,
- `shadow.culling=true`,
- `shadowTranslucent=true`,
- manual nearest shadow sampling constants exist,
- no hardware-filtering requirement is introduced,
- no frame-varying shadow jitter source is introduced,
- `hasSkylight` guards celestial shadow sampling,
- transparent-shadow path references `shadowtex0`, `shadowtex1`, and `shadowcolor0`,
- Foundation still uses no `colortex2+`,
- compute/SSBO/custom-image requirements remain absent.

## 42. S1 Validation Extensions

Generic GLSL validation compiles/links:

- `shadow`,
- `shadow_solid`,
- `shadow_cutout`,
- `shadow_water`,
- `shadow_entities`,
- `shadow_block`,
- modified `deferred`,
- existing affected fullscreen/G-buffer programs.

Validator-only preprocessor definitions may be expanded as needed for Iris symbolic constants, but their purpose must remain clearly static-only.

S1 success still does not prove Iris runtime compatibility.

## 43. Evidence Model

The existing evidence levels remain:

| Level | Meaning |
| --- | --- |
| S0 | repository/source architecture and mathematical/static tests |
| S1 | generic GLSL compile/link validation |
| I0 | real Iris/Minecraft discovery, patching, compilation, loading |
| I1 | genuine rendered visuals/stability/performance |

No S0/S1 result may be described as proof that shadows render correctly.

## 44. I0 Runtime Acceptance Criteria

When genuine runtime testing is available, verify on the primary reference:

- shaderpack is discovered,
- shaderpack enables,
- shadow programs compile through Iris,
- deferred lighting compiles,
- Overworld loads,
- Nether loads,
- End loads,
- shader reload succeeds,
- dimension switching succeeds,
- terrain casts shadows,
- cutout foliage casts shaped shadows,
- entities cast shadows,
- block entities cast shadows,
- translucent terrain shadow path does not fail,
- day/night transition does not fail,
- clear/rain/thunder transitions do not fail,
- no-skylight dimensions do not receive fake celestial direct light.

A corresponding smoke test should later run on the secondary compatibility lane.

## 45. I1 Visual Acceptance Criteria

Only genuine rendered output may assess:

- shadow acne,
- Peter Panning,
- aliasing,
- shadow shimmer,
- distortion artifacts,
- near-player shadow detail,
- distance fade quality,
- cutout shadow shape,
- entity shadow quality,
- transparent shadow tint,
- transparent-shadow edge behavior,
- sunrise/sunset source transition,
- moonlight darkness/readability,
- weather direct-light attenuation,
- camera-motion stability,
- gameplay readability.

No visual-quality statement is accepted without rendered evidence.

## 46. Benchmark Scene Set

Initial I1 performance measurements should include at least:

### Open terrain at noon

Measures broad-screen direct-light/shadow sampling.

### Dense forest

Stresses cutout shadow casters and shadow-pass geometry.

### Village/entity-heavy scene

Stresses entity and block-entity shadow rendering.

### Low-angle celestial light

Stresses long projected shadows, distortion, fade, and bias.

### Rain with transparent geometry

Stresses weather attenuation and transparent shadow transmission.

## 47. Benchmark Configurations

For each benchmark scene compare:

```text
Foundation v0
Direct Lighting with shadow lookups disabled / diagnostic baseline where practical
Direct Lighting + Shadows
```

Record:

- commit SHA,
- Minecraft version,
- Iris version,
- Sodium version,
- GPU,
- CPU,
- driver,
- OS,
- resolution,
- render distance,
- VSync,
- FPS cap,
- monitor refresh where known,
- `TARGET_FPS`,
- `SHADOW_QUALITY`,
- average FPS,
- 1% low FPS,
- GPU frame time where measurable,
- CPU frame time where measurable.

The objective is to isolate incremental subsystem cost.

## 48. Performance Budget Rule

This specification does **not** invent a millisecond pass/fail budget before I1 measurements exist.

The project-wide target remains at least 120 FPS at 1080p on the defined mainstream reference class under defined conditions.

At 120 FPS the entire frame interval is 8.33 ms, and Solar does not own all of it.

Therefore:

- PCF tap increases require visible benefit,
- map-resolution increases require visible benefit,
- shadow distance requires visible benefit,
- entity shadow distance requires visible benefit,
- transparent-shadow refinement requires visible benefit.

If a more expensive setting is nearly indistinguishable in I1 evidence, Solar prefers the cheaper setting and preserves budget for later clouds, atmosphere, water, materials, and temporal reconstruction.

## 49. Foundation Documentation Reconciliation

Foundation was merged into `main` at:

```text
b5f7d05fc4f3e3a2024c7a5d75d3c92f33ddf281
```

The current merged `README.md` and `ROADMAP.md` still contain branch-era wording that says Foundation integration is pending.

Implementation of this cycle must correct that stale status.

Required truth after reconciliation:

- Foundation v0 is integrated into `main`,
- Foundation S0/S1 passed,
- Foundation I0/I1 remain pending unless genuine evidence is supplied,
- Direct Lighting + Shadow Foundation is the active/next subsystem cycle as appropriate to implementation status.

This is scoped housekeeping because it establishes the correct baseline for the new milestone.

## 50. Vercel Boundary

The connected Vercel project:

```text
minecraft
```

remains optional future web infrastructure.

This cycle must not:

- deploy the shaderpack to Vercel,
- use a Vercel preview as shader evidence,
- add benchmark dashboards,
- add web documentation merely because Vercel is connected.

Existing automatic Git/Vercel preview activity is incidental and has no S0/S1/I0/I1 meaning for Minecraft rendering.

## 51. Known Risks

### 51.1 Shadow distortion artifacts

Single-map radial distortion can create uneven projected geometry behavior and large distorted shadow shapes.

Mitigation:

- deterministic shared distortion function,
- conservative initial parameters,
- I1 evaluation at low sun angles,
- no escalation to huge map sizes before evidence.

### 51.2 Bias tuning

Too little bias causes acne; too much causes Peter Panning.

Mitigation:

- dedicated bias module,
- slope/distance-aware structure,
- static monotonicity tests,
- I1 screenshots at representative angles/distances.

### 51.3 Transparent shadow approximation

One representative `shadowcolor0` sample cannot represent multiple colored transparent blockers inside a PCF footprint.

Mitigation:

- treat this as an explicit approximation,
- preserve RGB transmittance ABI,
- avoid multiplying color-sample cost per PCF tap,
- revisit only if I1 evidence shows the limitation is visually important.

### 51.4 No-skylight shadow-pass overhead

Deferred sampling can early-out on `hasSkylight`, but Iris may still execute shadow-pass geometry in dimensions where celestial lighting is not used.

Mitigation:

- accept during this cycle,
- measure if I1 profiling becomes available,
- introduce dimension-specific program routing only if the recovered cost justifies the architectural complexity.

### 51.5 Readability term mistaken for GI

The temporary sky/block readability approximation is intentionally not indirect lighting.

Mitigation:

- keep functions explicitly named as approximations,
- document their replacement boundary,
- do not advertise GI or physically propagated lighting.

### 51.6 Static validation false confidence

Generic GLSL cannot reproduce the Iris patch/runtime environment.

Mitigation:

- preserve S0/S1/I0/I1 terminology,
- keep CI wording constrained,
- require real runtime evidence for visual/performance claims.

## 52. Deliberate Deferrals

The following need their own later architectural design:

- physically based sky/sun spectral model,
- atmosphere-derived sunlight,
- GI/SSGI,
- voxel lighting,
- emissive materials,
- contact shadows,
- PCSS,
- temporal shadow denoising/reuse,
- shadow cache systems,
- cascaded shadow maps,
- dynamic runtime AutoTune controller,
- dimension-specific shadow-pass suppression,
- global quality profiles.

## 53. Decisions Locked by This Spec

Unless superseded by a later approved design:

- direct opaque lighting lives in `deferred`,
- Solar uses a single distorted shadow-map family,
- default shadow quality is Cinematic / 2,
- the quality table in Section 10 defines the initial envelopes,
- shadow-map resolution remains at 2048 for Balanced and Cinematic,
- Ultra alone uses 4096,
- manual deterministic PCF is used,
- approved PCF counts are 4/6/8/12,
- no temporal shadow jitter exists,
- nearest raw shadow buffers are used,
- hardware shadow filtering is not required,
- `shadowtex0`, `shadowtex1`, and `shadowcolor0` define transparent-shadow inputs,
- colored shadow output is RGB transmittance,
- transparent color sampling is conditional rather than per-PCF-tap,
- `shadowLightPosition` is the authoritative direct/shadow direction,
- `hasSkylight` gates celestial direct-light sampling,
- one shared base shader tree remains,
- no `worldN` folders are introduced,
- weather attenuates direct celestial energy,
- sky/block readability approximations are temporary and centralized,
- no extra full-resolution Solar color target is introduced,
- no compute/SSBO/custom-image dependency is introduced,
- `DEBUG_VIEW=5` is reserved for shadow diagnostics,
- global whole-pack quality profiles remain deferred,
- Foundation documentation status is reconciled during implementation,
- Vercel remains outside shader runtime validation.

## 54. External Technical References

Current Iris documentation was consulted through Context7 using:

```text
/irisshaders/docs
```

and cross-checked in the current `IrisShaders/docs` repository.

Relevant documentation areas include:

- shadow programs,
- shadow buffers,
- `shadowtex0` / `shadowtex1`,
- `shadowcolor0`,
- shadow filtering constants,
- `shadowMapResolution`,
- `shadowDistance`,
- `shadowDistanceRenderMul`,
- `entityShadowDistanceMul`,
- `shadow.culling`,
- `shadowTranslucent`,
- shadow/world coordinate spaces,
- `shadowLightPosition`,
- `sunAngle`,
- `rainStrength`,
- `thunderStrength`,
- dimension/skylight uniforms,
- current shader-settings behavior.

These references are dated 2026-09-29 and must be rechecked before version-sensitive implementation if the target ecosystem changes.

---

This specification defines architecture only.

Approval of this written specification permits the next Superpowers action: writing the detailed implementation plan.

It does **not** permit shader implementation before that plan is reviewed and an execution method is approved.
