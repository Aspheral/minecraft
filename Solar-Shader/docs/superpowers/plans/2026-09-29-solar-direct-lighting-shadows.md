# Solar Direct Lighting + Shadow Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Solar's first visual rendering subsystem: camera-stable celestial direct lighting with a distorted single-map shadow pass, deterministic manual PCF, transparent/colored shadow transmission, readability lighting, quality envelopes, diagnostics, and static validation.

**Architecture:** Six thin Iris shadow-program pairs feed Iris-owned `shadowtex0`, `shadowtex1`, and `shadowcolor0`. Shared shadow libraries own distortion, receiver transforms, bias, filtering, and RGB transmittance. Opaque lighting runs in the existing deferred pass using Foundation `SurfaceData` and depth reconstruction, while `DEBUG_VIEW=5` visualizes the already-computed shadow result in deferred so composite never duplicates shadow work.

**Tech Stack:** GLSL 330 compatibility, Iris shaderpack conventions, Fabric, Python 3.12 standard library, GitHub Actions on `ubuntu-24.04`, Khronos glslang 16.5.0.

**Spec:** `Solar-Shader/docs/superpowers/specs/2026-09-29-solar-direct-lighting-shadows-design.md`

**Plan status:** Written for user review. No implementation begins until this plan is approved and an execution method is selected.

## Global Constraints

- Repository: `Aspheral/minecraft`.
- Project root: `Solar-Shader/`.
- Implementation branch: `feat/solar-direct-lighting-shadows`.
- Baseline: `main` at `b5f7d05fc4f3e3a2024c7a5d75d3c92f33ddf281`.
- Primary runtime reference: Minecraft Java 26.3 + Fabric + Iris 1.11.6 + Sodium 0.9.2.
- Secondary compatibility lane: Minecraft Java 1.21.11 + Fabric + Iris 1.10.x.
- GLSL baseline: `#version 330 compatibility`.
- Foundation `colortex0` and `colortex1` ownership must not change.
- No `colortex2+`, compute shader, SSBO, or custom-image dependency.
- No legacy `world0/`, `world-1/`, or `world1/`.
- Direct opaque lighting belongs in `deferred`.
- Six explicit shadow programs: `shadow`, `shadow_solid`, `shadow_cutout`, `shadow_water`, `shadow_entities`, `shadow_block`.
- Shadow pass writes Iris shadow buffers only; no Solar `RENDERTARGETS` directive in shadow fragments.
- `shadowcolor0.rgb` stores linear-light caster color; alpha stores source caster alpha.
- `SHADOW_QUALITY=2` is default.
- Quality envelopes:
  - 0: 1024 map, 96-block distance, 4 taps, entity multiplier 0.50.
  - 1: 2048 map, 128-block distance, 6 taps, entity multiplier 0.70.
  - 2: 2048 map, 160-block distance, 8 taps, entity multiplier 0.85.
  - 3: 4096 map, 192-block distance, 12 taps, entity multiplier 1.00.
- `shadowDistanceRenderMul = 1.0`.
- `shadow.culling=true`.
- `shadowTranslucent=true`.
- `shadowtex0Nearest`, `shadowtex1Nearest`, and `shadowcolor0Nearest` are true.
- Manual deterministic PCF only; no hardware shadow filtering requirement.
- No temporal/random shadow jitter.
- Shadow fade is full through 85% of effective range and smoothly fades to unshadowed by 100%.
- `shadowLightPosition` is the authoritative celestial/shadow direction.
- Celestial elevation must be camera-invariant using `dot(normalize(shadowLightPosition), normalize(upPosition))` or an exactly equivalent player-space calculation.
- Direct celestial lighting is disabled when `hasSkylight == false`.
- Weather attenuation targets: clear 1.0, full rain approximately 0.55, full thunder approximately 0.25-0.35.
- Initial moon direct intensity is approximately 0.10 of the normalized sun scale.
- Readability lighting is explicitly approximate, not GI.
- `DEBUG_VIEW=5` is shadow transmittance/visibility diagnostics.
- `solarGetQuality().shadows` remains deterministic at 1.0 in this cycle.
- No global whole-pack profiles yet.
- S0/S1 remain static evidence only; I0/I1 require genuine Minecraft + Iris runtime evidence.
- Vercel remains outside shader runtime architecture and validation. Do not deploy for this milestone.
- TDD uses intentional RED commits followed by GREEN commits. GitHub Actions is the executable test environment for chat-only development.

## Review Focus

1. **Camera orientation:** celestial intensity must not change merely because the player looks up/down; tests must pin elevation to `shadowLightPosition · upPosition`, never view-space Y alone.
2. **Write/sample distortion parity:** the shadow-pass vertex transform and deferred receiver transform must use one shared distortion equation; tests must detect a duplicated or divergent formula.
3. **Transparent footprint/color miss:** if PCF sees transparent blocking but the representative `shadowcolor0` sample is clear, the result must use neutral transmission rather than arbitrary clear-buffer tint.
4. **No-skylight dimensions:** `hasSkylight == false` must bypass celestial direct light and shadow texture sampling in deferred while leaving readability lighting usable.
5. **Default-path cost:** `DEBUG_VIEW=0` must perform one shadow calculation path only; `DEBUG_VIEW=5` reuses deferred shadow results and composite must not resample shadow maps.

---

## Planned File Map

### Reference math and tests

- Modify: `Solar-Shader/tools/solar_reference.py`
- Modify: `Solar-Shader/tools/tests/test_solar_reference.py`
- Modify: `Solar-Shader/tools/solar_validate.py`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

### Configuration

- Modify: `Solar-Shader/shaders/lib/config.glsl`
- Modify: `Solar-Shader/shaders/shaders.properties`
- Create: `Solar-Shader/shaders/lib/shadow/settings.glsl`

### Shadow libraries

- Create: `Solar-Shader/shaders/lib/shadow/transform.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/bias.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/sampling.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/filtering.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/shadow_vertex.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/shadow_fragment.glsl`

### Shadow entry points

Create `.vsh` and `.fsh` for:

- `shadow`
- `shadow_solid`
- `shadow_cutout`
- `shadow_water`
- `shadow_entities`
- `shadow_block`

### Lighting libraries and deferred integration

- Create: `Solar-Shader/shaders/lib/lighting/celestial.glsl`
- Create: `Solar-Shader/shaders/lib/lighting/readability.glsl`
- Create: `Solar-Shader/shaders/lib/lighting/direct.glsl`
- Modify: `Solar-Shader/shaders/lib/programs/deferred_fragment.glsl`
- Modify: `Solar-Shader/shaders/lib/programs/composite_fragment.glsl`
- Modify: `Solar-Shader/shaders/lib/debug/debug_view.glsl`

### Evidence/documentation

- Create: `Solar-Shader/benchmarks/direct-lighting-shadows-runtime-template.md`
- Modify: `Solar-Shader/README.md`
- Modify: `Solar-Shader/ROADMAP.md`
- Modify: `Solar-Shader/CHANGELOG.md`

---

### Task 1: Extend CPU Reference Math for Shadows and Lighting

**Files:**
- Modify: `Solar-Shader/tools/solar_reference.py`
- Modify: `Solar-Shader/tools/tests/test_solar_reference.py`

**Interfaces:**
- Produces:
  - `shadow_distort_clip(position: Vec3) -> Vec3`
  - `shadow_distance_fade(distance: float, shadow_distance: float) -> float`
  - `shadow_kernel(taps: int) -> tuple[tuple[float, float], ...]`
  - `shadow_bias(ndotl: float, receiver_distance: float, shadow_distance: float, distortion_metric: float) -> float`
  - `weather_attenuation(rain_strength: float, thunder_strength: float) -> float`
  - `celestial_elevation(light_direction: Vec3, up_direction: Vec3) -> float`
  - `is_daylight(sun_angle: float) -> bool`
  - `sky_readability(sky_light: float) -> Vec3`
  - `block_readability(block_light: float) -> Vec3`

- [ ] **Step 1: Add failing reference tests**

Add tests with these exact behaviors:

```python
def test_shadow_distortion_keeps_origin_centered(): ...
def test_shadow_distortion_is_finite_and_radially_monotonic(): ...
def test_shadow_fade_is_full_through_85_percent_and_zero_at_range(): ...
def test_shadow_fade_is_monotonic_in_fade_region(): ...
def test_shadow_kernel_supports_only_4_6_8_12(): ...
def test_every_shadow_kernel_prefix_is_symmetric_and_zero_centered(): ...
def test_shadow_bias_is_finite_nonnegative_and_grazing_is_not_lower(): ...
def test_weather_clear_rain_and_thunder_targets(): ...
def test_weather_attenuation_is_monotonic(): ...
def test_celestial_elevation_is_camera_basis_invariant(): ...
def test_daylight_ranges_match_iris_sun_angle_semantics(): ...
def test_readability_zero_and_monotonic_bounds(): ...
```

Pin the deterministic 12-sample kernel in this order:

```text
(-0.35,  0.00)
( 0.35,  0.00)
( 0.00, -0.35)
( 0.00,  0.35)
(-0.25, -0.25)
( 0.25,  0.25)
(-0.25,  0.25)
( 0.25, -0.25)
(-0.70,  0.00)
( 0.70,  0.00)
( 0.00, -0.70)
( 0.00,  0.70)
```

Approved prefixes: 4, 6, 8, 12.

Commit RED checkpoint:

```text
test: define Solar shadow and lighting reference math
```

- [ ] **Step 2: Verify the RED checkpoint in GitHub Actions**

Expected: new reference tests fail because the new functions are absent.

- [ ] **Step 3: Implement reference helpers**

Use the spec's distortion:

```text
factor = length(xy) + 0.1
xy /= factor
z *= 0.5
```

`shadow_distance_fade` returns shadow influence:
- 1.0 at/below 0.85 × range,
- smoothstep-style transition,
- 0.0 at/above range.

Initial bias equation, centralized for parity with GLSL:

```text
distanceNorm = clamp(receiver_distance / max(shadow_distance, epsilon), 0, 1)
slope        = (1 - clamp(ndotl, 0, 1))^2

bias =
    0.00025
  + 0.00125 * slope
  + 0.00025 * distanceNorm
  + 0.00025 * clamp(distortion_metric, 0, 1)
```

Weather equation:

```text
rainFactor    = 1 - 0.45 * clamp(rain, 0, 1)
thunderFactor = 1 - 0.45454545 * clamp(thunder, 0, 1)
attenuation   = rainFactor * thunderFactor
```

This yields approximately 0.55 at full rain and 0.30 at full rain + full thunder.

`celestial_elevation`:
- normalize both vectors,
- dot light with up,
- clamp to [0,1],
- return smoothstep(0.02, 0.20, elevation).

`is_daylight` follows current Iris `sunAngle` semantics:
- sunrise 0,
- noon 0.25,
- sunset 0.5,
- midnight 0.75,
- day when `0 <= sunAngle < 0.5`,
- night otherwise.

Readability reference:
- base readability is tested later in GLSL, not returned here.
- sky: `0.14 * pow(sky, 1.6) * (0.70, 0.82, 1.00)`.
- block: `0.22 * pow(block, 1.35) * (1.00, 0.55, 0.22)`.

- [ ] **Step 4: Commit GREEN implementation**

```text
test: add Solar shadow and lighting reference math
```

- [ ] **Step 5: Verify CI green**

Expected: Foundation tests remain green and new reference tests pass.

---

### Task 2: Establish Shadow Configuration and Quality Envelopes

**Files:**
- Modify: `Solar-Shader/shaders/lib/config.glsl`
- Modify: `Solar-Shader/shaders/shaders.properties`
- Create: `Solar-Shader/shaders/lib/shadow/settings.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- `config.glsl` adds:
  - `#define SHADOW_QUALITY 2 // [0 1 2 3]`
  - `DEBUG_VIEW` range becomes `[0 1 2 3 4 5]`.
- `settings.glsl` exposes compile-time:
  - `shadowMapResolution`
  - `shadowDistance`
  - `shadowDistanceRenderMul`
  - `entityShadowDistanceMul`
  - `SOLAR_SHADOW_TAPS`
  - nearest-filter constants.

- [ ] **Step 1: Add failing configuration tests**

Tests assert:

- default `SHADOW_QUALITY 2`,
- exact allowed values [0 1 2 3],
- DEBUG_VIEW includes 5,
- `screen=TARGET_FPS SHADOW_QUALITY DEBUG_VIEW`,
- `sliders=TARGET_FPS` only,
- `shadow.culling=true`,
- `shadowTranslucent=true`,
- no hardware shadow filtering requirement,
- exact quality table in `settings.glsl`,
- `shadowDistanceRenderMul = 1.0`,
- all three nearest constants are true.

Commit RED checkpoint:

```text
test: define Solar shadow configuration envelope
```

- [ ] **Step 2: Verify CI fails on missing settings**

- [ ] **Step 3: Implement config and settings**

Exact mapping:

```text
quality 0 -> 1024, 96.0, 4 taps, 0.50 entity
quality 1 -> 2048, 128.0, 6 taps, 0.70 entity
quality 2 -> 2048, 160.0, 8 taps, 0.85 entity
quality 3 -> 4096, 192.0, 12 taps, 1.00 entity
```

Use preprocessor branches on `SHADOW_QUALITY`; do not expose separate public map-resolution/tap/bias controls.

- [ ] **Step 4: Commit GREEN implementation**

```text
feat: add Solar shadow quality envelopes
```

- [ ] **Step 5: Verify CI green**

---

### Task 3: Implement Shared Shadow Math Libraries

**Files:**
- Create: `Solar-Shader/shaders/lib/shadow/transform.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/bias.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/sampling.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Produces:
  - `vec3 solarDistortShadowClip(vec3 shadowClipPosition)`
  - `float solarShadowDistortionMetric(vec2 undistortedClipXY)`
  - `vec4 solarViewToDistortedShadowClip(vec3 viewPosition, mat4 gbufferModelViewInverse, mat4 shadowModelView, mat4 shadowProjection)`
  - `vec3 solarShadowClipToScreen(vec4 shadowClipPosition)`
  - `float solarShadowDistanceFade(float receiverDistance, float effectiveDistance)`
  - `float solarShadowBias(vec3 normal, vec3 lightDirection, float receiverDistance, float effectiveDistance, float distortionMetric)`
  - `vec2 solarShadowKernelOffset(int index)`

- [ ] **Step 1: Add failing source-contract tests**

Tests assert:

- distortion formula occurs only in `transform.glsl`,
- no duplicate `length(...xy) + 0.1` shadow distortion appears elsewhere,
- no GPU `inverse()`,
- bias constants match Task 1 reference,
- the 12 GLSL offsets match Task 1 exactly,
- allowed tap counts are 4/6/8/12,
- no random/frameCounter/noise-based kernel rotation.

Commit RED:

```text
test: define Solar shared shadow math contract
```

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement transform, bias, and sampling**

Use CPU-precomputed Iris inverse matrices only.

`solarShadowDistortionMetric` returns:

```text
clamp((length(undistortedClipXY) + 0.1) / 1.5, 0, 1)
```

so farther/less-dense regions receive at least as much compensation as the center.

`solarShadowClipToScreen` performs perspective divide and maps NDC to [0,1].

`solarShadowDistanceFade` uses horizontal player-space distance as specified.

- [ ] **Step 4: Commit GREEN**

```text
feat: add Solar shadow transforms bias and kernel
```

- [ ] **Step 5: Verify CI green**

---

### Task 4: Add Explicit Iris Shadow Programs

**Files:**
- Create: `Solar-Shader/shaders/lib/shadow/shadow_vertex.glsl`
- Create: `Solar-Shader/shaders/lib/shadow/shadow_fragment.glsl`
- Create program pairs:
  - `Solar-Shader/shaders/shadow.vsh/.fsh`
  - `Solar-Shader/shaders/shadow_solid.vsh/.fsh`
  - `Solar-Shader/shaders/shadow_cutout.vsh/.fsh`
  - `Solar-Shader/shaders/shadow_water.vsh/.fsh`
  - `Solar-Shader/shaders/shadow_entities.vsh/.fsh`
  - `Solar-Shader/shaders/shadow_block.vsh/.fsh`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Every wrapper starts with `#version 330 compatibility`, defines one `SOLAR_SHADOW_PROGRAM_*` role, and includes one shared stage implementation.
- Shared vertex:
  - obtains ordinary shadow clip position with `ftransform()`,
  - applies `solarDistortShadowClip` exactly once,
  - passes atlas UV and vertex color as needed.
- Shared fragment writes only location 0 / `shadowcolor0`.
- No shadow fragment contains a Solar `RENDERTARGETS` directive.

- [ ] **Step 1: Add failing shadow-program tests**

Assert:

- all 12 files exist,
- wrappers remain <=12 non-empty/non-comment lines,
- no `RENDERTARGETS` in shadow fragments,
- shared vertex includes `transform.glsl` and calls `solarDistortShadowClip`,
- solid role does not require a texture lookup,
- cutout role samples `gtexture`, applies alpha discard, and writes opaque alpha after surviving,
- water/base/entity/block roles preserve source alpha,
- every textured role converts RGB through `solarToLinearApprox` before shadowcolor write.

Commit RED:

```text
test: define Solar Iris shadow program contract
```

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement shared shadow vertex**

Use the same distortion library deferred will later consume.

- [ ] **Step 4: Implement shared shadow fragment**

Role behavior:

- solid: fixed opaque shadow color `vec4(0.0, 0.0, 0.0, 1.0)`, no texture sample.
- cutout: sample `gtexture * glcolor`, discard below `alphaTestRef`, write linear RGB with alpha 1.0.
- base/water/entities/block: sample `gtexture * glcolor`, discard effectively invisible fragments, write linear RGB + source alpha.

- [ ] **Step 5: Commit GREEN**

```text
feat: add Solar Iris shadow pass programs
```

- [ ] **Step 6: Verify S1 compiles and links all six new program pairs**

---

### Task 5: Add Celestial and Readability Lighting Without Shadow Sampling

**Files:**
- Create: `Solar-Shader/shaders/lib/lighting/celestial.glsl`
- Create: `Solar-Shader/shaders/lib/lighting/readability.glsl`
- Create: `Solar-Shader/shaders/lib/lighting/direct.glsl`
- Modify: `Solar-Shader/shaders/lib/programs/deferred_fragment.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Produces:
  - `struct SolarCelestialLight { vec3 direction; vec3 color; float intensity; };`
  - `float solarWeatherAttenuation(float rainStrength, float thunderStrength)`
  - `float solarCelestialElevation(vec3 lightDirection, vec3 upDirection)`
  - `SolarCelestialLight solarGetCelestialLight(vec3 shadowLightPosition, vec3 upPosition, float sunAngle, float rainStrength, float thunderStrength, bool hasSkylight)`
  - `vec3 solarSkyReadability(float skyLight)`
  - `vec3 solarBlockLightApprox(float blockLight)`
  - `vec3 solarReadabilityLight(SurfaceData surface)`
  - `vec3 solarDirectUnshadowed(SurfaceData surface, SolarCelestialLight light)`

- [ ] **Step 1: Add failing lighting ABI tests**

Tests assert:

- no use of `shadowLightPosition.y` as elevation,
- `upPosition` is declared and used,
- `hasSkylight` can zero celestial intensity,
- weather constants match Task 1,
- sunAngle day/night split matches current Iris semantics,
- exact provisional constants are centralized:
  - noon sun color `vec3(1.00, 0.92, 0.80)`,
  - horizon sun color `vec3(1.00, 0.58, 0.32)`,
  - moon color `vec3(0.28, 0.38, 0.62)`,
  - moon intensity `0.10`,
  - base readability `vec3(0.025)`,
  - sky formula matches Task 1,
  - block formula matches Task 1.
- deferred reads/decode SurfaceData and preserves linear-light math.
- deferred has no shadow texture sampler yet in this task.

Commit RED:

```text
test: define Solar direct-lighting ABI
```

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement celestial/readability libraries**

Sun color blends horizon -> noon by elevation factor.

Moon uses fixed cool color/intensity multiplied by the same elevation and weather terms.

- [ ] **Step 4: Integrate unshadowed direct light into deferred**

Deferred behavior:

```text
scene albedo
×
(readability RGB + unshadowed celestial direct RGB)
```

for valid surfaces.

Background/invalid surfaces pass scene color through.

No gamma-space lighting.

- [ ] **Step 5: Commit GREEN**

```text
feat: add Solar celestial and readability lighting
```

- [ ] **Step 6: Verify CI green**

This task intentionally creates a measurable future benchmark midpoint: direct lighting before shadow lookup cost.

---

### Task 6: Add Manual PCF, RGB Transmittance, Shadowed Deferred Lighting, and DEBUG_VIEW 5

**Files:**
- Create: `Solar-Shader/shaders/lib/shadow/filtering.glsl`
- Modify: `Solar-Shader/shaders/lib/lighting/direct.glsl`
- Modify: `Solar-Shader/shaders/lib/programs/deferred_fragment.glsl`
- Modify: `Solar-Shader/shaders/lib/programs/composite_fragment.glsl`
- Modify: `Solar-Shader/shaders/lib/debug/debug_view.glsl`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Produces:
  - `vec3 solarShadowTransmittance(vec3 shadowScreenPosition, float receiverDistance, float filterRadiusTexels)`
  - `vec3 solarDirectShadowed(SurfaceData surface, SolarCelestialLight light, vec3 shadowTransmittance)`
  - `vec3 solarDebugShadowTransmittance(vec3 transmittance)`

- [ ] **Step 1: Add failing filtering/integration tests**

Tests assert:

- `shadowtex0` and `shadowtex1` are sampled exactly inside `filtering.glsl`,
- `shadowcolor0` is conditional on transparent blocked fraction,
- color is not sampled once per PCF tap,
- transparent blocked fraction is `max(opaqueVisibility - allVisibility, 0)`,
- opaque blocked fraction is `1 - opaqueVisibility`,
- representative color with near-zero alpha triggers neutral fallback,
- transmittance clamps to [0,1],
- receiver outside shadow range skips texture sampling,
- `hasSkylight == false` skips shadow sampling,
- `NdotL <= 0` skips shadow sampling,
- DEBUG_VIEW 5 is produced in deferred,
- composite DEBUG_VIEW 5 only passes `colortex0` through,
- composite contains no shadow samplers,
- DEBUG_VIEW 0 has one shadow calculation path, not a duplicate diagnostic path.

Commit RED:

```text
test: define Solar filtered shadow integration
```

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement PCF filtering**

For each selected tap:
- offset = ordered kernel prefix,
- convert radius from texels using `1.0 / shadowMapResolution`,
- compare receiver biased depth against `shadowtex0`,
- compare receiver biased depth against `shadowtex1`,
- average all/opaque visibility.

Do not use hardware comparison samplers.

- [ ] **Step 4: Implement transparent RGB transmission**

If transparent fraction > epsilon:
- sample representative central `shadowcolor0`,
- if alpha > epsilon, use `color.rgb * (1 - alpha)`,
- otherwise use neutral scalar transmission `vec3(1 - alphaFallback)` derived from the transparent blocked fraction, never clear-buffer RGB.

Conceptual final:

```text
transmittance =
    vec3(unblockedFraction)
  + transparentBlockedFraction * casterTransmissionRGB
```

clamped to [0,1].

- [ ] **Step 5: Integrate receiver transform, bias, fade, and early-outs in deferred**

Required uniform path:

- `depthtex1`,
- `gbufferProjectionInverse`,
- `gbufferModelViewInverse`,
- `shadowModelView`,
- `shadowProjection`,
- `shadowLightPosition`,
- `upPosition`,
- `sunAngle`,
- `rainStrength`,
- `thunderStrength`,
- `hasSkylight`.

Apply distance fade by mixing shadow transmittance toward vec3(1) as fade influence approaches zero.

- [ ] **Step 6: Implement DEBUG_VIEW 5 without duplicate shadow work**

In deferred:
- when DEBUG_VIEW == 5, output computed RGB transmittance for valid receivers,
- output black for invalid/no-skylight receivers.

In composite:
- DEBUG_VIEW == 5 simply returns `colortex0`.
- no shadow texture/matrix uniforms are added to composite.

- [ ] **Step 7: Commit GREEN**

```text
feat: add Solar filtered colored shadows
```

- [ ] **Step 8: Verify CI green and S1 links affected programs**

---

### Task 7: Extend Complete S0/S1 Validation for the Shadow Architecture

**Files:**
- Modify: `Solar-Shader/tools/solar_validate.py`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Adds manifest groups:
  - `SHADOW_PROGRAMS`
  - `SHADOW_LIBRARIES`
- Complete validation understands shadow programs separately from Foundation `RENDERTARGETS` programs.

- [ ] **Step 1: Add failing complete-validation tests**

Required tests:

```python
def test_complete_mode_requires_all_shadow_program_pairs(): ...
def test_complete_mode_requires_shadow_and_lighting_libraries(): ...
def test_shadow_programs_must_not_declare_rendertargets(): ...
def test_shadow_settings_match_quality_envelope(): ...
def test_shadow_properties_require_culling_and_translucent_pass(): ...
def test_shadow_path_requires_manual_nearest_filtering(): ...
def test_shadow_path_rejects_hardware_filtering_requirement(): ...
def test_shadow_path_rejects_frame_varying_jitter(): ...
def test_deferred_has_skylight_guard_precedes_shadow_sampling(): ...
def test_complete_mode_still_rejects_colortex_two_or_higher(): ...
```

Commit RED:

```text
test: define complete Solar shadow validation
```

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement complete validator rules**

Do not weaken any Foundation checks.

S1 continues using pinned glslang 16.5.0 and automatically compiles the six new root program pairs.

- [ ] **Step 4: Commit GREEN**

```text
ci: enforce Solar direct-lighting shadow architecture
```

- [ ] **Step 5: Verify exact workflow summary**

Expected:
- Python tests PASS,
- S0 PASS,
- S1 PASS,
- glslang 16.5.0,
- static-only disclaimer remains,
- no I0/I1 claim.

---

### Task 8: Reconcile Milestone Documentation and Add Runtime Evidence Template

**Files:**
- Create: `Solar-Shader/benchmarks/direct-lighting-shadows-runtime-template.md`
- Modify: `Solar-Shader/README.md`
- Modify: `Solar-Shader/ROADMAP.md`
- Modify: `Solar-Shader/CHANGELOG.md`
- Modify: `Solar-Shader/tools/tests/test_solar_validate.py`

**Interfaces:**
- Documentation distinguishes implemented/static evidence from pending runtime evidence.
- Runtime template is blank evidence structure, never fabricated benchmark data.

- [ ] **Step 1: Add failing documentation tests**

Tests require:

- README says Foundation v0 is integrated into `main` at `b5f7d05`,
- README links the new lighting/shadow spec and plan,
- roadmap no longer says Foundation integration is pending,
- roadmap separates Direct Lighting + Shadow Foundation from later indirect/interior/emissive lighting,
- changelog records only implemented/static-validated facts,
- runtime template contains no invented FPS or hardware values.

Commit RED:

```text
test: define Solar lighting shadow evidence documentation
```

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Create runtime evidence template**

Required fields:

```text
Date
Commit SHA
Evidence level (I0 or I1)
Minecraft version
Fabric Loader version
Iris version
Sodium version
GPU
GPU driver
CPU
RAM
OS
Resolution
Render distance
FPS cap
VSync
Monitor refresh
TARGET_FPS
SHADOW_QUALITY
DEBUG_VIEW
Scene class
Seed / coordinates / camera description
Shaderpack discovery result
Shaderpack enable result
Compile error result
Shader reload result
Overworld result
Nether result
End result
Dimension switching result
Terrain shadow result
Cutout shadow result
Entity shadow result
Block-entity shadow result
Transparent/water shadow result
Day/night transition result
Rain/thunder transition result
Shadow acne notes
Peter Panning notes
Shimmer notes
Distance fade notes
Transparent tint notes
Average FPS (I1 only)
1% low FPS (I1 only)
GPU frame time where measurable
CPU frame time where measurable
Foundation baseline measurement
Direct-light-only measurement
Direct-light+shadow measurement
Screenshots/log references
Notes
```

- [ ] **Step 4: Reconcile README/ROADMAP/CHANGELOG**

Truthful state after implementation:
- Foundation integrated in main,
- current branch contains Direct Lighting + Shadow source,
- S0/S1 status only if workflow is green,
- I0/I1 pending unless genuine evidence exists,
- next lighting cycle is indirect/interior/emissive lighting.

- [ ] **Step 5: Commit GREEN**

```text
docs: record Solar direct-lighting shadow status
```

- [ ] **Step 6: Verify CI green**

---

### Task 9: Whole-Branch Verification and Review Handoff

**Files:**
- Verify only unless a regression is found.
- Any defect receives a RED regression test before a fix.

**Interfaces:**
- Consumes all prior task outputs.
- Produces a review-ready branch; does not merge automatically.

- [ ] **Step 1: Compare feature branch against `main`**

Verify:
- only Solar files plus existing shared CI file changed,
- no Vercel deployment/config was added,
- no GI/AO/PCSS/TAA/volumetric/compute scope slipped in,
- no `colortex2+`,
- no `worldN` folders.

- [ ] **Step 2: Map every spec requirement to branch evidence**

Spec sections 1-54 must map to:
- source,
- test,
- documentation,
- or explicit I0/I1 pending status.

- [ ] **Step 3: Inspect exact-head GitHub Actions**

Require:
- all Python tests pass,
- complete S0 pass,
- S1 pass,
- glslang 16.5.0,
- evidence disclaimer intact.

- [ ] **Step 4: Fresh source review**

Review at minimum:
- distortion equation single ownership,
- shadow pass/deferred transform parity,
- light/up dot camera invariance,
- day/night sunAngle logic,
- weather attenuation,
- bias monotonicity,
- PCF prefix symmetry,
- shadowtex0/1 comparison semantics,
- transparent color fallback,
- linear `shadowcolor0` contract,
- no-skylight early-out,
- DEBUG_VIEW 0/5 cost behavior,
- readability not mislabeled as GI.

- [ ] **Step 5: If a defect is found, add a failing regression first**

Commit RED, confirm workflow failure, implement narrow fix, confirm GREEN, then restart Task 9 from Step 1.

- [ ] **Step 6: Record review-ready status**

Do not merge automatically.

Branch is ready for:
1. whole-branch review,
2. optional genuine I0/I1 runtime evidence,
3. PR creation only through the finishing workflow.

---

## Execution Notes

### Chat-only TDD

During implementation:

- GitHub is canonical state.
- GitHub Actions is the executable static test environment.
- Each task uses RED then GREEN commits where the plan specifies.
- Do not ask the user to manually edit or run local files merely to continue source engineering.

### Iris Runtime Boundary

Context7/current Iris docs confirm the implementation assumptions used by this plan, including:
- six shadow-program names/fallback behavior,
- `shadowtex0` / `shadowtex1`,
- `shadowcolor0`,
- `shadowMapResolution`,
- `shadowDistance`,
- `shadowDistanceRenderMul`,
- `entityShadowDistanceMul`,
- `shadowLightPosition`,
- `upPosition`,
- `sunAngle`,
- `rainStrength`,
- `thunderStrength`,
- `hasSkylight`.

Generic glslang remains S1 only. Iris is required for I0.

### Vercel Boundary

The connected Vercel `minecraft` project remains present but unused by this plan.

Do not:
- deploy Solar to Vercel,
- treat automatic preview checks as shader evidence,
- add a web benchmark dashboard in this cycle.

### Completion Wording

Without genuine Minecraft evidence:

```text
Direct Lighting + Shadow source and S0/S1 static validation complete.
Minecraft/Iris runtime validation (I0/I1) pending.
```

Do not claim:
- shadows render correctly,
- cinematic quality,
- driver compatibility,
- 120 FPS.
